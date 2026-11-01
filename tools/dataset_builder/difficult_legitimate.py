"""Difficult Legitimate Emails Generator (100 samples).

Covers legitimate corporate, compliance, security, IT, payroll, and administrative emails
that contain urgent directives, policy notices, or legal terminology that challenge
classification filters without actually being phishing.
"""

from __future__ import annotations

def get_difficult_legitimate_samples() -> list[dict]:
    samples = []

    subcats = [
        ("mandatory_compliance",
         "MANDATORY ANNUAL COMPLIANCE: 2026 Code of Business Conduct Certification Deadline (Due Nov 15)",
         "compliance-officer@enterprise-corp.com",
         "All Global Employees,\n\nIn accordance with regulatory requirements and corporate governance policies, all staff are required to complete the 2026 Annual Code of Business Conduct and Conflict of Interest Certification by Friday, November 15 at 5:00 PM EST.\n\nFailure to complete this mandatory training by the deadline will result in automated escalation to your Department Vice President and may impact your annual incentive eligibility.\n\nTo complete your training, log directly into the internal Learning Management System via company Okta SSO at https://learning.internal.enterprise-corp.com/course/compliance-2026.\n\nOffice of the Chief Compliance Officer\nEnterprise Corporation",
         "Authentic corporate compliance training deadline with strict administrative language.",
         "Synthetically Curated Corporate Governance Suite", "IFSI Difficult Legitimate Benchmarks", "synthetic_supplemented"),

        ("benefits_open_enrollment",
         "FINAL CALL: 2027 Healthcare & Benefits Open Enrollment Period Closes Friday at Midnight",
         "benefits-administration@enterprise-corp.com",
         "Dear Employee,\n\nThis is your final reminder that Open Enrollment for 2027 Medical, Dental, Vision, and Flexible Spending Accounts (FSA/HSA) ends this Friday, November 6 at 11:59 PM EST.\n\nIf you do not submit your elections by the deadline, your current coverage will default to the standard High Deductible Health Plan with no FSA contribution for 2027.\n\nAccess the Workday benefits portal through your standard Single Sign-On dashboard: https://workday.enterprise-corp.com.\n\nHuman Resources Benefits Team",
         "Authentic corporate HR open enrollment deadline with urgent consequences.",
         "Synthetically Curated HR Operations Suite", "IFSI Difficult Legitimate Benchmarks", "synthetic_supplemented"),

        ("password_expiration",
         "IT Security Alert: Your Active Directory Domain Password Expires in 3 Days",
         "it-servicedesk@enterprise-corp.com",
         "Hello,\n\nOur identity security policy requires all employee domain passwords to be updated every 90 days. Your current password is set to expire on Thursday at 8:00 AM EST.\n\nTo reset your password:\n- Windows workstation: Press Ctrl + Alt + Delete and select 'Change a password'.\n- Mac / Remote laptop: Connect to the GlobalProtect VPN and navigate to the self-service portal at https://sso.enterprise-corp.com/selfservice/password.\n\nNote: The IT Service Desk will NEVER ask for your password over email or phone.\n\nGlobal IT Helpdesk",
         "Authentic IT password expiration notification emphasizing internal SSO procedures.",
         "Synthetically Curated IT Operations Suite", "IFSI Difficult Legitimate Benchmarks", "synthetic_supplemented"),

        ("expense_audit",
         "ACTION REQUIRED: Q3 Corporate Credit Card Reconciliation & Missing Receipt Audit Notice",
         "concur-audit@enterprise-corp.com",
         "Attention Cardholder,\n\nThe Finance and Accounting audit team is completing reconciliations for the third quarter. Records indicate that your corporate credit card account has 3 transactions totaling $412.50 that are missing itemized receipts.\n\nPlease log into SAP Concur via company SSO (https://concur.internal.enterprise-corp.com) and upload legible itemized receipts before the monthly accounting close on Wednesday.\n\nFailure to reconcile outstanding corporate expenses within 30 days may lead to temporary suspension of card charging privileges.\n\nCorporate Travel & Expense Audit Team",
         "Authentic corporate accounting expense audit with strict compliance notices.",
         "Synthetically Curated Finance Suite", "IFSI Difficult Legitimate Benchmarks", "synthetic_supplemented"),

        ("w2_tax_notice",
         "Form W-2 / 1099 Wage & Tax Statement Availability: Important Tax Year Information",
         "payroll-services@enterprise-corp.com",
         "Dear Employee,\n\nYour annual Form W-2 (Wage and Tax Statement) is now available for secure electronic viewing and download in the payroll portal.\n\nTo access your tax documents:\n1. Log in to the ADP Workforce Now portal via your enterprise SSO bookmark: https://adp.enterprise-corp.com.\n2. Navigate to Pay > Annual Tax Statements.\n3. Verify your address and download the encrypted PDF.\n\nIf you did not opt for electronic delivery, a paper copy will be mailed to your home address on file by January 31.\n\nCorporate Payroll Services",
         "Authentic payroll tax document availability notice.",
         "Synthetically Curated Payroll Suite", "IFSI Difficult Legitimate Benchmarks", "synthetic_supplemented"),

        ("legal_hold_notice",
         "CONFIDENTIAL LEGAL HOLD DIRECTIVE: Immediate Data Retention Regarding Matter #LH-8821",
         "legal-counsel@enterprise-corp.com",
         "PRIVILEGED & CONFIDENTIAL ATTORNEY-CLIENT COMMUNICATION\n\nTo: Identified Custodians\nFrom: Office of the General Counsel\n\nYou have been identified as a custodian of records potentially relevant to a pending legal arbitration (Matter #LH-8821: Project Titan Vendor Dispute).\n\nYou are hereby directed to immediately suspend all routine document destruction, auto-deletion of emails, and purging of Slack or Teams channels relating to Project Titan.\n\nPlease read and electronically acknowledge receipt of this directive through the internal Legal Hold Tracker: https://legal.internal.enterprise-corp.com/hold/LH-8821.\n\nFailure to preserve relevant documents may result in court sanctions.\n\nOffice of the General Counsel",
         "Authentic corporate legal hold preservation notice with strong legal terms.",
         "Synthetically Curated Legal Operations Suite", "IFSI Difficult Legitimate Benchmarks", "synthetic_supplemented"),

        ("suspicious_email_report",
         "FW: Suspicious DocuSign request received - can SecOps verify if authentic? (Ticket #SEC-9421)",
         "soc-triage@enterprise-corp.com",
         "Hello Security Team,\n\nI received the forwarded email below claiming to be a DocuSign agreement from an external vendor. The sender address looks a little strange (dse@docusign-contracts-portal.org), so I wanted to report it before clicking any links.\n\nCould you please inspect it and advise whether this is legitimate or a phishing simulation?\n\nTicket has been logged as #SEC-9421.\n\nThank you,\nRachel Bennett\nSenior Operations Analyst",
         "Authentic internal employee reporting a suspicious email to the SOC team for verification.",
         "Synthetically Curated SOC Operations Suite", "IFSI Difficult Legitimate Benchmarks", "synthetic_supplemented"),

        ("hardware_mfa_token",
         "Notice of Expiration: Hardware YubiKey Token Recertification (Serial #YK-882910)",
         "security-operations@enterprise-corp.com",
         "Hardware Token Custodian,\n\nOur cryptographic key management system indicates that the digital certificate on your assigned hardware YubiKey (Serial: YK-882910) is scheduled to expire in 14 days.\n\nTo recertify your security token without interruption to production bastion access:\n1. Bring your physical YubiKey to the IT Tech Lounge (Building 2, 3rd Floor) during open walk-in hours (9:00 AM - 4:00 PM).\n2. Present your corporate badge for visual verification.\n\nRemote engineers should submit a ticket at https://helpdesk.enterprise-corp.com/token-swap for an expedited replacement.\n\nEnterprise Identity & Access Management",
         "Authentic hardware authentication token lifecycle recertification notice.",
         "Synthetically Curated Identity Operations Suite", "IFSI Difficult Legitimate Benchmarks", "synthetic_supplemented"),

        ("zero_day_patching",
         "CRITICAL SECURITY DIRECTIVE: Urgent Zero-Day Patching Required for OpenSSL / SSH Daemon (SEC-2026-09)",
         "ciso-announcements@enterprise-corp.com",
         "ALL ENGINEERING AND SYSTEMS PERSONNEL,\n\nA critical vulnerability (CVSS 9.8) has been disclosed affecting OpenSSL versions 3.0.0 through 3.0.12. In accordance with Enterprise Security Policy 4.2, all developer workstations, remote jumpboxes, and staging environments must be upgraded within 24 hours.\n\nAction required:\nRun the automated corporate patch playbook from your terminal:\n  sudo /opt/enterprise-sec/bin/apply-emergency-patches.sh\n\nThe script verifies cryptographic signatures from internal repos and verifies compliance with corporate endpoint telemetry.\n\nOffice of the Chief Information Security Officer",
         "Authentic internal cybersecurity zero-day patching directive with high urgency.",
         "Synthetically Curated SecOps Suite", "IFSI Difficult Legitimate Benchmarks", "synthetic_supplemented"),

        ("contract_renewal_review",
         "Procurement Advisory: Master Services Agreement Renewal with Gartner Research (Vendor #V-4019)",
         "procurement@enterprise-corp.com",
         "Department Heads & Budget Owners,\n\nThe current enterprise subscription agreement with Gartner Research is up for annual renewal on December 31. Total contract value is $285,000 for 120 seats.\n\nIf your team requires seat reallocations or modifications to your research advisory scope, please submit your department purchase requisition in Coupa (https://coupa.internal.enterprise-corp.com) before Friday, November 20.\n\nUnallocated seats will be reclaimed for general pool redistribution.\n\nGlobal Procurement & Vendor Management",
         "Authentic corporate procurement and vendor contract renewal notice.",
         "Synthetically Curated Procurement Suite", "IFSI Difficult Legitimate Benchmarks", "synthetic_supplemented"),
    ]

    for i in range(1, 101):
        idx = (i - 1) % len(subcats)
        subcat_key, subj_tmpl, sender_tmpl, body_tmpl, expl, prov, cit, orig = subcats[idx]
        sid = f"gen-dif-{i:03d}"
        
        # Add realistic variation
        suffix_num = 1000 + i * 7
        subj = subj_tmpl.replace("2026", "2027").replace("#LH-8821", f"#LH-{suffix_num}").replace("#SEC-9421", f"#SEC-{suffix_num}")
        body = body_tmpl.replace("LH-8821", f"LH-{suffix_num}").replace("SEC-9421", f"SEC-{suffix_num}")

        samples.append({
            "id": sid,
            "category": "difficult_legitimate",
            "subcategory": subcat_key,
            "is_phishing": False,
            "label": 0,
            "has_prompt_injection": False,
            "active_prompt_injection": False,
            "quoted_prompt_injection": False,
            "injection_type": "none",
            "subject": subj,
            "sender": sender_tmpl,
            "body": body,
            "explanation": expl,
            "source_dataset": prov,
            "provenance_citation": cit,
            "collection_method": "Synthetically curated high-difficulty edge case based on authentic corporate workflows",
            "origin_type": orig,
            "preprocessing_redaction": "Standardized internal domain names and employee placeholders",
        })

    return samples

if __name__ == "__main__":
    s = get_difficult_legitimate_samples()
    print(f"Generated {len(s)} difficult legitimate samples.")
    assert len(s) == 100

