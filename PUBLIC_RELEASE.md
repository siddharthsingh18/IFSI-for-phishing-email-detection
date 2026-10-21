# Public release boundary

This repository is designed to publish the experiment code without silently
redistributing email text or per-request model traces.

## Publish

- `src/phishbench/` and `src/tools/`
- `tests/` and the synthetic records under `examples/`
- frozen prompt snapshot JSON and experiment configuration
- aggregate machine-readable results and reports
- source/preparation metadata and top-level integrity manifests
- selected documentation and summary reports

## Keep local by default

- `data/raw/` and `data/processed/`
- `experiments/inputs/*.jsonl` (expanded prompts contain email bodies)
- `experiments/raw/` (responses may repeat email text and reasoning traces)
- `experiments/work/`, `.env*`, caches, and temporary render/build files
- internal paper drafts, backups, reviewer notes, and venue-planning documents

The root `.gitignore` enforces this default boundary. Do not use `git add -f`
on an excluded artifact without completing a record-level privacy and upstream
license review.

## Before publishing a new release

1. The repository is released under the MIT license in `LICENSE`; retain
   upstream attribution and verify redistribution terms for any source data.
2. Review `git status --short` and `git diff --cached --stat`.
3. Run `./src/tools/release/check_public_release.sh` when that helper exists in
   the checkout.
4. Because historical commits may contain older V1 material, create a clean
   standalone tree with
   `./src/tools/release/export_public_tree.sh /tmp/phishbench-public`.
5. Inspect the exported or staged file list for email bodies, credentials, absolute local
   paths, private reviewer material, and unpublished paper drafts.
6. Never commit raw `.mbox` corpora or expanded email records. If raw artifacts
   will be released separately, publish their hashes from
   `experiments/MANIFEST.json` and document the access/licensing process.

## Reproducibility levels

- **Code-level:** unit tests and the synthetic offline dry-run require no data
  or API key.
- **Prompt/matrix-level:** frozen prompt definitions and matrix configuration
  are included.
- **Aggregate-result-level:** final JSON and reports are included.
- **Record-level rerun:** requires the upstream datasets and model access. The
  email corpora and archived responses are intentionally not bundled here.
