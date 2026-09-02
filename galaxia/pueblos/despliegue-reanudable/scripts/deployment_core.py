#!/usr/bin/env python3
"""Núcleo genérico y sin red para pipelines reanudables por fases."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class GateKind(str, Enum):
    IRREVERSIBLE_DECISION = "irreversible_decision"
    EXTERNAL_ACTION = "external_action"


class ManualGate(RuntimeError):
    """Indica que una fase necesita una decisión o acción humana fuera del runner."""

    def __init__(self, kind: GateKind, detail: str):
        super().__init__(f"{kind.value}: {detail}")
        self.kind = kind
        self.detail = detail


class ProbeFailure(RuntimeError):
    """El probe no pudo medir; una fase mutante no debe ejecutarse a ciegas."""


@dataclass
class Context:
    scope_id: str
    values: dict[str, Any] = field(default_factory=dict)


RunFn = Callable[[Context], None]
ProbeFn = Callable[[Context], bool]


@dataclass
class Phase:
    name: str
    run: RunFn
    deps: tuple[str, ...] = ()
    probe: ProbeFn | None = None
    mutates: bool = True
    idempotent: bool = False
    retryable: bool = False
    max_attempts: int = 1
    gate: GateKind | None = None
    contract_version: str = "1"


_PHASE_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")


@dataclass(frozen=True)
class GraphIssue:
    code: str
    phase: str
    detail: str = ""


@dataclass
class GraphReport:
    order: tuple[str, ...] = ()
    issues: list[GraphIssue] = field(default_factory=list)
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None and not self.issues


def _phase_map(phases: Iterable[Phase]) -> dict[str, Phase]:
    by_name: dict[str, Phase] = {}
    for phase in phases:
        if not isinstance(phase, Phase):
            raise ValueError("el plan contiene una fase de tipo inválido")
        if not isinstance(phase.name, str) or not _PHASE_NAME.fullmatch(phase.name):
            raise ValueError("nombre de fase inválido")
        if phase.name in by_name:
            raise ValueError("nombre de fase duplicado")
        if not isinstance(phase.deps, tuple) or any(
            not isinstance(dep, str) or not _PHASE_NAME.fullmatch(dep)
            for dep in phase.deps
        ):
            raise ValueError("dependencias de fase inválidas")
        if not callable(phase.run) or (phase.probe is not None and not callable(phase.probe)):
            raise ValueError("run o probe de fase inválido")
        if any(type(value) is not bool for value in (phase.mutates, phase.idempotent, phase.retryable)):
            raise ValueError("flags de fase no booleanos")
        if type(phase.max_attempts) is not int:
            raise ValueError("max_attempts no es entero")
        if phase.gate is not None and not isinstance(phase.gate, GateKind):
            raise ValueError("gate de fase inválido")
        if not isinstance(phase.contract_version, str) or not _PHASE_NAME.fullmatch(
            phase.contract_version
        ):
            raise ValueError("contract_version de fase inválida")
        by_name[phase.name] = phase
    return by_name


def topological_order(phases: Iterable[Phase]) -> tuple[str, ...]:
    """Orden topológico estable; falla ante ciclos o dependencias inexistentes."""

    by_name = _phase_map(phases)
    for phase in by_name.values():
        unknown = sorted(set(phase.deps) - set(by_name))
        if unknown:
            raise ValueError(f"{phase.name}: dependencias inexistentes {unknown}")

    pending = {name: set(phase.deps) for name, phase in by_name.items()}
    order: list[str] = []
    while pending:
        ready = sorted(name for name, deps in pending.items() if not deps)
        if not ready:
            raise ValueError(f"ciclo entre fases {sorted(pending)}")
        for name in ready:
            order.append(name)
            pending.pop(name)
        for deps in pending.values():
            deps.difference_update(ready)
    return tuple(order)


def inspect_graph(phases: Iterable[Phase]) -> GraphReport:
    """Valida el DAG como datos, sin ejecutar runs, probes, red ni I/O externo."""

    rows = list(phases)
    try:
        by_name = _phase_map(rows)
        order = topological_order(rows)
    except ValueError as exc:
        return GraphReport(error=str(exc))

    report = GraphReport(order=order)
    for name in order:
        phase = by_name[name]
        add = report.issues.append
        if phase.mutates and phase.probe is None:
            add(GraphIssue("mutating_phase_without_probe", name))
        if phase.gate is not None and phase.probe is None:
            add(GraphIssue("gate_without_probe", name))
        if phase.retryable and not phase.idempotent:
            add(GraphIssue("retry_without_idempotency", name))
        if phase.retryable and phase.probe is None:
            add(GraphIssue("retry_without_probe", name))
        if phase.retryable and phase.max_attempts < 2:
            add(GraphIssue("retry_without_multiple_attempts", name))
        if not phase.retryable and phase.max_attempts != 1:
            add(GraphIssue("attempts_on_non_retryable_phase", name))
    return report


_SENSITIVE_NAME = (
    r"(?:pass(?:word)?|passwd|token|secret|client[_-]?secret|api[_-]?key|"
    r"access[_-]?key(?:[_-]?id)?|private[_-]?key|cookie|authorization)"
)
_SENSITIVE_KEY = re.compile(rf"(?:^|[_-]){_SENSITIVE_NAME}(?:$|[_-])", re.IGNORECASE)
_CAMEL_SENSITIVE_KEY = re.compile(
    r"(?:password|passwd|token|secret|apiKey|privateKey|accessKeyId)\Z",
    re.IGNORECASE,
)
_ASSIGNMENT = re.compile(
    rf"(?i)(\b(?:[a-z0-9]+[_-])*{_SENSITIVE_NAME}\b[\"']?\s*[:=]\s*)"
    r"(?:\"[^\"]*\"|'[^']*'|[^\s,;]+)"
)
_CAMEL_ASSIGNMENT = re.compile(
    r"(?i)(\b[a-z0-9]*(?:password|passwd|token|secret|apiKey|privateKey|accessKeyId)"
    r"\b[\"']?\s*[:=]\s*)(?:\"[^\"]*\"|'[^']*'|[^\s,;]+)"
)
_FLAG = re.compile(
    r"(?i)(--[a-z0-9_-]*(?:pass|token|secret|key|cookie)[a-z0-9_-]*[=\s]+)"
    r"(?:\"[^\"]*\"|'[^']*'|\S+)"
)
_URI_CREDENTIALS = re.compile(
    r"(?i)\b([a-z][a-z0-9+.-]{1,20}://)([^/\s@]+)@"
)
_AUTHORIZATION = re.compile(
    r"(?i)(\bauthorization\s*[:=]\s*)(?:bearer|basic)\s+[^\s,;]+"
)
_COMMON_SECRET = re.compile(
    r"(?:github_pat_[A-Za-z0-9_]{40,}|gh[pousr]_[A-Za-z0-9]{30,}|"
    r"sk-(?:proj-)?[A-Za-z0-9_-]{30,}|sk-ant-[A-Za-z0-9_-]{30,}|"
    r"AKIA[0-9A-Z]{16}|xox[baprs]-[0-9A-Za-z-]{10,})"
)


def redact(value: Any) -> Any:
    """Redacta datos sensibles antes de logs o estado sin mostrar el valor original."""

    if isinstance(value, dict):
        return {
            str(key): "[REDACTED]"
            if _SENSITIVE_KEY.search(str(key)) or _CAMEL_SENSITIVE_KEY.search(str(key))
            else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple, set)):
        return [redact(item) for item in value]
    if isinstance(value, str):
        safe = _URI_CREDENTIALS.sub(r"\1[REDACTED]@", value)
        safe = _AUTHORIZATION.sub(r"\1[REDACTED]", safe)
        safe = _FLAG.sub(r"\1[REDACTED]", safe)
        safe = _ASSIGNMENT.sub(r"\1[REDACTED]", safe)
        safe = _CAMEL_ASSIGNMENT.sub(r"\1[REDACTED]", safe)
        return _COMMON_SECRET.sub("[REDACTED]", safe)
    return value


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class StateLedger:
    """Ledger atómico de observabilidad; nunca sustituye al probe."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.data = self._load()

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"version": 1, "phases": {}}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or not isinstance(data.get("phases"), dict):
                raise ValueError("estructura inválida")
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
            return {"version": 1, "phases": {}, "recovered_invalid_ledger": True}
        for row in data["phases"].values():
            if isinstance(row, dict) and row.get("status") == "running":
                row.update(
                    status="interrupted",
                    error="ejecución anterior interrumpida",
                    ended_at=_utc_now(),
                )
        return data

    def status(self, name: str) -> str | None:
        row = self.data.get("phases", {}).get(name, {})
        return row.get("status") if isinstance(row, dict) else None

    def row(self, name: str) -> dict[str, Any]:
        row = self.data.get("phases", {}).get(name, {})
        return dict(row) if isinstance(row, dict) else {}

    def bind_scope(self, scope_id: str) -> None:
        fingerprint = hashlib.sha256(scope_id.encode("utf-8")).hexdigest()
        current = self.data.get("scope_fingerprint")
        if current not in (None, fingerprint):
            raise RuntimeError("el ledger pertenece a otro scope")
        if current is None:
            self.data["scope_fingerprint"] = fingerprint
            self._write()

    def set(self, name: str, *, replace: bool = False, **fields: Any) -> None:
        safe_fields = redact(fields)
        phases = self.data.setdefault("phases", {})
        if replace:
            phases[name] = safe_fields
        else:
            phases.setdefault(name, {}).update(safe_fields)
        self._write()

    def _write(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_name(f".{self.path.name}.tmp")
        payload = json.dumps(self.data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        with temporary.open("w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, self.path)


class ScopeLock:
    """Lock advisory atómico por scope; no impone un límite global."""

    def __init__(self, directory: Path, scope_id: str):
        digest = hashlib.sha256(scope_id.encode("utf-8")).hexdigest()[:20]
        self.path = Path(directory) / f".{digest}.lock"
        self.handle: Any = None
        self.backend = ""

    def __enter__(self) -> ScopeLock:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = self.path.open("a+", encoding="utf-8")
        try:
            if os.name == "posix":
                import fcntl

                fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                self.backend = "posix"
            elif os.name == "nt":
                import msvcrt

                self.handle.seek(0)
                if not self.handle.read(1):
                    self.handle.write("0")
                    self.handle.flush()
                self.handle.seek(0)
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
                self.backend = "windows"
            else:
                raise RuntimeError("plataforma sin backend de lock soportado")
        except (BlockingIOError, OSError) as exc:
            self.handle.close()
            self.handle = None
            raise RuntimeError("ya existe una ejecución activa para este scope") from exc
        except Exception:
            self.handle.close()
            self.handle = None
            raise
        self.handle.seek(0)
        self.handle.truncate()
        self.handle.write(str(os.getpid()))
        self.handle.flush()
        os.fsync(self.handle.fileno())
        return self

    def __exit__(self, *_args: Any) -> None:
        if self.handle is None:
            return
        try:
            if self.backend == "posix":
                import fcntl

                fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
            elif self.backend == "windows":
                import msvcrt

                self.handle.seek(0)
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)
        finally:
            self.handle.close()
            self.handle = None


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    detail: str = ""


@dataclass
class PreflightResult:
    checks: list[Check] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return bool(self.checks) and all(check.ok is True for check in self.checks)

    @property
    def failed(self) -> tuple[Check, ...]:
        return tuple(check for check in self.checks if not check.ok)


def run_preflight(checks: Iterable[Callable[[], Check]]) -> PreflightResult:
    """Ejecuta todos los checks read-only y convierte excepciones en fallos redactados."""

    result = PreflightResult()
    for index, check_fn in enumerate(checks, start=1):
        try:
            check = check_fn()
            if not isinstance(check, Check):
                raise TypeError("el check no devolvió Check")
            if type(check.ok) is not bool:
                raise TypeError("check.ok debe ser bool")
            if not isinstance(check.name, str) or not _PHASE_NAME.fullmatch(check.name):
                raise TypeError("check.name inválido")
            result.checks.append(Check(check.name, check.ok, str(redact(check.detail))))
        except Exception as exc:  # noqa: BLE001 - backstop deliberado de preflight
            result.checks.append(Check(f"check-{index}", False, str(redact(str(exc)))))
    return result


@dataclass
class RunResult:
    done: list[str] = field(default_factory=list)
    already_done: list[str] = field(default_factory=list)
    needs_human: list[tuple[str, GateKind, str]] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    reconcile_required: list[str] = field(default_factory=list)
    blocked: list[str] = field(default_factory=list)
    timings: dict[str, float] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return (
            not self.needs_human
            and not self.failed
            and not self.reconcile_required
            and not self.blocked
        )


def _phase_fingerprint(phase: Phase) -> str:
    payload = json.dumps(
        {
            "name": phase.name,
            "deps": phase.deps,
            "mutates": phase.mutates,
            "idempotent": phase.idempotent,
            "retryable": phase.retryable,
            "max_attempts": phase.max_attempts,
            "gate": phase.gate.value if phase.gate else None,
            "contract_version": phase.contract_version,
        },
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _safety_fields(prior: dict[str, Any]) -> dict[str, Any]:
    """Conserva incertidumbre y gates aunque cambie el estado observado del DAG."""

    fields: dict[str, Any] = {}
    if prior.get("attempted") is True:
        fields["attempted"] = True
    if prior.get("gate_pending") is True or prior.get("status") == "needs_human":
        fields["gate_pending"] = True
        for key in ("gate", "gate_detail", "phase_fingerprint"):
            if key in prior:
                fields[key] = prior[key]
    return fields


class Scheduler:
    def __init__(
        self,
        phases: Iterable[Phase],
        context: Context,
        ledger: StateLedger,
        *,
        log: Callable[[str], None] = print,
        sleeper: Callable[[float], None] = time.sleep,
    ):
        self.rows = list(phases)
        self.by_name = _phase_map(self.rows)
        self.context = context
        self.ledger = ledger
        self.log = log
        self.sleeper = sleeper

    def _emit(self, phase: str, message: str) -> None:
        self.log(f"{phase}: {redact(message)}")

    def _probe(self, phase: Phase) -> tuple[bool, float]:
        if phase.probe is None:
            return False, 0.0
        started = time.monotonic()
        try:
            measured = phase.probe(self.context)
            if type(measured) is not bool:
                raise TypeError("el probe debe devolver bool")
            return measured, round(time.monotonic() - started, 4)
        except Exception as exc:  # noqa: BLE001 - frontera de medición
            raise ProbeFailure(f"probe no concluyente: {redact(str(exc))}") from exc

    def _execute(self, phase: Phase) -> None:
        attempts = phase.max_attempts if phase.retryable else 1
        last_error: Exception | None = None
        for attempt in range(1, attempts + 1):
            try:
                phase.run(self.context)
                if phase.probe is not None:
                    postcondition, _elapsed = self._probe(phase)
                    if not postcondition:
                        raise RuntimeError("la postcondición no quedó verificada")
                return
            except ManualGate:
                raise
            except ProbeFailure:
                raise
            except Exception as exc:  # noqa: BLE001 - se persiste de forma redactada
                last_error = exc
                if not phase.retryable or attempt == attempts:
                    raise
                delay = min(2 ** (attempt - 1), 8)
                self._emit(phase.name, f"intento {attempt} falló; reintento en {delay}s: {exc}")
                self.sleeper(delay)
        if last_error is not None:
            raise last_error

    def run(self) -> RunResult:
        report = inspect_graph(self.rows)
        if not report.ok:
            details = report.error or ", ".join(issue.code for issue in report.issues)
            raise ValueError(f"plan inválido: {details}")

        result = RunResult()
        outcome: dict[str, str] = {}
        for name in report.order:
            phase = self.by_name[name]
            prior = self.ledger.row(name)
            broken = [dep for dep in phase.deps if outcome.get(dep) != "done"]
            if broken:
                outcome[name] = "blocked"
                result.blocked.append(name)
                prior = self.ledger.row(name)
                if (
                    phase.gate is not None
                    and (
                        prior.get("gate_pending") is True
                        or prior.get("status") == "needs_human"
                    )
                    and prior.get("phase_fingerprint") == _phase_fingerprint(phase)
                ):
                    self.ledger.set(
                        name,
                        replace=True,
                        status="blocked",
                        temporarily_blocked_by=broken,
                        **_safety_fields(prior),
                    )
                else:
                    self.ledger.set(
                        name,
                        replace=True,
                        status="blocked",
                        blocked_by=broken,
                        **_safety_fields(prior),
                    )
                self._emit(name, f"bloqueada por dependencias: {broken}")
                continue

            try:
                present, probe_seconds = self._probe(phase)
            except ProbeFailure as exc:
                outcome[name] = "failed"
                result.failed.append(name)
                self.ledger.set(
                    name,
                    replace=True,
                    status="failed",
                    error=str(exc),
                    ended_at=_utc_now(),
                    **_safety_fields(prior),
                )
                self._emit(name, str(exc))
                continue
            if present:
                outcome[name] = "done"
                result.already_done.append(name)
                self.ledger.set(
                    name,
                    replace=True,
                    status="done",
                    source="probe",
                    probe_seconds=probe_seconds,
                    ended_at=_utc_now(),
                )
                self._emit(name, "postcondición ya presente")
                continue

            if (
                phase.gate is not None
                and (
                    prior.get("gate_pending") is True
                    or prior.get("status") == "needs_human"
                )
                and prior.get("phase_fingerprint") == _phase_fingerprint(phase)
            ):
                detail = str(prior.get("gate_detail") or prior.get("error") or "gate pendiente")
                outcome[name] = "needs_human"
                result.needs_human.append((name, phase.gate, detail))
                self.ledger.set(name, status="needs_human", temporarily_blocked_by=[])
                self._emit(name, "el gate declarado sigue pendiente")
                continue

            if (
                phase.mutates
                and not phase.idempotent
                and (
                    prior.get("attempted") is True
                    or self.ledger.data.get("recovered_invalid_ledger") is True
                )
            ):
                outcome[name] = "reconcile_required"
                result.reconcile_required.append(name)
                self.ledger.set(
                    name,
                    status="reconcile_required",
                    error="fase no idempotente incierta; reconciliar el destino con el probe",
                    ended_at=_utc_now(),
                )
                self._emit(name, "requiere reconciliación antes de otro intento")
                continue

            self.ledger.set(
                name,
                replace=True,
                status="running",
                attempted=True,
                started_at=_utc_now(),
            )
            started = time.monotonic()
            try:
                self._execute(phase)
            except ManualGate as gate:
                duration = round(time.monotonic() - started, 4)
                if phase.gate != gate.kind:
                    outcome[name] = "failed"
                    result.failed.append(name)
                    self.ledger.set(
                        name,
                        status="failed",
                        error="gate ejecutado sin declaración coincidente en el plan",
                        duration_seconds=duration,
                        ended_at=_utc_now(),
                    )
                    self._emit(name, "gate no declarado o de tipo distinto")
                    continue
                outcome[name] = "needs_human"
                result.needs_human.append((name, gate.kind, str(redact(gate.detail))))
                self.ledger.set(
                    name,
                    status="needs_human",
                    gate=gate.kind.value,
                    error=gate.detail,
                    gate_detail=gate.detail,
                    gate_pending=True,
                    phase_fingerprint=_phase_fingerprint(phase),
                    duration_seconds=duration,
                    ended_at=_utc_now(),
                )
                self._emit(name, f"requiere intervención: {gate.kind.value}")
            except Exception as exc:  # noqa: BLE001 - frontera de una fase
                duration = round(time.monotonic() - started, 4)
                outcome[name] = "failed"
                result.failed.append(name)
                result.timings[name] = duration
                self.ledger.set(
                    name,
                    status="failed",
                    error=str(exc),
                    duration_seconds=duration,
                    ended_at=_utc_now(),
                )
                self._emit(name, f"falló: {exc}")
            else:
                duration = round(time.monotonic() - started, 4)
                outcome[name] = "done"
                result.done.append(name)
                result.timings[name] = duration
                self.ledger.set(
                    name,
                    status="done",
                    source="execution",
                    duration_seconds=duration,
                    ended_at=_utc_now(),
                )
                self._emit(name, "postcondición verificada")
        return result


def run_pipeline(
    phases: Iterable[Phase],
    context: Context,
    state_path: Path,
    *,
    log: Callable[[str], None] = print,
    sleeper: Callable[[float], None] = time.sleep,
) -> RunResult:
    """Ejecuta bajo lock de scope y guarda solo estado redactado."""

    state_path = Path(state_path)
    if not context.scope_id.strip():
        raise ValueError("scope_id no puede estar vacío")
    state_key = f"state:{state_path.resolve(strict=False)}"
    with ScopeLock(state_path.parent, f"scope:{context.scope_id}"), ScopeLock(
        state_path.parent,
        state_key,
    ):
        ledger = StateLedger(state_path)
        ledger.bind_scope(context.scope_id)
        return Scheduler(
            phases,
            context,
            ledger,
            log=log,
            sleeper=sleeper,
        ).run()


def _phase_from_json(row: dict[str, Any]) -> Phase:
    if not isinstance(row, dict):
        raise ValueError("cada fase debe ser un objeto")
    gate_value = row.get("gate")
    if gate_value is not None and not isinstance(gate_value, str):
        raise ValueError("gate debe ser string")
    gate = GateKind(gate_value) if gate_value else None
    has_probe = _json_bool(row.get("has_probe", False), "has_probe")
    return Phase(
        name=_json_str(row.get("name", ""), "name"),
        run=lambda _context: None,
        deps=_json_string_tuple(row.get("deps", []), "deps"),
        probe=(lambda _context: False) if has_probe else None,
        mutates=_json_bool(row.get("mutates", True), "mutates"),
        idempotent=_json_bool(row.get("idempotent", False), "idempotent"),
        retryable=_json_bool(row.get("retryable", False), "retryable"),
        max_attempts=_json_int(row.get("max_attempts", 1), "max_attempts"),
        gate=gate,
        contract_version=_json_str(
            row.get("contract_version", "1"),
            "contract_version",
        ),
    )


def _json_str(value: Any, field: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} debe ser string")
    return value


def _json_bool(value: Any, field: str) -> bool:
    if type(value) is not bool:
        raise ValueError(f"{field} debe ser booleano JSON")
    return value


def _json_int(value: Any, field: str) -> int:
    if type(value) is not int:
        raise ValueError(f"{field} debe ser entero JSON")
    return value


def _json_string_tuple(value: Any, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(f"{field} debe ser una lista de strings")
    return tuple(value)


def _plan(path: Path, as_json: bool) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("phases"), list):
        raise ValueError("el plan debe contener una lista phases")
    report = inspect_graph(_phase_from_json(row) for row in data["phases"])
    if as_json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2, sort_keys=True))
    else:
        if report.error:
            print(f"PLAN INVÁLIDO: {report.error}")
        else:
            print("Orden: " + " -> ".join(report.order))
            for issue in report.issues:
                print(f"ERROR {issue.phase}: {issue.code} {issue.detail}".rstrip())
            if not report.issues:
                print("Plan válido")
    return 0 if report.ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    plan_parser = subparsers.add_parser("plan", help="valida un DAG JSON sin ejecutar nada")
    plan_parser.add_argument("path", type=Path)
    plan_parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "plan":
        return _plan(args.path, args.json)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
