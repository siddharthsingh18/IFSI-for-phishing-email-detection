# IFSI for Phishing Email Detection

Code and aggregate artifacts for **Injection-First Staged Inference: Balancing
Robustness and Reasoning Cost in LLM-Based Phishing Detection**.

PhishBench evaluates three single-call prompting protocols:

- **Direct**: phishing classification with a shared untrusted-data boundary;
- **Robust**: Direct plus explicit prompt-injection guidance;
- **Ours**: Robust plus an ordered injection assessment before the phishing
  decision.

The paired evaluation covers clean email, injected phishing email, and matched
injected legitimate controls. It reports ordinary classification quality,
attacked-phishing recall, control false-positive rate, paired McNemar tests,
format reliability, and reasoning-inclusive output tokens.

## Repository layout

```text
src/phishbench/        Core data, attack, prompt, inference, and evaluation code
src/tools/             Reproducible shell and reporting entry points
prompts/               Exact Direct, Robust, and Ours system prompts
scripts/               Short public entry points for common workflows
tests/                 Standard-library unit tests
examples/              Synthetic, redistribution-safe smoke-test records
experiments/config/    Frozen experiment matrix and pricing snapshot
experiments/results/   Aggregate machine-readable results and reports
data/metadata/         Source provenance and preparation summaries
```

Email corpora, expanded per-email prompts, and per-request model traces are
intentionally excluded from Git. See [PUBLIC_RELEASE.md](PUBLIC_RELEASE.md).

## Installation

PhishBench requires Python 3.10 or newer and has no third-party runtime
dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

## Offline verification

These commands do not call a model service and do not require private data:

```bash
python -m unittest discover -s tests -v

phishbench-run \
  --input examples/sample_emails.jsonl \
  --output /tmp/phishbench-results.jsonl \
  --manifest /tmp/phishbench-manifest.json \
  --dataset synthetic_demo \
  --condition clean \
  --method ours \
  --model deepseek-v4-pro \
  --thinking off \
  --limit 1 \
  --dry-run

./src/tools/release/check_public_release.sh
```

The dry-run writes a manifest and computes the exact expanded-prompt hash, but
does not read an API key or send a request.

## Core implementation map

The requested reproducibility components are deliberately separated:

- prompt-injection simulation: `src/phishbench/attacks.py`;
- dataset preparation and paired conditions: `src/phishbench/prepare.py` and
  `src/phishbench/attacks.py`;
- batch inference: `src/phishbench/runner.py` and
  `src/tools/inference/run_deepseek_matrix.sh`;
- exact paper prompts: `prompts/direct.txt`, `prompts/robust.txt`, and
  `prompts/ours.txt`;
- metric and paired-test implementation: `src/phishbench/evaluate.py`;
- aggregate paper-table rebuild: `src/tools/evaluation/rebuild_final_results.sh`.

To score one or more completed JSONL result files and write the complete
machine-readable report directly:

```bash
./scripts/run_scoring.sh output/metrics.json results-a.jsonl results-b.jsonl
```

The scorer reports failure-as-error classification metrics, valid-output-only
metrics, injection detection, paired flips, exact McNemar comparisons, output
token distributions, format reliability, latency summaries, and estimated
API cost when the matching pricing snapshot is available.

This workspace is nested inside a larger historical Git repository. Create a
standalone public tree instead of publishing the parent repository:

```bash
./src/tools/release/export_public_tree.sh /tmp/ifsi-public
cd /tmp/ifsi-public
git init
```

Inspect the exported tree and choose a license before committing or pushing.

## Reproducing the experiment pipeline

1. Acquire the upstream datasets and verify their terms. The local data layout
   and pinned source metadata are described in [data/README.md](data/README.md).
2. Prepare paired clean/attack/control files with the commands in
   [src/tools/README.md](src/tools/README.md).
3. Freeze the prompt snapshot and experiment matrix:

   ```bash
   ./src/tools/prompts/freeze_prompts.sh
   ./src/tools/prompts/export_portable_prompts.sh
   ```

4. For DeepSeek-compatible inference, set `DEEPSEEK_API_KEY` in the shell and
   run a cell or the matrix. Never place a key in a tracked file.
5. Evaluate local-model JSONL with `evaluate_portable_results.py`, then combine
   all model results using the evaluation tools.

The archived paper results can be rebuilt only when the excluded raw artifacts
are present locally:

```bash
BOOTSTRAP_ITERATIONS=2000 ./src/tools/evaluation/rebuild_final_results.sh
```

This rebuild reads saved JSONL files; it does not invoke a model API.

## Frozen experimental scope

- datasets: PhishFuzzer and a quality-filtered Nazario + Enron set;
- conditions: clean, attacked phishing, injected legitimate control;
- methods: Direct, Robust, Ours; plus a limited no-summary ablation;
- main paper models: DeepSeek-v4-Pro, Qwen3.5-9B, Qwen3.5-35B-A3B;
- audit/boundary model: DeepSeek-v4-Flash;
- reasoning regimes: non-thinking and thinking.

The complete aggregate result is
`experiments/results/all-model-results.json`. The reports under
`experiments/results/` explain the metrics and statistical families. The
results support a model-dependent robustness/cost trade-off, not universal
superiority across every model and reasoning regime.

## Citation and license

Citation metadata and a publication link will be added when the proceedings
record is final. A
software license has intentionally not been selected in this working copy;
both authors should approve one before public release.
