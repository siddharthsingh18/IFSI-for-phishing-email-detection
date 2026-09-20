#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 OUTPUT_DIRECTORY" >&2
  exit 2
fi

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
output_dir="$1"

if [[ -e "$output_dir" ]] && [[ -n "$(find "$output_dir" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]]; then
  echo "refusing to overwrite non-empty directory: $output_dir" >&2
  exit 1
fi

mkdir -p "$output_dir"
cd "$project_root"

copied=0
while IFS= read -r relative_path; do
  [[ -f "$relative_path" ]] || continue
  destination="$output_dir/$relative_path"
  mkdir -p "$(dirname "$destination")"
  cp -p "$relative_path" "$destination"
  copied=$((copied + 1))
done < <({ git ls-files; git ls-files --others --exclude-standard; } | sort -u)

if [[ "$copied" -eq 0 ]]; then
  echo "no public files were selected" >&2
  exit 1
fi

echo "Exported $copied files to $output_dir"
echo "Review the export, choose a license, then initialize its Git repository."
