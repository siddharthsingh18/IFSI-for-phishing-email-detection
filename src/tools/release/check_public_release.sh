#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
python_bin="${PYTHON_BIN:-python3}"
cd "$project_root"

for private_probe in \
  data/raw/.release-boundary-probe \
  data/processed/.release-boundary-probe \
  experiments/raw/.release-boundary-probe \
  experiments/work/.release-boundary-probe \
  experiments/inputs/phishbench_portable_prompts_v1.jsonl \
  paper/.release-boundary-probe \
  docs/INTERNAL_NOTES.md; do
  if ! git check-ignore --no-index -q "$private_probe"; then
    echo "release boundary failure: not ignored: $private_probe" >&2
    exit 1
  fi
done

while IFS= read -r tracked_path; do
  [[ -e "$tracked_path" ]] || continue
  case "$tracked_path" in
    .env|.env.*|data/raw/*|data/processed/*|experiments/raw/*|experiments/work/*|experiments/inputs/*.jsonl|paper/*)
      echo "release boundary failure: private artifact is tracked: $tracked_path" >&2
      exit 1
      ;;
  esac
done < <(git ls-files)

PYTHONPATH=src "$python_bin" -m compileall -q src tests
PYTHONPATH=src "$python_bin" -m unittest discover -s tests -v

release_tmp="$(mktemp -d "${TMPDIR:-/tmp}/phishbench-release.XXXXXX")"
cleanup() {
  find "$release_tmp" -type f -delete
  find "$release_tmp" -depth -type d -empty -delete
}
trap cleanup EXIT

PYTHONPATH=src "$python_bin" -m phishbench.runner \
  --input examples/sample_emails.jsonl \
  --output "$release_tmp/results.jsonl" \
  --manifest "$release_tmp/manifest.json" \
  --dataset synthetic_demo \
  --condition clean \
  --method ours \
  --model deepseek-v4-pro \
  --thinking off \
  --limit 1 \
  --dry-run >/dev/null

echo "Public-release checks passed."
