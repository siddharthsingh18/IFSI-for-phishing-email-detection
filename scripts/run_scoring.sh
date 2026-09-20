#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "usage: $0 OUTPUT_JSON RESULT_JSONL [RESULT_JSONL ...]" >&2
  exit 2
fi

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
output="$1"
shift
python_bin="${PYTHON_BIN:-python3}"

cd "$project_root"
PYTHONPATH=src "$python_bin" -m phishbench.evaluate \
  --results "$@" \
  --output "$output"

echo "Wrote complete evaluation report to $output"
