import sys
import os

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))
sys.stdout.reconfigure(encoding="utf-8")

from src.experiments.phase6_domain_evidence.domain_analyzer_v2 import (
    analyze_email_domains,
    format_domain_evidence_block,
)

test_cases = [
    {
        "name": "Sophisticated Phish 1 (Board VDR)",
        "subject": "Board of Directors: Q4 Executive Strategy Deck & Governance Briefing Materials",
        "sender": "board-secretary@enterprise-governance-vdr.com",
        "body": "Notice to Members of the Board... Access Secure Board Materials: https://enterprise-governance-vdr.com/vdr/board-q4",
    },
    {
        "name": "Sophisticated Phish 2 (Amex Travel)",
        "subject": "American Express Global Business Travel: Revised 2027 Corporate Lodging Per Diem Guidelines",
        "sender": "notifications@amex-businesstravel-portal.com",
        "body": "Corporate Travel Policy Notice... Concur travel profile... https://amex-businesstravel-portal.com/policy/perdiem-2027",
    },
    {
        "name": "Difficult Genuine 1 (Internal Compliance)",
        "subject": "MANDATORY ANNUAL COMPLIANCE: 2027 Code of Business Conduct Certification Deadline (Due Nov 15)",
        "sender": "compliance-officer@enterprise-corp.com",
        "body": "All Global Employees... log directly into https://learning.internal.enterprise-corp.com/course/compliance-2026",
    },
    {
        "name": "Difficult Genuine 2 (Legitimate DocuSign)",
        "subject": "DocuSign: Please sign Master Services Agreement - Q4 2026",
        "sender": "DocuSign System <dse@docusign.net>",
        "body": "Please review and sign the attached agreement: https://na3.docusign.net/Member/PowerFormSigning.aspx?Token=123",
    },
]

for tc in test_cases:
    print("=" * 60)
    print(f"TEST: {tc['name']}")
    analysis = analyze_email_domains(tc["subject"], tc["sender"], tc["body"])
    block = format_domain_evidence_block(analysis)
    print(block)

