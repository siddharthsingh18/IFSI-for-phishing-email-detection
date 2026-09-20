#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$project_dir"
PYTHONPATH=src "${PYTHON_BIN:-python3}" -m phishbench.validate_artifacts "$@"
