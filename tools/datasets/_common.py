from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse


OPEN_HOSTS = {"physionet.org", "www.physionet.org", "vitaldb.net", "www.vitaldb.net", "api.vitaldb.net"}


class DatasetToolError(RuntimeError):
    """A user-facing validation or acquisition error."""


def positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValueError("must be an integer") from exc
    if parsed <= 0:
        raise ValueError("must be greater than zero")
    return parsed


def load_registry(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise DatasetToolError(f"registry not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise DatasetToolError(
            f"registry must be JSON-compatible YAML: {path} ({exc.msg} at line {exc.lineno})"
        ) from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("datasets"), list):
        raise DatasetToolError("registry must contain a top-level datasets list")
    return payload


def dataset_by_id(registry: dict[str, Any], dataset_id: str) -> dict[str, Any]:
    matches = [row for row in registry["datasets"] if row.get("dataset_id") == dataset_id]
    if not matches:
        raise DatasetToolError(f"dataset_id is not registered: {dataset_id}")
    if len(matches) != 1:
        raise DatasetToolError(f"dataset_id is duplicated in registry: {dataset_id}")
    return matches[0]


def validate_open_https_url(url: str) -> str:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https":
        raise DatasetToolError("sample URL must use HTTPS")
    if host not in OPEN_HOSTS:
        raise DatasetToolError(
            f"sample host is not on the official open-data allowlist: {host or '<missing>'}"
        )
    if parsed.username or parsed.password:
        raise DatasetToolError("credentials must not be embedded in a sample URL")
    return host


def inside_git_checkout(path: Path) -> bool:
    resolved = path.expanduser().resolve(strict=False)
    current = resolved if resolved.is_dir() else resolved.parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return True
    return False


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def limited_files(sample: Path, limit: int) -> list[Path]:
    if not sample.exists():
        raise DatasetToolError(f"sample path does not exist: {sample}")
    if sample.is_file():
        return [sample]
    files = sorted(path for path in sample.rglob("*") if path.is_file() and ".git" not in path.parts)
    if len(files) > limit:
        raise DatasetToolError(
            f"sample contains {len(files)} files, exceeding --limit {limit}; increase the explicit limit"
        )
    return files


def require_fields(row: dict[str, Any], fields: Iterable[str], context: str) -> list[str]:
    errors: list[str] = []
    for field in fields:
        if field not in row or row[field] is None or str(row[field]).strip() == "":
            errors.append(f"{context}: missing required field '{field}'")
    return errors
