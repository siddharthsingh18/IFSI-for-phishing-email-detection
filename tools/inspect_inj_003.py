import json

with open("data/evaluation/phase5_regression_160.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        r = json.loads(line)
        if r["sample_id"] == "gen-inj-003":
            print("Subject:", r.get("subject"))
            print("Body:\n", r.get("body"))

with open("results/phase5_a1_sanitizer_latency/predictions.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        r = json.loads(line)
        if r["sample_id"] == "gen-inj-003" and r["config_id"] == "A1-Opt":
            print("\nA1-Opt Sanitization Info:")
            print("  Redacted span:", repr(r["sanitization_info"].get("redacted_span")))
            print("  Security action:", r.get("security_action"))
            print("  is_phishing:", r.get("is_phishing"))
            print("  Reasons:", r.get("reasons"))

