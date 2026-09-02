#!/usr/bin/env python3
"""Validador puro de manifiestos de evidencia ligados a una release."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlsplit


@dataclass(frozen=True)
class EvidenceItem:
    item_id: str
    scope_id: str
    kind: str
    origin: str
    collected_at: str
    sha256: str
    path: str
    draft: bool = False
    requires_attestation: bool = False


@dataclass(frozen=True)
class EvidenceManifest:
    scope_id: str
    release_fingerprint: str
    declared_origins: tuple[str, ...]
    required_kinds: tuple[str, ...]
    items: tuple[EvidenceItem, ...]
    attestation_id: str | None = None
    attestation_actor_id: str | None = None


@dataclass(frozen=True)
class Violation:
    code: str
    item_id: str = ""
    detail: str = ""


@dataclass
class EvidenceReport:
    violations: list[Violation] = field(default_factory=list)
    report_kind: str = ""

    @property
    def ok(self) -> bool:
        return not self.violations


def _blank(value: str | None) -> bool:
    return not isinstance(value, str) or not value.strip()


def _digest(value: str) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )


def _release_fingerprint(value: str) -> bool:
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


def _safe_relative_path(value: str) -> bool:
    if (
        _blank(value)
        or value != value.strip()
        or "\\" in value
        or ":" in value
        or "\x00" in value
    ):
        return False
    path = PurePosixPath(value)
    return (
        not path.is_absolute()
        and all(part not in {"", ".", ".."} for part in path.parts)
        and path.as_posix() == value
    )


def validate_manifest(
    manifest: EvidenceManifest,
    *,
    now: str,
    max_age_days: int,
    allowed_kinds: frozenset[str] | None = None,
) -> EvidenceReport:
    """Acumula todas las violaciones sin leer ficheros ni tocar red."""

    report = EvidenceReport(report_kind="manifest")
    add = report.violations.append
    if _blank(manifest.scope_id):
        add(Violation("scope_missing"))
    if not _release_fingerprint(manifest.release_fingerprint):
        add(Violation("release_fingerprint_invalid"))
    if not manifest.declared_origins or any(not _origin(origin) for origin in manifest.declared_origins):
        add(Violation("declared_origins_missing"))
    if len(set(manifest.declared_origins)) != len(manifest.declared_origins):
        add(Violation("duplicate_declared_origin"))
    if not manifest.required_kinds:
        add(Violation("required_kinds_missing"))
    if len(set(manifest.required_kinds)) != len(manifest.required_kinds):
        add(Violation("duplicate_required_kind"))
    if not manifest.items:
        add(Violation("evidence_items_missing"))
    if type(max_age_days) is not int or max_age_days <= 0:
        add(Violation("freshness_policy_invalid"))

    moment = _parse(now)
    cutoff = moment - timedelta(days=max_age_days) if moment and max_age_days > 0 else None
    if moment is None:
        add(Violation("now_invalid"))

    seen: set[str] = set()
    seen_paths: set[str] = set()
    kinds: set[str] = set()
    attestation_needed = False
    declared = set(manifest.declared_origins)
    for item in manifest.items:
        if _blank(item.item_id):
            add(Violation("item_id_missing"))
        elif item.item_id in seen:
            add(Violation("duplicate_item_id", item.item_id))
        seen.add(item.item_id)
        kinds.add(item.kind)

        if item.scope_id != manifest.scope_id:
            add(Violation("cross_scope_evidence", item.item_id))
        if item.origin not in declared:
            add(Violation("undeclared_origin", item.item_id))
        if not _origin(item.origin):
            add(Violation("item_origin_invalid", item.item_id))
        if _blank(item.kind):
            add(Violation("kind_missing", item.item_id))
        elif allowed_kinds is not None and item.kind not in allowed_kinds:
            add(Violation("kind_not_allowed", item.item_id))
        if not _safe_relative_path(item.path):
            add(Violation("unsafe_artifact_path", item.item_id))
        elif item.path in seen_paths:
            add(Violation("duplicate_artifact_path", item.item_id))
        seen_paths.add(item.path)
        if not _digest(item.sha256):
            add(Violation("digest_invalid", item.item_id))
        if type(item.draft) is not bool:
            add(Violation("draft_flag_invalid", item.item_id))
        elif item.draft:
            add(Violation("draft_in_package", item.item_id))

        collected = _parse(item.collected_at)
        if collected is None or cutoff is None or moment is None:
            add(Violation("collected_at_invalid", item.item_id))
        elif collected > moment:
            add(Violation("evidence_from_future", item.item_id))
        elif collected < cutoff:
            add(Violation("stale_evidence", item.item_id))

        if type(item.requires_attestation) is not bool:
            add(Violation("attestation_flag_invalid", item.item_id))
        else:
            attestation_needed = attestation_needed or item.requires_attestation

    for kind in manifest.required_kinds:
        if _blank(kind):
            add(Violation("required_kind_invalid"))
        elif kind not in kinds:
            add(Violation("required_kind_missing", detail=kind))

    if attestation_needed and (
        _blank(manifest.attestation_id) or _blank(manifest.attestation_actor_id)
    ):
        add(Violation("human_attestation_missing"))
    if any(
        value is not None and _blank(value)
        for value in (manifest.attestation_id, manifest.attestation_actor_id)
    ):
        add(Violation("attestation_metadata_invalid"))
    return report


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_artifact_hashes(manifest: EvidenceManifest, root: Path) -> EvidenceReport:
    """Verifica rutas y hashes sin seguir enlaces fuera de la raíz declarada."""

    report = EvidenceReport(report_kind="hashes")
    unresolved_base = Path(root).absolute()
    if unresolved_base.is_symlink():
        report.violations.extend(
            Violation("artifact_root_symlink_rejected", item.item_id)
            for item in manifest.items
        )
        return report
    base = unresolved_base.resolve()
    seen_files: set[tuple[int, int]] = set()
    for item in manifest.items:
        if not _safe_relative_path(item.path):
            report.violations.append(Violation("unsafe_artifact_path", item.item_id))
            continue
        relative = PurePosixPath(item.path)
        candidate = base / relative
        cursor = base
        symlink_found = False
        for part in relative.parts:
            cursor /= part
            if cursor.is_symlink():
                symlink_found = True
                break
        if symlink_found:
            report.violations.append(Violation("artifact_symlink_rejected", item.item_id))
            continue
        resolved = candidate.resolve(strict=False)
        if not resolved.is_relative_to(base):
            report.violations.append(Violation("artifact_path_escape", item.item_id))
        elif not resolved.is_file():
            report.violations.append(Violation("artifact_missing", item.item_id))
        else:
            stat = resolved.stat()
            identity = (stat.st_dev, stat.st_ino)
            if identity in seen_files:
                report.violations.append(
                    Violation("duplicate_artifact_identity", item.item_id)
                )
            else:
                seen_files.add(identity)
                if sha256_file(resolved) != item.sha256:
                    report.violations.append(
                        Violation("artifact_digest_mismatch", item.item_id)
                    )
    return report


def packageable_items(
    manifest: EvidenceManifest,
    *reports: EvidenceReport,
) -> tuple[EvidenceItem, ...]:
    kinds = {report.report_kind for report in reports}
    if {"manifest", "hashes"} - kinds or any(not report.ok for report in reports):
        return ()
    return tuple(sorted(manifest.items, key=lambda item: item.item_id))


def manifest_receipt(manifest: EvidenceManifest) -> str:
    """SHA-256 determinista del manifiesto final."""

    payload = json.dumps(
        asdict(manifest),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


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


def _optional_str(value: Any, field: str) -> str | None:
    if value is None:
        return None
    return _require_str(value, field)


def _require_int(value: Any, field: str) -> int:
    if type(value) is not int:
        raise ValueError(f"{field} debe ser entero JSON")
    return value


def _manifest(data: dict[str, Any]) -> EvidenceManifest:
    if not isinstance(data.get("items"), list):
        raise ValueError("items debe ser una lista")
    items = tuple(
        EvidenceItem(
            item_id=_require_str(row["item_id"], "items[].item_id"),
            scope_id=_require_str(row["scope_id"], "items[].scope_id"),
            kind=_require_str(row["kind"], "items[].kind"),
            origin=_require_str(row["origin"], "items[].origin"),
            collected_at=_require_str(row["collected_at"], "items[].collected_at"),
            sha256=_require_str(row["sha256"], "items[].sha256"),
            path=_require_str(row["path"], "items[].path"),
            draft=_require_bool(row.get("draft", False), "items[].draft"),
            requires_attestation=_require_bool(
                row.get("requires_attestation", False),
                "items[].requires_attestation",
            ),
        )
        for row in data["items"]
        if isinstance(row, dict)
    )
    if len(items) != len(data["items"]):
        raise ValueError("cada item debe ser un objeto")
    return EvidenceManifest(
        scope_id=_require_str(data["scope_id"], "scope_id"),
        release_fingerprint=_require_str(
            data["release_fingerprint"], "release_fingerprint"
        ),
        declared_origins=_tuple(data["declared_origins"]),
        required_kinds=_tuple(data["required_kinds"]),
        items=items,
        attestation_id=_optional_str(data.get("attestation_id"), "attestation_id"),
        attestation_actor_id=_optional_str(
            data.get("attestation_actor_id"), "attestation_actor_id"
        ),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args(argv)
    data = json.loads(args.path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("el manifiesto debe ser un objeto JSON")
    manifest = _manifest(data)
    allowed = data.get("allowed_kinds")
    report = validate_manifest(
        manifest,
        now=_require_str(data["now"], "now"),
        max_age_days=_require_int(data["max_age_days"], "max_age_days"),
        allowed_kinds=frozenset(_tuple(allowed)) if allowed is not None else None,
    )
    reports = [report, verify_artifact_hashes(manifest, args.root)]
    violations = [asdict(item) for current in reports for item in current.violations]
    output = {"ok": not violations, "violations": violations}
    if not violations:
        output["manifest_receipt"] = manifest_receipt(manifest)
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not violations else 1


if __name__ == "__main__":
    raise SystemExit(main())
