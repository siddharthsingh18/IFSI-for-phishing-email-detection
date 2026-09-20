#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 5 ]]; then
  echo "usage: $0 DATASET CONDITION METHOD MODEL THINKING [runner options...]" >&2
  exit 2
fi

dataset="$1"
condition="$2"
method="$3"
model="$4"
thinking="$5"
shift 5

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
input="$project_dir/data/processed/$dataset/$condition.jsonl"
run_name="${dataset}__${condition}__${method}__${model}__thinking-${thinking}"
output="$project_dir/experiments/work/deepseek/$run_name/results.jsonl"
manifest="$project_dir/experiments/work/deepseek/$run_name/manifest.json"

cd "$project_dir"
PYTHONPATH=src "${PYTHON_BIN:-python3}" -m phishbench.runner \
  --input "$input" --output "$output" --manifest "$manifest" \
  --dataset "$dataset" --condition "$condition" --method "$method" \
  --model "$model" --thinking "$thinking" "$@"
