# Dataset acquisition and provenance

Raw email corpora are intentionally not downloaded by the repository and are
not redistributed by default. Put each source at the documented local path,
then use the parser `--check` mode and compare the recorded SHA-256 before
parsing. The common parser schema is:
`{id,text,label,source,family?,raw_sha256,original_path}`. IDs are SHA-256
hashes of normalized message text and are stable across parser runs.

| Source | Role | Origin / expected local location | Format | License / redistribution |
|---|---|---|---|---|
| Enron | legit | https://www.cs.cmu.edu/~enron/ ; `data/raw/enron/` | mbox/maildir | Original corpus terms; verify; redistribution: no |
| SpamAssassin ham | legit | https://spamassassin.apache.org/old/publiccorpus/ ; `data/raw/spamassassin/{easy_ham,hard_ham}/` | tar.gz / RFC822 | Original sender copyrights; live-system warning; verify; redistribution: no |
| Nazario | phishing | https://monkey.org/~jose/phishing/ ; `data/raw/nazario/phishing3.mbox` | mbox | Source terms; verify; redistribution: no |
| Nigerian fraud | phishing/fraud | CLAIR/Yale Nigerian Fraud corpus; `data/raw/nigerian_fraud/` | mbox | Access-gated/source terms; verify; redistribution: no |
| EPVME | malicious/adversarial | local acquisition under `~/Downloads/EPVME-Dataset-main/` | `.eml` tree | GPL-3.0 package plus embedded-source terms; verify; redistribution: no |
| IWSPA synthetic | malicious/adversarial | local acquisition under `~/Downloads/IWSPA-2023-Adversarial-Synthetic-Dataset-main/Synthetic/` | CSV | Dataset terms; verify; redistribution: no |
| IWSPA adversarial | both labels/adversarial | local acquisition under `~/Downloads/IWSPA-2023-Adversarial-Synthetic-Dataset-main/Adversarial/` | CSV | Dataset terms; verify; redistribution: no |

The EPVME folder names are retained as `family` labels. When a source provides
explicit family or template tags, parsers preserve them; otherwise the parser
uses the immediate directory name and records the original path. EPVME
fingerprints for split grouping are derived from `(family, payload fingerprint,
header-scaffold fingerprint)` so generated variants stay together.

## Local findings

At the time of this audit, EPVME and IWSPA were present under `~/Downloads`.
Two untracked copies of `phishing3.mbox` were present under `~/Downloads`;
the repository root did not contain a tracked copy. No files were deleted.

If a tracked raw mbox is ever found, print and review the following history
rewrite commands rather than running them automatically:

```bash
git filter-repo --path phishing3.mbox --path data/raw/ --invert-paths
git push --force-with-lease origin main
```

History rewriting changes commit IDs and requires coordination with every
clone. This repository currently ignores `*.mbox`, `*.eml`, and `data/`.
