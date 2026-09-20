# 补充统计：配对翻转、多重校正、Token 与可靠性

口径：论文主叙事暂以 DeepSeek-v4-Pro、Qwen3.5-9B、Qwen3.5-35B-A3B 为主；
DeepSeek-v4-Flash 原始结果继续保留，作为审计与方法边界，不进入主张汇总。
成本代理统一使用最终回答加 reasoning 的输出 Token；Qwen 原始记录没有统一 input token 和 latency。

## Ours 的 Clean→Attack 配对翻转

`损害`表示 clean 判对、注入后判错；`恢复`表示 clean 判错、注入后判对。

| 配置 | 数据集 | 条件 | N | 损害 | 恢复 | 净损害 |
|---|---|---|---:|---:|---:|---:|
| deepseek-v4-pro_non-thinking | PhishFuzzer | 黑注入 phishing | 1000 | 0 (0.00%) | 33 (3.30%) | -33 |
| deepseek-v4-pro_non-thinking | PhishFuzzer | 白注入 legitimate | 1000 | 5 (0.50%) | 0 (0.00%) | +5 |
| deepseek-v4-pro_non-thinking | Nazario+Enron | 黑注入 phishing | 239 | 0 (0.00%) | 2 (0.84%) | -2 |
| deepseek-v4-pro_non-thinking | Nazario+Enron | 白注入 legitimate | 239 | 1 (0.42%) | 0 (0.00%) | +1 |
| deepseek-v4-pro_thinking | PhishFuzzer | 黑注入 phishing | 1000 | 5 (0.50%) | 20 (2.00%) | -15 |
| deepseek-v4-pro_thinking | PhishFuzzer | 白注入 legitimate | 1000 | 16 (1.60%) | 1 (0.10%) | +15 |
| deepseek-v4-pro_thinking | Nazario+Enron | 黑注入 phishing | 239 | 1 (0.42%) | 0 (0.00%) | +1 |
| deepseek-v4-pro_thinking | Nazario+Enron | 白注入 legitimate | 239 | 4 (1.67%) | 2 (0.84%) | +2 |
| qwen3.5-9b_non-thinking | PhishFuzzer | 黑注入 phishing | 1000 | 4 (0.40%) | 51 (5.10%) | -47 |
| qwen3.5-9b_non-thinking | PhishFuzzer | 白注入 legitimate | 1000 | 24 (2.40%) | 0 (0.00%) | +24 |
| qwen3.5-9b_non-thinking | Nazario+Enron | 黑注入 phishing | 239 | 0 (0.00%) | 9 (3.77%) | -9 |
| qwen3.5-9b_non-thinking | Nazario+Enron | 白注入 legitimate | 239 | 6 (2.51%) | 0 (0.00%) | +6 |
| qwen3.5-9b_thinking | PhishFuzzer | 黑注入 phishing | 1000 | 4 (0.40%) | 16 (1.60%) | -12 |
| qwen3.5-9b_thinking | PhishFuzzer | 白注入 legitimate | 1000 | 36 (3.60%) | 4 (0.40%) | +32 |
| qwen3.5-9b_thinking | Nazario+Enron | 黑注入 phishing | 239 | 1 (0.42%) | 5 (2.09%) | -4 |
| qwen3.5-9b_thinking | Nazario+Enron | 白注入 legitimate | 239 | 4 (1.67%) | 0 (0.00%) | +4 |
| qwen3.5-35b-a3b_non-thinking | PhishFuzzer | 黑注入 phishing | 1000 | 2 (0.20%) | 17 (1.70%) | -15 |
| qwen3.5-35b-a3b_non-thinking | PhishFuzzer | 白注入 legitimate | 1000 | 5 (0.50%) | 4 (0.40%) | +1 |
| qwen3.5-35b-a3b_non-thinking | Nazario+Enron | 黑注入 phishing | 239 | 1 (0.42%) | 5 (2.09%) | -4 |
| qwen3.5-35b-a3b_non-thinking | Nazario+Enron | 白注入 legitimate | 239 | 5 (2.09%) | 0 (0.00%) | +5 |
| qwen3.5-35b-a3b_thinking | PhishFuzzer | 黑注入 phishing | 1000 | 0 (0.00%) | 8 (0.80%) | -8 |
| qwen3.5-35b-a3b_thinking | PhishFuzzer | 白注入 legitimate | 1000 | 20 (2.00%) | 2 (0.20%) | +18 |
| qwen3.5-35b-a3b_thinking | Nazario+Enron | 黑注入 phishing | 239 | 1 (0.42%) | 2 (0.84%) | -1 |
| qwen3.5-35b-a3b_thinking | Nazario+Enron | 白注入 legitimate | 239 | 11 (4.60%) | 0 (0.00%) | +11 |

## Ours vs Robust：attacked-phishing McNemar 与 Holm 校正

