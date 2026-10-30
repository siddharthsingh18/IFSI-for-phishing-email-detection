import sys
import json
sys.path.insert(0, "src")
from core.inference_m4_v2 import (
    get_balanced_rag_retriever,
    format_balanced_reference_block,
    SYSTEM_IS_PHISHING_ONLY_V2,
    _call_ollama_json
)
from core.domain_analyzer import analyze_email_domains, format_domain_evidence_block

with open("data/evaluation/live_benchmark_v2.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        d = json.loads(line)
        if d["id"] == "v2-sop-30":
            email_text = f"Subject: {d['subject']}\nFrom: {d['sender']}\n\n{d['body']}"
            domain_analysis = analyze_email_domains(d["subject"], d["sender"], email_text)
            domain_evidence_block = format_domain_evidence_block(domain_analysis)
            balanced_retriever = get_balanced_rag_retriever()
            retrieved = balanced_retriever.retrieve_balanced(email_text, k_phish=2, k_legit=2)
            rag_block = format_balanced_reference_block(retrieved)
            prompt = f"{rag_block}\n\n{domain_evidence_block}\n\n--- CANDIDATE EMAIL TO EVALUATE ---\n{email_text}\n--- END CANDIDATE EMAIL ---"
            print("=== STAGE 2 PROMPT ===")
            print(prompt)
            print("=== CALLING OLLAMA ===")
            p, raw, dur, fail = _call_ollama_json(SYSTEM_IS_PHISHING_ONLY_V2, prompt)
            print("Response:", json.dumps(p, indent=2))
            break

