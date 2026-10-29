import json

data = json.load(open('scratch/decision_analysis_master_results.json', encoding='utf-8'))
for suite in ['HeldOut_28', 'Diagnostic_20']:
    print(f"\n==================== {suite} ERRORS ====================")
    errors = data['suite_results'][suite]['errors']
    for m in ['M1_Baseline', 'M1_Enron', 'M2_ZeroShot', 'M3_Baseline', 'M4_Baseline', 'M4_Enron']:
        fps = [x['id'] for x in errors[m]['false_positives']]
        fns = [x['id'] for x in errors[m]['false_negatives']]
        print(f"{m:14} | FP ({len(fps)}): {fps} | FN ({len(fns)}): {fns}")

print("\n--- DETAILS OF M4 ERRORS ---")
for suite in ['HeldOut_28', 'Diagnostic_20']:
    for m in ['M4_Baseline', 'M4_Enron']:
        for fp in data['suite_results'][suite]['errors'][m]['false_positives']:
            print(f"[{suite}] {m} FP -> {fp['id']} ({fp['category']}): {fp['subject']}")
            print(f"   Snippet: {fp['text_snippet'][:100]}...")
            print(f"   Reasons: {fp['reasons']}")
            print(f"   Refs: {fp['retrieved_refs']}")