Holm family 包含完整矩阵 16 个比较，包括归档的 Flash，因而是较保守的校正。
`R错/O对`是 Ours 相对 Robust 恢复的样本；`R对/O错`是 Ours 新增漏检。

| 配置 | 数据集 | R错/O对 | R对/O错 | 净恢复 | 原始 p | Holm p | 0.05 |
|---|---|---:|---:|---:|---:|---:|:---:|
| deepseek-v4-flash_non-thinking | PhishFuzzer | 0 | 10 | -10 | 0.00195 | 0.0256 | 是 |
| deepseek-v4-flash_non-thinking | Nazario+Enron | 2 | 3 | -1 | 1 | 1 | 否 |
| deepseek-v4-flash_thinking | PhishFuzzer | 1 | 13 | -12 | 0.00183 | 0.0256 | 是 |
| deepseek-v4-flash_thinking | Nazario+Enron | 1 | 4 | -3 | 0.375 | 1 | 否 |
| deepseek-v4-pro_non-thinking | PhishFuzzer | 31 | 0 | +31 | 9.31e-10 | 1.4e-08 | 是 |
| deepseek-v4-pro_non-thinking | Nazario+Enron | 3 | 0 | +3 | 0.25 | 1 | 否 |
| deepseek-v4-pro_thinking | PhishFuzzer | 8 | 8 | +0 | 1 | 1 | 否 |
| deepseek-v4-pro_thinking | Nazario+Enron | 1 | 7 | -6 | 0.0703 | 0.773 | 否 |
| qwen3.5-9b_non-thinking | PhishFuzzer | 46 | 4 | +42 | 4.46e-10 | 7.14e-09 | 是 |
| qwen3.5-9b_non-thinking | Nazario+Enron | 9 | 0 | +9 | 0.00391 | 0.0469 | 是 |
| qwen3.5-9b_thinking | PhishFuzzer | 5 | 4 | +1 | 1 | 1 | 否 |
| qwen3.5-9b_thinking | Nazario+Enron | 3 | 2 | +1 | 1 | 1 | 否 |
| qwen3.5-35b-a3b_non-thinking | PhishFuzzer | 9 | 10 | -1 | 1 | 1 | 否 |
| qwen3.5-35b-a3b_non-thinking | Nazario+Enron | 6 | 2 | +4 | 0.289 | 1 | 否 |
| qwen3.5-35b-a3b_thinking | PhishFuzzer | 2 | 2 | +0 | 1 | 1 | 否 |
| qwen3.5-35b-a3b_thinking | Nazario+Enron | 0 | 1 | -1 | 1 | 1 | 否 |

## Token 分布

每项为 `mean / median / p95`；在两个数据集和三种条件上汇总。

| 配置 | 方法 | Answer | Reasoning | 输出合计 | Input | Total |
|---|---|---:|---:|---:|---:|---:|
| deepseek-v4-pro_non-thinking | Direct | 8.2/8.0/11.0 | 0.0/0.0/0.0 | 8.2/8.0/11.0 | 878.5/586.5/2509.5 | 886.7/595.0/2518.2 |
| deepseek-v4-pro_non-thinking | Robust | 8.3/8.0/11.0 | 0.0/0.0/0.0 | 8.3/8.0/11.0 | 965.5/673.5/2596.5 | 973.9/682.0/2605.2 |
| deepseek-v4-pro_non-thinking | Ours | 38.7/32.0/48.0 | 0.0/0.0/0.0 | 38.7/32.0/48.0 | 1174.5/882.5/2805.5 | 1213.3/923.0/2840.5 |
| deepseek-v4-pro_thinking | Direct | 9.0/9.0/9.0 | 280.7/236.0/600.0 | 289.6/245.0/609.0 | 878.5/586.5/2509.5 | 1168.2/888.0/2888.0 |
| deepseek-v4-pro_thinking | Robust | 9.0/9.0/9.0 | 290.4/244.0/609.5 | 299.4/253.0/618.5 | 965.5/673.5/2596.5 | 1265.0/979.5/2984.0 |
| deepseek-v4-pro_thinking | Ours | 34.7/33.0/45.0 | 324.5/297.0/594.0 | 359.2/333.0/628.5 | 1174.5/882.5/2805.5 | 1533.8/1256.0/3221.2 |
| qwen3.5-9b_non-thinking | Direct | 7.1/7.0/7.0 | 0.0/0.0/0.0 | 7.1/7.0/7.0 | —/—/— | —/—/— |
| qwen3.5-9b_non-thinking | Robust | 7.0/7.0/7.0 | 0.0/0.0/0.0 | 7.0/7.0/7.0 | —/—/— | —/—/— |
| qwen3.5-9b_non-thinking | Ours | 36.2/31.0/46.0 | 0.0/0.0/0.0 | 36.2/31.0/46.0 | —/—/— | —/—/— |
| qwen3.5-9b_thinking | Direct | 7.0/7.0/7.0 | 1805.6/1190.0/3837.0 | 1812.5/1197.0/3844.0 | —/—/— | —/—/— |
| qwen3.5-9b_thinking | Robust | 7.0/7.0/7.0 | 1564.5/1246.0/3183.5 | 1571.5/1253.0/3190.5 | —/—/— | —/—/— |
| qwen3.5-9b_thinking | Ours | 32.2/31.0/43.2 | 1848.8/1530.5/3521.2 | 1881.0/1562.5/3554.8 | —/—/— | —/—/— |
| qwen3.5-35b-a3b_non-thinking | Direct | 10.8/11.0/11.0 | 0.0/0.0/0.0 | 10.8/11.0/11.0 | —/—/— | —/—/— |
| qwen3.5-35b-a3b_non-thinking | Robust | 10.2/11.0/11.0 | 0.0/0.0/0.0 | 10.2/11.0/11.0 | —/—/— | —/—/— |
| qwen3.5-35b-a3b_non-thinking | Ours | 37.7/31.0/49.0 | 0.0/0.0/0.0 | 37.7/31.0/49.0 | —/—/— | —/—/— |
| qwen3.5-35b-a3b_thinking | Direct | 7.0/7.0/7.0 | 1353.5/1115.5/3052.2 | 1360.5/1122.5/3059.2 | —/—/— | —/—/— |
| qwen3.5-35b-a3b_thinking | Robust | 7.0/7.0/7.0 | 1434.8/1166.0/3389.5 | 1441.8/1173.0/3396.5 | —/—/— | —/—/— |
| qwen3.5-35b-a3b_thinking | Ours | 30.8/31.0/44.0 | 2002.2/1558.5/4351.2 | 2032.9/1589.0/4385.2 | —/—/— | —/—/— |

