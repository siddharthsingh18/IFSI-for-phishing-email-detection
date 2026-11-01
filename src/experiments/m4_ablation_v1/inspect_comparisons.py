import json

with open('results/m4_ablation_v1/independently_verified_comparisons.json', 'r', encoding='utf-8') as f:
    comps = json.load(f)

for k, v in comps.items():
    st = v['statistical_test']
    print(f"{k}: Net={st['net_gain']:+d} (b={st['b_favors_test']}, c={st['c_favors_baseline']}), chi2={st['mcnemar_chi2_corrected']:.4f}, p_asymp={st['asymptotic_p_value']:.6f}, p_exact={st['exact_binomial_p_value']:.6f}, CI_95=[{st['delta_ci_95'][0]:.4f}, {st['delta_ci_95'][1]:.4f}]")

