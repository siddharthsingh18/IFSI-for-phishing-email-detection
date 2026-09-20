#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
upstream_dir="$project_dir/data/raw/phishfuzzer/upstream"
commit="1e21dd4edbe5c64694f156bf5318c97c7c80681c"
expected_seed_sha256="394d542e27dcef57321bc69f0f93b03e5965531f616eb3d3c79416cc60a30765"

sha256_file() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  else
    shasum -a 256 "$1" | awk '{print $1}'
  fi
}

if [[ ! -d "$upstream_dir/.git" ]]; then
  git clone --no-checkout https://github.com/DataPhish/PhishFuzzer.git "$upstream_dir"
fi

git -C "$upstream_dir" fetch --depth 1 origin "$commit"
git -C "$upstream_dir" checkout --detach "$commit"

seed_file="$upstream_dir/PhishFuzzer_emails_original_seed_v1.json"
actual_seed_sha256="$(sha256_file "$seed_file")"
if [[ "$actual_seed_sha256" != "$expected_seed_sha256" ]]; then
  echo "PhishFuzzer seed SHA-256 mismatch: $actual_seed_sha256" >&2
  exit 1
fi

for reused in \
  "$project_dir/../v1/data/processed/nazario_enron/nazario_enron_test.jsonl" \
  "$project_dir/../v1/data/processed/nazario_enron/preparation_report.json"; do
  if [[ ! -f "$reused" ]]; then
    echo "required frozen v1 artifact is missing: $reused" >&2
    exit 1
  fi
done

echo "PhishFuzzer pinned at $commit; seed SHA-256 verified."
echo "Frozen Nazario+Enron v1 artifacts are present."
