#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$project_dir"

concurrency="${CONCURRENCY:-10}"
for dataset in phishfuzzer_seed_42 nazario_enron_quality_seed_42; do
  for model in deepseek-v4-flash deepseek-v4-pro; do
    for thinking in off on; do
      max_tokens=512
      reasoning_args=()
      if [[ "$thinking" == "on" ]]; then
        max_tokens=2048
        reasoning_args=(--reasoning-effort high)
      fi
      for method in direct robust ours; do
        for condition in clean attacked_phishing injected_legitimate_control; do
          bash "$project_dir/src/tools/inference/run_deepseek_cell.sh" \
            "$dataset" "$condition" "$method" "$model" "$thinking" \
            --resume --concurrency "$concurrency" --max-tokens "$max_tokens" \
            --timeout 180 --retries 3 "${reasoning_args[@]}"
        done
      done
    done
  done
done
