# Public release boundary

This repository is designed to publish the experiment code without silently
redistributing email text or per-request model traces.

## Publish

- `src/phishbench/` and `src/tools/`
- `tests/` and the synthetic records under `examples/`
- frozen prompt snapshot JSON and experiment configuration
- aggregate machine-readable results and reports
- source/preparation metadata and top-level integrity manifests
- selected paper source or PDF only after all authors approve redistribution

## Keep local by default

- `data/raw/` and `data/processed/`
- `experiments/inputs/*.jsonl` (expanded prompts contain email bodies)
- `experiments/raw/` (responses may repeat email text and reasoning traces)
- `experiments/work/`, `.env*`, caches, and temporary render/build files
- internal paper drafts, backups, reviewer notes, and venue-planning documents

The root `.gitignore` enforces this default boundary. Do not use `git add -f`
on an excluded artifact without completing a record-level privacy and upstream
license review.

## Before the first push

1. Choose and add a software license with both authors' approval. Until then,
   public visibility does not grant reuse rights.
2. Review `git status --short` and `git diff --cached --stat`.
3. Run `./src/tools/release/check_public_release.sh`.
4. Because `v2` is nested in a larger historical repository, create a clean
   standalone tree with
   `./src/tools/release/export_public_tree.sh /tmp/phishbench-public`.
5. Inspect the exported or staged file list for email bodies, credentials, absolute local
   paths, private reviewer material, and unpublished paper drafts.
6. If raw artifacts will be released separately, publish their hashes from
   `experiments/MANIFEST.json` and document the access/licensing process.

## Reproducibility levels

- **Code-level:** unit tests and the synthetic offline dry-run require no data
  or API key.
- **Prompt/matrix-level:** frozen prompt definitions and matrix configuration
  are included.
- **Aggregate-result-level:** final JSON and reports are included.
- **Record-level rerun:** requires the upstream datasets and model access. The
  email corpora and archived responses are intentionally not bundled here.
