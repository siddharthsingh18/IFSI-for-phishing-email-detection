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

## Installation & Environment Setup

PhishBench requires **Python 3.11+**.

```bash
# 1. Create and activate virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# 2. Install package in editable mode with dependencies
pip install -e .

# 3. Verify installation with test suite (49 passing tests)
pytest tests/
```

## Local Model Server Setup (Ollama)

The LLM evaluations (M2, M3, M4) utilize `qwen2.5:0.5b` served via local Ollama.

```bash
# 1. Start Ollama daemon (redirect logs to avoid pipe stalls)
ollama serve > /tmp/ollama.log 2>&1 &

# 2. Pull evaluation model
ollama pull qwen2.5:0.5b

# 3. Verify server responsiveness
curl -s http://127.0.0.1:11434/api/tags
```

Configuration parameters (temperature 0.0, timeout, token limits) are managed in [`config/ollama_config.json`](config/ollama_config.json).

## Reproducing the Experiment Pipeline

### Step 1: Data Preparation & Stratified Split
Deduplicate raw email records and generate stratified 80/10/10 train/validation/test splits:
```bash
python -m phishbench.data_loader \
  --data-dir data/raw \
  --output-dir data/splits \
  --seed 42
```

### Step 2: Build RAG Vector Index (Train Split Only)
Index embeddings for the 4,178 training emails using `all-MiniLM-L6-v2` and FAISS:
```bash
python -m phishbench.rag \
  --train data/splits/train.jsonl \
  --output-dir results/rag_index
```

### Step 3: Generate Injection Datasets (Marked & Unmarked)
Synthesize explicit-marker and naturally blended prompt injections across both phishing and legitimate control emails:
```bash
python -m phishbench.injections \
  --test-split data/splits/test.jsonl \
  --output-dir data/injections \
  --seed 42
```

### Step 4: Execute Full Benchmark & Generate Report (M1–M4)
Run all four detection methods across Clean, Marked, and Unmarked conditions ($4 \times 3 = 12$ matrix), compute confusion matrices, 2,000-sample bootstrap 95% CIs, and paired McNemar tests:
```bash
python -m phishbench.benchmark_suite \
  --train data/splits/train.jsonl \
  --splits-dir data/splits \
  --injections-dir data/injections \
  --rag-index results/rag_index \
  --results-dir results \
  --config config/ollama_config.json \
  --concurrency 4
```

### Step 5: Inspect Evaluation Artifacts
- **Comprehensive Markdown Report**: [`results/report.md`](results/report.md)
- **Machine-Readable Summary**: [`results/full_benchmark_summary.json`](results/full_benchmark_summary.json)
- **Per-Method Prediction Traces**: `results/M{1,2,3,4}_{clean,marked,unmarked}_predictions.jsonl`

## Evaluated Methods (M1–M4)

- **M1 (TF-IDF + LogisticRegression)**: Feature baseline trained on bag-of-words/n-grams ($V=10,000$).
- **M2 (Zero-Shot LLM)**: Direct prompt to `qwen2.5:0.5b` without external reference context.
- **M3 (RAG Combined Single-Call)**: Single API call retrieving top-3 train exemplars, generating verdict, confidence, and explanatory reasoning tokens.
- **M4 (RAG Two-Call Decoupled)**: Staged inference with strictly zero shared context: Call 1 performs prompt injection detection alone; Call 2 performs pure boolean phishing classification with RAG context.

## Citation and License

Released under the MIT License. See [LICENSE](LICENSE) for details.
