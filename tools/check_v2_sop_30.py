import sys
import json
sys.path.insert(0, "src")
from core.domain_analyzer import analyze_email_domains, format_domain_evidence_block

with open("data/evaluation/live_benchmark_v2.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        d = json.loads(line)
        if d["id"] == "v2-sop-30":
            print("ID:", d["id"])
            print("Sender:", d["sender"])
            print("Subject:", d["subject"])
            ev = analyze_email_domains(d["subject"], d["sender"], d["body"])
            print("Evidence dict:")
            print(json.dumps(ev, indent=2))
            print("\nEvidence block:")
            print(format_domain_evidence_block(ev))
            break
