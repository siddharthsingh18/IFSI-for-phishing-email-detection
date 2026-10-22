# IFSI Phishing Detection

A research benchmark comparing phishing-detection methods under indirect prompt injection.

By Siddharth Singh & Sanchit Kukreja

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

IFSI compares four phishing-detection architectures (M1–M4), from a classical
TF-IDF baseline to retrieval-augmented LLM pipelines. It focuses on whether
LLM-based detectors maintain the correct phishing verdict when untrusted email
text contains indirect prompt-injection instructions. The project provides a
React frontend and a local FastAPI backend for live classification and
precomputed benchmark exploration.

> **Current frontend screenshot:** A fresh screenshot of the current running
> frontend is needed here. The committed landing-page screenshot currently
> shows the old 522 counter and should not be presented as current.

## Quick start

The app consists of a FastAPI backend and a React/Vite frontend. Use Python
3.11 or newer and Node.js 22.x. Live LLM methods use Ollama.

### 1. Backend

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Pull the configured default model:

```bash
ollama pull qwen2.5:0.5b
```

`llama3.2:3b` is configured as a promotion candidate, not the current default:

```bash
ollama pull llama3.2:3b
```

If Ollama is not already running as a service, start it in its own terminal:

```bash
ollama serve
```

Start FastAPI from the repository root in another terminal:

```bash
source .venv/bin/activate
uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000
```

### 2. Frontend

In a separate terminal:

```bash
cd frontend
npm ci
npm run dev
```

Open the local URL printed by Vite, normally
[http://localhost:5173](http://localhost:5173). The frontend uses
`http://localhost:8000` for the API by default; set `VITE_API_BASE_URL` to
override it.

> **Local data requirement:** Email corpora and the M1 training split are not
> included in Git. A fresh clone therefore needs the permitted local data
> prepared before it can run M1. See [data/README.md](data/README.md) and the
> source metadata for provenance and restrictions.

## Repository layout

```text
config/                 Ollama and dataset-gate configuration
data/README.md          Data provenance and local-data notes
data/metadata/          Tracked source and preparation metadata
docs/screenshots/       Committed application screenshots (some are historical)
examples/               Synthetic sample input for offline tooling
experiments/             Research experiment configurations and outputs
frontend/               React 19 + Vite application
prompts/                Versioned model prompts
results/                Aggregate benchmark summaries and reports
scripts/                Dataset preparation and audit scripts
src/api/                FastAPI routes and Pydantic schemas
src/core/               Live M1–M4 inference and resource loading
src/phishbench/         Offline research and benchmark pipeline
src/ui_utils.py         Compatibility exports backed by src/core/
tests/                  Backend and research tests
```

Raw email text, derived email splits, and per-request prediction traces are
local-only and are not distributed with this repository.

## Dataset

The local M1 review split combines:

- **Nazario phishing:** 2,279 raw messages; 2,241 retained after excluding
  38 empty or placeholder-body messages.
- **SpamAssassin ham:** 4,150 parsed legitimate emails.

The resulting grouped split contains 6,391 records: 4,881 train, 677
validation, and 833 test. M1 currently loads the **4,881-row training file**
from `data/splits/review_seed42/train.jsonl`.

This split is for local review, not an unbiased cross-source evaluation:
all legitimate messages come from SpamAssassin and all phishing messages come
from Nazario. Source and label are therefore perfectly confounded. The split
is not committed because the email text is local-only.

This is distinct from both the older, highly imbalanced M1 data (37,835
phishing and 85 legitimate examples) and the historical 522-email benchmark
test set summarized in `results/`. The historical test set and its precomputed
metrics must not be interpreted as evaluation on the local review split.

The project also retains provenance for legacy Nazario/Enron evaluation
artifacts. A MIME-extraction issue affected 196 of 441 Nazario phishing
records in the frozen legacy test copy. A quality-filtered artifact is
recorded for new cross-dataset experiments; Enron is not the ham source in
the current M1 review split.

For details on provenance, preparation, licensing, and local-only files, see
[data/README.md](data/README.md) and
[data/metadata/source_manifest.json](data/metadata/source_manifest.json).

## Evaluated methods

- **M1 — TF-IDF + Logistic Regression:** A deterministic classical baseline
  using a maximum 10,000 TF-IDF features. It does not interpret embedded
  instructions.
- **M2 — Zero-Shot LLM:** Sends the email to the configured local Ollama model
  with a direct classification prompt and requests a structured response.
- **M3 — RAG Combined:** Retrieves similar email examples and puts the
  references, email, and classification task into one LLM context.
- **M4 — RAG Decoupled / IFSI:** First asks the LLM to detect prompt injection,
  then makes a separate phishing-only classification call with retrieved
  examples. The backend combines the two stage signals; this can improve
  injection resilience while increasing false alarms on legitimate security,
  compliance, or IT messages.

## Key finding

On the historical 522-email held-out benchmark, unmarked prompt injection
reduced M3 phishing recall to 21.1%. M4 recovered recall to 96.1%, but at a
72.1% false-positive rate on legitimate email. This is an evasion/false-alarm
tradeoff, not evidence that M4 is ready for automatic production blocking; the
result is from the historical benchmark, not the source-confounded local M1
review split.

## Limitations

- **Small-model scope:** Evaluations use lightweight local models, primarily
  Qwen 2.5 0.5B; Llama 3.2 3B is a promotion candidate. Larger models may
  behave differently.
- **Fixed attack templates:** The benchmark uses five known attack families.
  Real attackers may use polymorphic, multi-turn, or novel instructions.
- **Uncalibrated confidence:** Confidence values are not calibrated
  probabilities.
- **Source confounding:** The current local review split has one source per
  label, so it cannot establish source-independent generalization.
- **M4 false-alarm and latency costs:** Its injection-first policy can flag
  legitimate correspondence, and two-stage inference makes two model calls
  per email.

This is a research and demonstration system, not a production email gateway.
Do not expose the development API directly to the public internet.

## Offline research tooling

The `phishbench-run` command remains available for legacy offline research
workflows and is exercised by CI in dry-run mode. It is separate from the
FastAPI endpoints and the React application.

## License

The software in this repository is released under the MIT License; see
[LICENSE](LICENSE). Upstream email datasets retain their own terms and are
not redistributed by this project.
