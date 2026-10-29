import json
import re
from pathlib import Path
import sys

sys.path.insert(0, "src")
from core.data_loaders import load_preset_samples

# Load diagnostic suite
with open("data/diagnostic_suite.json", "r", encoding="utf-8") as f:
    diag_samples = json.load(f)

print(f"Loaded {len(diag_samples)} diagnostic samples.")

# 1. Check overlap with train.jsonl
train_path = Path("data/splits/review_seed42/train.jsonl")
train_records = []
if train_path.exists():
    with open(train_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                train_records.append(json.loads(line))
print(f"Loaded {len(train_records)} train records.")

# 2. Check overlap with RAG metadata.json
rag_path = Path("results/rag_index/metadata.json")
rag_records = []
if rag_path.exists():
    with open(rag_path, "r", encoding="utf-8") as f:
        rag_data = json.load(f)
        rag_records = rag_data.get("records", [])
print(f"Loaded {len(rag_records)} RAG records.")

# 3. Check overlap with presets
presets_dict = load_preset_samples()
print(f"Loaded {len(presets_dict)} UI presets.")

# Check overlaps
train_texts = [r.get("text", "") for r in train_records]
rag_texts = [r.get("text", "") for r in rag_records]

overlaps = []
for d in diag_samples:
    d_body = d.get("body", "").strip()
    d_subj = d.get("subject", "").strip()
    d_full = f"Subject: {d_subj}\nFrom: {d.get('sender', '')}\n\n{d_body}".strip()
    
    # Check exact match with train
    for idx, t in enumerate(train_texts):
        if d_body == t or d_full == t:
            overlaps.append(("exact_train", d["id"], train_records[idx]["id"]))
        elif d_body in t or t in d_body:
            overlaps.append(("partial_train", d["id"], train_records[idx]["id"]))
            
    # Check exact match with RAG
    for idx, t in enumerate(rag_texts):
        if d_body == t or d_full == t:
            overlaps.append(("exact_rag", d["id"], rag_records[idx]["id"]))
        elif d_body in t or t in d_body:
            overlaps.append(("partial_rag", d["id"], rag_records[idx]["id"]))
            
    # Check exact match with presets
    for pname, pdata in presets_dict.items():
        p_body = pdata.get("body", "").strip()
        p_subj = pdata.get("subject", "").strip()
        p_full = f"Subject: {p_subj}\n\n{p_body}".strip()
        if d_body == p_body or d_full == p_full:
            overlaps.append(("exact_preset", d["id"], pname))
        elif d_body in p_body or p_body in d_body:
            overlaps.append(("partial_preset", d["id"], pname))

print(f"\nTotal Detected Overlaps: {len(overlaps)}")
for ov in overlaps:
    print("  Overlap:", ov)

# 4. Check prompt overlap
prompts_to_check = []
from phishbench.ollama_client import SYSTEM_PROMPT
prompts_to_check.append(("SYSTEM_PROMPT", SYSTEM_PROMPT))
from phishbench.rag import RAG_PROMPT_TEMPLATE
prompts_to_check.append(("RAG_PROMPT_TEMPLATE", RAG_PROMPT_TEMPLATE))
from phishbench.evaluate_decoupled_rag import SYSTEM_INJECTION_DETECTOR, SYSTEM_IS_PHISHING_ONLY
prompts_to_check.append(("SYSTEM_INJECTION_DETECTOR", SYSTEM_INJECTION_DETECTOR))
prompts_to_check.append(("SYSTEM_IS_PHISHING_ONLY", SYSTEM_IS_PHISHING_ONLY))

prompt_leaks = []
for d in diag_samples:
    for pname, ptext in prompts_to_check:
        if d["body"] in ptext or (len(d["body"]) > 30 and d["body"][:30] in ptext):
            prompt_leaks.append((d["id"], pname))

print(f"Prompt verbatim leaks: {len(prompt_leaks)} -> {prompt_leaks}")
