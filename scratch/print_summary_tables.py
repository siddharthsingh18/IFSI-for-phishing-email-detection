import json

data = json.load(open('scratch/decision_analysis_master_results.json', encoding='utf-8'))
for suite_name in ['HeldOut_28', 'Diagnostic_20']:
    print(f"\n==================== {suite_name} METRICS ====================")
    metrics = data['suite_results'][suite_name]['metrics']
    for k, v in metrics.items():
        print(f"{k:14} | Acc: {v['accuracy']*100:5.2f}% | Prec: {v['precision']*100:5.2f}% | Rec: {v['recall']*100:5.2f}% | F1: {v['f1']*100:5.2f}% | FPR: {v['fpr']*100:5.2f}% | FNR: {v['fnr']*100:5.2f}% | TP={v['TP']:2d} FP={v['FP']:2d} TN={v['TN']:2d} FN={v['FN']:2d}")

print("\n==================== M4 STAGE 1 INJECTION DETECTOR ====================")
for suite_name in ['HeldOut_28', 'Diagnostic_20']:
    print(f"\n--- {suite_name} ---")
    inj = data['suite_results'][suite_name]['m4_injection_detector']
    for k, v in inj.items():
        print(f"{k:28} | Acc: {v['accuracy']*100:5.2f}% | Prec: {v['precision']*100:5.2f}% | Rec: {v['recall']*100:5.2f}% | FPR: {v['fpr']*100:5.2f}% | TP={v['TP']:2d} FP={v['FP']:2d} TN={v['TN']:2d} FN={v['FN']:2d}")

