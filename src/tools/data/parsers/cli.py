"""Parse a source file/tree into provenance-preserving JSONL; never downloads."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .common import parse_csv, parse_eml_tree, parse_mbox, parse_spamassassin_ham_tree


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("mbox", "csv", "eml-tree", "spamassassin-ham-tree"), required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--check", action="store_true", help="Report missing input and exit without parsing")
    parser.add_argument("--sha256", help="Expected SHA-256 for --check")
    args = parser.parse_args()
    if args.check:
        if not args.input.exists():
            print(json.dumps({"missing": [str(args.input)]}))
            raise SystemExit(2)
        digest = hashlib.sha256(args.input.read_bytes()).hexdigest() if args.input.is_file() else None
        if args.sha256 and digest != args.sha256:
            print(json.dumps({"checksum_mismatch": {"path": str(args.input), "expected": args.sha256, "actual": digest}}))
            raise SystemExit(3)
        print(json.dumps({"present": str(args.input), "sha256": digest}))
        return
    if args.format == "mbox":
        records = parse_mbox(args.input, source=args.source, label=args.label)
    elif args.format == "csv":
        records = parse_csv(args.input, source=args.source)
    elif args.format == "spamassassin-ham-tree":
        if args.label != "legit":
            parser.error("SpamAssassin ham records must use --label legit")
        records = parse_spamassassin_ham_tree(args.input, source=args.source)
    else:
        records = parse_eml_tree(args.input, source=args.source, label=args.label)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(json.dumps({"records": len(records), "output": str(args.output)}))


if __name__ == "__main__":
    main()
