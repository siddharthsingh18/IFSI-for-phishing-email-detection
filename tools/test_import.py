import sys
import os

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

try:
    from src.experiments.phase6_domain_evidence.engine_v3 import classify_email_phase6
    print("Import SUCCESS!")
except Exception as e:
    import traceback
    traceback.print_exc()

