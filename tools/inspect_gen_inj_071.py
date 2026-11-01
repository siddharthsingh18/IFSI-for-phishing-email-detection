import json

preds = [json.loads(x) for x in open("results/phase7_domain_precision/predictions.jsonl", encoding="utf-8")]

r_a = next(r for r in preds if r["config_id"] == "A" and r["sample_id"] == "gen-inj-071")
r_b = next(r for r in preds if r["config_id"] == "B" and r["sample_id"] == "gen-inj-071")

print("=== SAMPLE gen-inj-071 ===")
print("Category:", r_a.get("category"))
print("Ground truth:", r_a.get("ground_truth_label"), r_a.get("ground_truth_is_phishing"))
print("Config A:", r_a.get("verdict"), r_a.get("is_phishing"), r_a.get("security_action"))
print("Config B:", r_b.get("verdict"), r_b.get("is_phishing"), r_b.get("security_action"))
print("Config B active injection:", r_b.get("active_prompt_injection"), "quoted:", r_b.get("quoted_prompt_injection"))
print("Config B reasons:", r_b.get("reasons"))

