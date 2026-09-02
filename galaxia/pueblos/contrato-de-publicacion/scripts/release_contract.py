#!/usr/bin/env python3
"""Contrato puro para autorizar una publicación y validar su recibo."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from collections.abc import Callable
from typing import Any
from urllib.parse import urlsplit


READY_GATES: tuple[str, ...] = (
    "scope_confirmed",
    "candidate_verified",
    "read_only_preflight_passed",
    "backup_verified",
    "rollback_verified",
    "authorization_verified",
    "exact_target_verified",
    "target_identity_verified",
)
REQUIRED_EFFECT = "publish_release"


@dataclass(frozen=True)
class ReleaseManifest:
    scope_id: str
    source_origin: str
    revision: str
    sealed_at: str
    builder_receipt_id: str
    checks: tuple[str, ...]


@dataclass(frozen=True)
class PublishTarget:
    scope_id: str
    origin: str
    server_identity: str
    backup_id: str
    rollback_id: str


@dataclass(frozen=True)
class EffectGrant:
    grant_id: str
    scope_id: str
    effect: str
    target_origin: str
    revision: str
    issued_at: str
    expires_at: str
    single_use: bool


@dataclass(frozen=True)
class PublicationReceipt:
    receipt_id: str
    grant_id: str
    scope_id: str
    target_origin: str
    revision: str
    applied_at: str
    postcondition_verified: bool


@dataclass(frozen=True)
class Violation:
    code: str
    detail: str = ""


@dataclass
class ContractReport:
    violations: list[Violation] = field(default_factory=list)
    grant_consumed: bool = False
    receipt_recorded: bool = False

    @property
    def ok(self) -> bool:
        return not self.violations


def _blank(value: str | None) -> bool:
    return not isinstance(value, str) or not value.strip()


def _exact_revision(value: str) -> bool:
    return (
        isinstance(value, str)
        and len(value) in (40, 64)
        and all(char in "0123456789abcdef" for char in value)
    )


def _origin(value: str) -> bool:
    if _blank(value) or value != value.strip() or "\\" in value:
        return False
    try:
        parsed = urlsplit(value)
        hostname = parsed.hostname
        parsed.port
    except ValueError:
        return False
    return bool(
        parsed.scheme in {"http", "https"}
        and hostname
        and not any(char.isspace() or ord(char) < 32 for char in hostname)
        and parsed.username is None
        and parsed.password is None
        and parsed.path in {"", "/"}
        and not parsed.query
        and not parsed.fragment
    )


def _parse(value: str) -> datetime | None:
    if _blank(value):
        return None
    text = value.strip()
    if text.endswith(("Z", "z")):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(timezone.utc)


def _static_report(
    manifest: ReleaseManifest,
    target: PublishTarget,
    grant: EffectGrant,
) -> ContractReport:
    """Valida bindings y sellos que deben ser ciertos en ready y receipt."""

    report = ContractReport()
    add = report.violations.append
    if any(
        _blank(value)
        for value in (
            manifest.scope_id,
            manifest.source_origin,
            manifest.sealed_at,
            manifest.builder_receipt_id,
        )
    ):
        add(Violation("manifest_not_sealed"))
    if not _exact_revision(manifest.revision):
        add(Violation("revision_not_exact"))
    if not _origin(manifest.source_origin):
        add(Violation("source_origin_invalid"))
    if not manifest.checks or any(_blank(check) for check in manifest.checks):
        add(Violation("candidate_checks_missing"))

    if manifest.scope_id != target.scope_id:
        add(Violation("scope_mismatch"))
    if not _origin(target.origin):
        add(Violation("target_origin_invalid"))
    if _blank(target.server_identity):
        add(Violation("target_identity_missing"))
    if _blank(target.backup_id):
        add(Violation("backup_missing"))
    if _blank(target.rollback_id):
        add(Violation("rollback_missing"))

    if _blank(grant.grant_id):
        add(Violation("grant_missing"))
    if grant.scope_id != manifest.scope_id or grant.scope_id != target.scope_id:
        add(Violation("grant_scope_mismatch"))
    if grant.effect != REQUIRED_EFFECT:
        add(Violation("grant_effect_mismatch"))
    if grant.target_origin != target.origin:
        add(Violation("grant_target_mismatch"))
    if grant.revision != manifest.revision:
        add(Violation("grant_revision_mismatch"))
    if grant.single_use is not True:
        add(Violation("grant_not_single_use"))

    sealed = _parse(manifest.sealed_at)
    issued = _parse(grant.issued_at)
    expires = _parse(grant.expires_at)
    if None in (sealed, issued, expires):
        add(Violation("invalid_timestamp"))
    else:
        assert sealed is not None and issued is not None and expires is not None
        if sealed > issued:
            add(Violation("grant_precedes_release_seal"))
        if expires <= issued:
            add(Violation("grant_window_invalid"))
    return report


def validate_ready(
    manifest: ReleaseManifest,
    target: PublishTarget,
    grant: EffectGrant,
    *,
    now: str,
    gates_passed: frozenset[str],
) -> ContractReport:
    """Valida todo antes del efecto y acumula todas las violaciones."""

    report = _static_report(manifest, target, grant)
    add = report.violations.append

    moment = _parse(now)
    issued = _parse(grant.issued_at)
    expires = _parse(grant.expires_at)
    if moment is None:
        add(Violation("now_invalid"))
    elif issued is not None and expires is not None and not issued <= moment <= expires:
        add(Violation("grant_not_current"))

    for gate in READY_GATES:
        if gate not in gates_passed:
            add(Violation("gate_missing", gate))
    return report


def validate_receipt(
    manifest: ReleaseManifest,
    target: PublishTarget,
    grant: EffectGrant,
    receipt: PublicationReceipt,
) -> ContractReport:
    """Comprueba que el recibo corresponde exactamente al efecto autorizado."""

    report = _static_report(manifest, target, grant)
    add = report.violations.append
    if _blank(receipt.receipt_id):
        add(Violation("receipt_missing"))
    if receipt.grant_id != grant.grant_id:
        add(Violation("receipt_grant_mismatch"))
    if receipt.scope_id != manifest.scope_id or receipt.scope_id != target.scope_id:
        add(Violation("receipt_scope_mismatch"))
    if receipt.target_origin != target.origin:
        add(Violation("receipt_target_mismatch"))
    if receipt.revision != manifest.revision:
        add(Violation("receipt_revision_mismatch"))
    applied = _parse(receipt.applied_at)
    issued = _parse(grant.issued_at)
    expires = _parse(grant.expires_at)
    if None in (applied, issued, expires):
        add(Violation("receipt_timestamp_invalid"))
    else:
        assert applied is not None and issued is not None and expires is not None
        if not issued <= applied <= expires:
            add(Violation("receipt_outside_grant_window"))
    if receipt.postcondition_verified is not True:
        add(Violation("postcondition_not_verified"))
    return report


def execution_allowed(report: ContractReport, *, blockers: tuple[str, ...] = ()) -> bool:
    """Fail-closed: solo un consumo atómico limpio autoriza el efecto."""

    return report.ok and report.grant_consumed is True and not blockers


def _grant_marker(store: Path, grant: EffectGrant, suffix: str) -> Path:
    payload = "\0".join(
        (grant.grant_id, grant.scope_id, grant.effect, grant.target_origin, grant.revision)
    ).encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()
    return Path(store) / f"{digest}.{suffix}"


def _prepare_store(store: Path) -> Path:
    directory = Path(store)
    if directory.is_symlink():
        raise OSError("el almacén de grants no puede ser symlink")
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    if not directory.is_dir():
        raise OSError("el almacén de grants no es un directorio")
    try:
        directory.chmod(0o700)
    except OSError:
        pass
    return directory


def _create_marker(path: Path) -> bool:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    try:
        descriptor = os.open(path, flags, 0o600)
    except FileExistsError:
        return False
    try:
        os.write(descriptor, b"recorded\n")
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    try:
        directory_descriptor = os.open(path.parent, os.O_RDONLY)
    except OSError:
        return True
    try:
        os.fsync(directory_descriptor)
    except OSError:
        pass
    finally:
        os.close(directory_descriptor)
    return True


def consume_grant(
    manifest: ReleaseManifest,
    target: PublishTarget,
    grant: EffectGrant,
    *,
    gates_passed: frozenset[str],
    store: Path,
    clock: Callable[[], datetime] | None = None,
) -> ContractReport:
    """Valida y consume el grant atómicamente antes del efecto externo."""

    try:
        moment = (clock or (lambda: datetime.now(timezone.utc)))()
        if not isinstance(moment, datetime) or moment.tzinfo is None or moment.utcoffset() is None:
            raise ValueError("reloj sin zona")
        trusted_now = moment.astimezone(timezone.utc).isoformat()
    except Exception:
        return ContractReport(violations=[Violation("trusted_clock_invalid")])
    report = validate_ready(
        manifest,
        target,
        grant,
        now=trusted_now,
        gates_passed=gates_passed,
    )
    if not report.ok:
        return report
    try:
        marker = _grant_marker(_prepare_store(store), grant, "consumed")
        if not _create_marker(marker):
            report.violations.append(Violation("grant_already_consumed"))
        else:
            report.grant_consumed = True
    except OSError:
        report.violations.append(Violation("grant_store_unavailable"))
    return report


def finalize_receipt(
    manifest: ReleaseManifest,
    target: PublishTarget,
    grant: EffectGrant,
    receipt: PublicationReceipt,
    *,
    store: Path,
) -> ContractReport:
    """Vincula un único recibo a un grant consumido; un segundo cierre falla."""

    report = validate_receipt(manifest, target, grant, receipt)
    try:
        directory = _prepare_store(store)
        consumed = _grant_marker(directory, grant, "consumed")
        if not consumed.is_file() or consumed.is_symlink():
            report.violations.append(Violation("grant_not_consumed"))
            return report
        report.grant_consumed = True
        if report.ok:
            marker = _grant_marker(directory, grant, "receipt")
            if not _create_marker(marker):
                report.violations.append(Violation("receipt_already_recorded"))
            else:
                report.receipt_recorded = True
    except OSError:
        report.violations.append(Violation("grant_store_unavailable"))
    return report


def _tuple(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ValueError("se esperaba una lista")
    if any(not isinstance(item, str) for item in value):
        raise ValueError("la lista solo admite strings")
    return tuple(value)


def _require_bool(value: Any, field: str) -> bool:
    if type(value) is not bool:
        raise ValueError(f"{field} debe ser booleano JSON")
    return value


def _require_str(value: Any, field: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} debe ser string")
    return value


def _require_object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field} debe ser objeto")
    return value


def _objects(data: dict[str, Any]) -> tuple[ReleaseManifest, PublishTarget, EffectGrant]:
    manifest_data = _require_object(data["manifest"], "manifest")
    target_data = _require_object(data["target"], "target")
    grant_data = _require_object(data["grant"], "grant")
    manifest = ReleaseManifest(
        scope_id=_require_str(manifest_data["scope_id"], "manifest.scope_id"),
        source_origin=_require_str(
            manifest_data["source_origin"], "manifest.source_origin"
        ),
        revision=_require_str(manifest_data["revision"], "manifest.revision"),
        sealed_at=_require_str(manifest_data["sealed_at"], "manifest.sealed_at"),
        builder_receipt_id=_require_str(
            manifest_data["builder_receipt_id"], "manifest.builder_receipt_id"
        ),
        checks=_tuple(manifest_data["checks"]),
    )
    target = PublishTarget(
        scope_id=_require_str(target_data["scope_id"], "target.scope_id"),
        origin=_require_str(target_data["origin"], "target.origin"),
        server_identity=_require_str(
            target_data["server_identity"], "target.server_identity"
        ),
        backup_id=_require_str(target_data["backup_id"], "target.backup_id"),
        rollback_id=_require_str(target_data["rollback_id"], "target.rollback_id"),
    )
    grant = EffectGrant(
        grant_id=_require_str(grant_data["grant_id"], "grant.grant_id"),
        scope_id=_require_str(grant_data["scope_id"], "grant.scope_id"),
        effect=_require_str(grant_data["effect"], "grant.effect"),
        target_origin=_require_str(
            grant_data["target_origin"], "grant.target_origin"
        ),
        revision=_require_str(grant_data["revision"], "grant.revision"),
        issued_at=_require_str(grant_data["issued_at"], "grant.issued_at"),
        expires_at=_require_str(grant_data["expires_at"], "grant.expires_at"),
        single_use=_require_bool(grant_data["single_use"], "grant.single_use"),
    )
    return manifest, target, grant


def _load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("el contrato debe ser un objeto JSON")
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("ready", "consume", "receipt"))
    parser.add_argument("path", type=Path)
    parser.add_argument("--grant-store", type=Path)
    args = parser.parse_args(argv)

    data = _load(args.path)
    manifest, target, grant = _objects(data)
    if args.mode in {"ready", "consume"}:
        gates_passed = frozenset(_tuple(data["gates_passed"]))
        if args.mode == "consume":
            if args.grant_store is None:
                parser.error("consume exige --grant-store")
            report = consume_grant(
                manifest,
                target,
                grant,
                store=args.grant_store,
                gates_passed=gates_passed,
            )
        else:
            report = validate_ready(
                manifest,
                target,
                grant,
                now=_require_str(data["now"], "now"),
                gates_passed=gates_passed,
            )
    else:
        if args.grant_store is None:
            parser.error("receipt exige --grant-store")
        receipt_data = data["receipt"]
        receipt_data = _require_object(receipt_data, "receipt")
        receipt = PublicationReceipt(
            receipt_id=_require_str(receipt_data["receipt_id"], "receipt.receipt_id"),
            grant_id=_require_str(receipt_data["grant_id"], "receipt.grant_id"),
            scope_id=_require_str(receipt_data["scope_id"], "receipt.scope_id"),
            target_origin=_require_str(
                receipt_data["target_origin"], "receipt.target_origin"
            ),
            revision=_require_str(receipt_data["revision"], "receipt.revision"),
            applied_at=_require_str(receipt_data["applied_at"], "receipt.applied_at"),
            postcondition_verified=_require_bool(
                receipt_data["postcondition_verified"],
                "receipt.postcondition_verified",
            ),
        )
        report = finalize_receipt(
            manifest,
            target,
            grant,
            receipt,
            store=args.grant_store,
        )

    print(json.dumps(asdict(report), ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
