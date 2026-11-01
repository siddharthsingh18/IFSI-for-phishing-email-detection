import json
import os
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

from src.experiments.phase5_a1_optimization.sanitizer_v2 import sanitize_stage2_input

with open("results/a1_generalization_v1/failure_case_details.json", "r", encoding="utf-8") as f:
    d = json.load(f)

inv1 = d["investigation_1_multilingual_sanitization_failures"]

print("Testing Sanitizer V2 against all 5 Chinese failure cases:")
all_passed = True
for sid, data in inv1.items():
    raw_text = data["body"]
    stage1_span = data.get("candidate_span", "")
    
    res = sanitize_stage2_input(raw_text, active_prompt_injection=True, candidate_span=stage1_span)
    
    passed = res["is_sanitized"] and not res["requires_manual_review"] and res["match_method"] == "flexible_pattern"
    if not passed:
        all_passed = False
        
    print(f"Sample: {sid}")
    print(f"  Stage 1 Candidate Span: {repr(stage1_span[:40])}...")
    print(f"  Sanitized: {res['is_sanitized']}")
    print(f"  Match method: {res['match_method']}")
    print(f"  Manual review required: {res['requires_manual_review']}")
    print(f"  Offsets: [{res['span_start']}:{res['span_end']}]")
    print(f"  Original slice matched: {repr(raw_text[res['span_start']:res['span_end']][:40])}...")
    print("-" * 50)

print(f"\nALL 5 CHINESE CASES RESOLVED WITHOUT MANUAL REVIEW: {all_passed}")
