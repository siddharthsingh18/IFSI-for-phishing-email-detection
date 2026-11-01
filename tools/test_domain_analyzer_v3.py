import sys
import os

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))
sys.stdout.reconfigure(encoding="utf-8")

from src.experiments.phase7_domain_precision.domain_analyzer_v3 import (
    analyze_email_domains_v3,
    format_domain_evidence_block_v3,
)

test_cases = [
    {
        "id": "gen-ord-010 (Amazon Business)",
        "subject": "Your Amazon Business order #114-8829102 has shipped",
        "sender": "auto-confirm@amazon-business.com",
        "body": "Hello, Your order of 4x Ergotron Dual-Monitor Arms has shipped via UPS Ground. Delivery Address: Suite 400. Thank you for shopping with Amazon Business.",
    },
    {
        "id": "p6-leg-007 (Internal Concur Expense)",
        "subject": "SAP Concur: Expense Report #ER-4491 Approved for Payment",
        "sender": "concur-travel@enterprise-corp.com",
        "body": "Attention Employee, Your travel report has been approved. Review payment advice: https://concur.internal.enterprise-corp.com/reimbursement/ER-4491",
    },
    {
        "id": "p6-leg-015 (Workday HCM Payslip)",
        "subject": "Workday: Your Monthly Payslip is Ready for Review",
        "sender": "Workday Notifications <notifications@workday.com>",
        "body": "Your payslip for the pay period ending Oct 31 is now available in Workday. View payslip: https://www.myworkday.com/enterprise-corp/login.htmld",
    },
    {
        "id": "gen-sop-007 (Sophisticated Phish: Board VDR)",
        "subject": "Board of Directors: Q4 Executive Strategy Deck & Governance Briefing Materials",
        "sender": "board-secretary@enterprise-governance-vdr.com",
        "body": "Notice to Members of the Board: The preparatory materials have been uploaded. Access Secure Board Materials: https://enterprise-governance-vdr.com/vdr/board-q4",
    },
    {
        "id": "gen-sop-009 (Sophisticated Phish: Amex GBT)",
        "subject": "American Express Global Business Travel: Revised 2027 Corporate Lodging Per Diem Guidelines",
        "sender": "notifications@amex-businesstravel-portal.com",
        "body": "Corporate Travel Policy Notice: Enterprise Corporation and Amex GBT implement revised per diems: https://amex-businesstravel-portal.com/policy/perdiem-2027",
    },
]

for tc in test_cases:
    print("=" * 75)
    print(f"TEST CASE: {tc['id']}")
    print("=" * 75)
    analysis = analyze_email_domains_v3(tc["subject"], tc["sender"], tc["body"])
    block = format_domain_evidence_block_v3(analysis)
    print(block)

