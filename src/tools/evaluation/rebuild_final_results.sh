#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
deepseek_dir="$project_root/experiments/raw/deepseek-v4-main"
qwen_dir="$project_root/experiments/raw/qwen3.5-vllm-main"
prompts="$project_root/experiments/inputs/phishbench_portable_prompts_v1.jsonl"
output="$project_root/experiments/results/all-model-results.json"
pricing="$project_root/experiments/config/deepseek_pricing_2026-08-09.json"
bootstrap_iterations="${BOOTSTRAP_ITERATIONS:-2000}"
python_bin="${PYTHON_BIN:-python3}"
work_dir="$(mktemp -d /tmp/phishbench-rebuild.XXXXXX)"

cleanup() {
  find "$work_dir" -type f -delete
  find "$work_dir" -depth -type d -empty -delete
}
trap cleanup EXIT

mkdir -p "$work_dir/qwen-metrics"

deepseek_results=()
while IFS= read -r result_path; do
  deepseek_results+=("$result_path")
done < <(find "$deepseek_dir/cells" -mindepth 2 -maxdepth 2 -name results.jsonl -print | sort)

if [[ ${#deepseek_results[@]} -eq 0 ]]; then
  echo "no archived DeepSeek results found under $deepseek_dir/cells" >&2
  exit 1
fi

PYTHONPATH="$project_root/src" "$python_bin" -m phishbench.evaluate \
  --results "${deepseek_results[@]}" \
  --output "$work_dir/deepseek-metrics.json" \
  --pricing "$pricing" \
  --bootstrap-iterations "$bootstrap_iterations"

run_specs=()
for result_path in "$qwen_dir"/*.jsonl; do
  run_id="$(basename "$result_path" .jsonl)"
  metrics_path="$work_dir/qwen-metrics/$run_id.json"
  PYTHONPATH="$project_root/src" "$python_bin" \
    "$project_root/src/tools/evaluation/evaluate_portable_results.py" \
    --prompts "$prompts" \
    --results "$result_path" \
    --output "$metrics_path"
  run_specs+=(--run "$run_id,$result_path,$metrics_path")
done

PYTHONPATH="$project_root/src" "$python_bin" \
  "$project_root/src/tools/evaluation/combine_portable_metrics.py" \
  --source-manifest "$qwen_dir/MANIFEST.json" \
  --output "$work_dir/qwen-matrix.json" \
  "${run_specs[@]}"

PYTHONPATH="$project_root/src" "$python_bin" \
  "$project_root/src/tools/evaluation/compile_all_experiment_results.py" \
  --deepseek "$work_dir/deepseek-metrics.json" \
  --qwen "$work_dir/qwen-matrix.json" \
  --output "$output" \
  --deepseek-raw-manifest "$deepseek_dir/MANIFEST.json" \
  --qwen-raw-manifest "$qwen_dir/MANIFEST.json" \
  --portable-prompts "$prompts"

echo "Rebuilt $output"