## 可靠性与失败

失败记录没有从分类分母静默删除；分类统计对不可解析结果采用保守错误计分。
Qwen 本地结果未记录逐请求 API 成功字段，因此该列为 `—`，但所有冻结 prompt 均有返回记录。

| 配置 | 方法 | 记录数 | 请求成功率 | 格式有效率 | 无效输出 | 重试记录 | 最大尝试次数 | Finish reason |
|---|---|---:|---:|---:|---:|---:|---:|---|
| deepseek-v4-pro_non-thinking | Direct | 4956 | 100.00% | 100.00% | 0 | 0 | 1 | stop:4956 |
| deepseek-v4-pro_non-thinking | Robust | 4956 | 100.00% | 100.00% | 0 | 1 | 2 | stop:4956 |
| deepseek-v4-pro_non-thinking | Ours | 4956 | 100.00% | 100.00% | 0 | 0 | 1 | stop:4956 |
| deepseek-v4-pro_thinking | Direct | 4956 | 100.00% | 98.85% | 57 | 0 | 1 | length:9, stop:4947 |
| deepseek-v4-pro_thinking | Robust | 4956 | 100.00% | 99.27% | 36 | 0 | 1 | length:10, stop:4946 |
| deepseek-v4-pro_thinking | Ours | 4956 | 100.00% | 99.84% | 8 | 0 | 1 | length:6, stop:4950 |
| qwen3.5-9b_non-thinking | Direct | 4956 | — | 99.11% | 44 | 0 | — | stop:4956 |
| qwen3.5-9b_non-thinking | Robust | 4956 | — | 99.98% | 1 | 0 | — | stop:4956 |
| qwen3.5-9b_non-thinking | Ours | 4956 | — | 100.00% | 0 | 0 | — | stop:4956 |
| qwen3.5-9b_thinking | Direct | 4956 | — | 99.56% | 22 | 0 | — | length:22, stop:4934 |
| qwen3.5-9b_thinking | Robust | 4956 | — | 99.84% | 8 | 0 | — | length:8, stop:4948 |
| qwen3.5-9b_thinking | Ours | 4956 | — | 99.80% | 10 | 0 | — | length:9, stop:4947 |
| qwen3.5-35b-a3b_non-thinking | Direct | 4956 | — | 100.00% | 0 | 0 | — | stop:4956 |
| qwen3.5-35b-a3b_non-thinking | Robust | 4956 | — | 100.00% | 0 | 0 | — | stop:4956 |
| qwen3.5-35b-a3b_non-thinking | Ours | 4956 | — | 99.98% | 1 | 0 | — | stop:4956 |
| qwen3.5-35b-a3b_thinking | Direct | 4956 | — | 100.00% | 0 | 0 | — | stop:4956 |
| qwen3.5-35b-a3b_thinking | Robust | 4956 | — | 100.00% | 0 | 0 | — | stop:4956 |
| qwen3.5-35b-a3b_thinking | Ours | 4956 | — | 99.94% | 3 | 0 | — | length:3, stop:4953 |

## 可复现性说明

本报告完全由保留的逐请求 JSONL 重建，没有重新调用任何模型服务。机器可读完整结果包含 Flash 和全部方法。
