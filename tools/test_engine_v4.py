import sys
sys.path.insert(0, "src")
import time

print("Importing engine_v4...")
t0 = time.time()
from experiments.phase7_domain_precision.engine_v4 import classify_email_phase7
print(f"Import succeeded in {time.time() - t0:.2f}s")

sample_email = """From: HR Department <payroll@company.com>
Subject: Direct Deposit Update
Date: Mon, 12 Oct 2026 10:00:00 +0000

Please verify your direct deposit information by visiting your internal HR portal.
"""

print("Running Config B inference test...")
t1 = time.time()
res_b = classify_email_phase7(sample_email, config_id="B")
print(f"Config B completed in {time.time() - t1:.2f}s: verdict={res_b['verdict']}, action={res_b['security_action']}")
print("All checks passed.")

