"""Small, deterministic parsers for the supported email source formats."""

from __future__ import annotations

import csv
import hashlib
import re
from email import policy
from email.parser import BytesParser
from pathlib import Path
from typing import Any, Iterable

from phishbench.data_loader import clean_text


def stable_content_id(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _email_text(message: Any) -> str:
    headers = "\n".join(f"{key}: {value}" for key, value in message.items())
    parts = [
        part for part in message.walk()
        if part.get_content_maintype() == "text"
        and not part.is_multipart()
        and part.get_content_disposition() != "attachment"
    ] if message.is_multipart() else [message]
    preferred = next((part for part in parts if part.get_content_type() == "text/plain"), parts[0])
    try:
        body = str(preferred.get_content())
    except (LookupError, UnicodeError):
        body = (preferred.get_payload(decode=True) or b"").decode("utf-8", errors="replace")
    return clean_text(f"{headers}\n\n{body}")


def _record(text: str, source: str, label: str, path: Path, raw: bytes, **extra: str) -> dict[str, str]:
    normalized = clean_text(text)
    return {
        "id": stable_content_id(normalized),
        "text": normalized,
        "label": label,
        "source": source,
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "original_path": str(path),
        **extra,
    }


def parse_mbox(path: Path, *, source: str, label: str, family: str | None = None) -> list[dict[str, str]]:
    """Parse an mbox without changing the source file."""
    from mailbox import mbox

    records = []
    mailbox = mbox(path, factory=None)
    try:
        for key in mailbox.iterkeys():
            raw = mailbox.get_bytes(key)
            parsed = BytesParser(policy=policy.default).parsebytes(raw)
            text = _email_text(parsed)
            if text:
                records.append(
                    _record(text, source, label, path, raw, **({"family": family} if family else {}))
                )
    finally:
        mailbox.close()
    return records


def parse_csv(
    path: Path,
    *,
    source: str,
    label_column: str = "label",
    text_columns: tuple[str, ...] = ("text", "body", "content"),
    label_map: dict[str, str] | None = None,
) -> list[dict[str, str]]:
    records = []
    raw = path.read_bytes()
    with path.open(newline="", encoding="utf-8-sig", errors="replace") as handle:
        for row in csv.DictReader(handle):
            text = next((row.get(column, "") for column in text_columns if row.get(column)), "")
            value = str(row.get(label_column, "")).strip().casefold()
            label = (label_map or {}).get(value, value)
            if text and label:
                records.append(_record(text, source, label, path, raw))
    return records


def parse_eml_tree(
    root: Path,
    *,
    source: str,
    label: str,
    family_from_parent: bool = True,
) -> list[dict[str, str]]:
    records = []
    for path in sorted(root.rglob("*.eml")):
        raw = path.read_bytes()
        text = _email_text(BytesParser(policy=policy.default).parsebytes(raw))
        if text:
            family = path.parent.name if family_from_parent else None
            records.append(_record(text, source, label, path, raw, **({"family": family} if family else {})))
    return records


def parse_spamassassin_ham_tree(root: Path, *, source: str = "spamassassin_ham") -> list[dict[str, str]]:
    """Parse SpamAssassin's extensionless ham message files, excluding its ``cmds`` helper."""
    if not root.is_dir():
        raise NotADirectoryError(f"SpamAssassin ham root is not a directory: {root}")
    message_name = re.compile(r"\d+\.[0-9a-fA-F]{32}\Z")
    ham_sets = {"easy_ham", "easy_ham_2", "hard_ham"}
    if not any((root / name).is_dir() for name in ham_sets):
        raise ValueError(f"No SpamAssassin ham subsets found under: {root}")
    records = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.parent.relative_to(root).parts[0] not in ham_sets:
            continue
        if path.name == "cmds":
            continue
        if not message_name.fullmatch(path.name):
            raise ValueError(f"Unexpected file in SpamAssassin ham tree: {path}")
        raw = path.read_bytes()
        text = _email_text(BytesParser(policy=policy.default).parsebytes(raw))
        if text:
            records.append(_record(text, source, "legit", path, raw, family=path.parent.name))
    if not records:
        raise ValueError(f"No SpamAssassin ham messages found under: {root}")
    return records
