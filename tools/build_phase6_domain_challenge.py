"""Build Phase 6 Domain Challenge Dataset (40 focused samples).

Categories:
- 20 Sophisticated Phishing (domain lookalikes, chained administrative keywords,
  display-name spoofing, reply-to discrepancies, synthetic vendor portals).
- 20 Difficult Legitimate (genuine enterprise multi-tenant SaaS, legitimate
  third-party vendors, legitimate hyphenated corporate domains, genuine subdomains).

Ensures:
- Deterministic, standardized JSONL format.
- Zero lexical or hash overlap with FAISS index or previous benchmark suites.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

OUTPUT_PATH = Path("data/evaluation/phase6_domain_challenge.jsonl")

# 20 Sophisticated Phishing Samples
SOPHISTICATED_PHISHING = [
    {
        "id": "p6-sop-001",
        "category": "sophisticated_phishing",
        "subcategory": "executive_vdr_lookalike",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Confidential: Q1 M&A Acquisition Committee Strategy Document",
        "sender": "ma-committee@corporate-strategy-vdr.com",
        "body": (
            "Senior Leadership Team,\n\n"
            "The confidential evaluation metrics for Project Titan have been published to the Virtual Data Room.\n\n"
            "Please review the projected synergy analysis and submit your voting feedback prior to tomorrow's executive session:\n"
            "https://corporate-strategy-vdr.com/vdr/project-titan-review\n\n"
            "Access requires authentication using your corporate identity provider credentials.\n\n"
            "M&A Strategy & Corporate Development"
        ),
        "explanation": "Executive spear-phishing utilizing synthetic hyphenated VDR domain with administrative pretext.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-sop-002",
        "category": "sophisticated_phishing",
        "subcategory": "hr_benefits_portal_lookalike",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Action Required: Complete Your 2027 Open Enrollment Election Changes",
        "sender": "benefits@enterprise-benefits-portal.net",
        "body": (
            "All Eligible Employees,\n\n"
            "The annual Open Enrollment period for medical, dental, and life insurance benefits concludes this Friday at midnight.\n\n"
            "To confirm your benefit elections and designate primary beneficiaries, access the enrollment portal:\n"
            "https://enterprise-benefits-portal.net/auth/enrollment-2027\n\n"
            "Unconfirmed elections will default to standard baseline coverage.\n\n"
            "Corporate Benefits & Total Rewards"
        ),
        "explanation": "HR benefits credential harvesting lure on a synthetic hyphenated .net domain.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-sop-003",
        "category": "sophisticated_phishing",
        "subcategory": "brand_lookalike_docusign",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "DocuSign: Please review and sign Vendor Master Agreement 2027",
        "sender": "DocuSign System <envelope-notification@docusign-envelope-review.com>",
        "body": (
            "DocuSign Document Notification\n\n"
            "Enterprise Procurement has sent you a document for electronic signature:\n"
            "Vendor Master Services Agreement (MSA) - Amendment 4.\n\n"
            "Review Document:\n"
            "https://docusign-envelope-review.com/signing/doc-89421\n\n"
            "This envelope will expire in 48 hours.\n\n"
            "Do Not Share This Email. This email contains a secure link to DocuSign."
        ),
        "explanation": "DocuSign brand lookalike typosquat domain embedding brand name with hyphenated words.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-sop-004",
        "category": "sophisticated_phishing",
        "subcategory": "brand_lookalike_zoom",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Zoom Meeting: Audio/Video Infrastructure Firmware Update Required",
        "sender": "Zoom Support <admin@zoom-meeting-secure.com>",
        "body": (
            "Dear User,\n\n"
            "A critical client security patch is required to continue hosting encrypted corporate webinars.\n\n"
            "Authenticate your Zoom Enterprise account and update your credentials here:\n"
            "https://zoom-meeting-secure.com/webinar/client-patch\n\n"
            "Failure to update may result in temporary meeting disconnection.\n\n"
            "Zoom Cloud Video Communications"
        ),
        "explanation": "Impersonation of Zoom using synthetic hyphenated brand lookalike domain.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-sop-005",
        "category": "sophisticated_phishing",
        "subcategory": "brand_lookalike_microsoft",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Microsoft 365: Mandatory Multi-Factor Session Key Re-authentication",
        "sender": "Microsoft Security Team <security-notice@microsoft-account-verify.net>",
        "body": (
            "Microsoft 365 Security Alert\n\n"
            "Unusual sign-in activity was detected on your account from an unverified IP address.\n\n"
            "To safeguard your corporate inbox and OneDrive files, re-verify your identity immediately:\n"
            "https://microsoft-account-verify.net/auth/session-validate\n\n"
            "Microsoft Security Operations Center"
        ),
        "explanation": "Microsoft 365 credential phishing utilizing a synthetic hyphenated .net lookalike domain.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-sop-006",
        "category": "sophisticated_phishing",
        "subcategory": "payroll_adp_lookalike",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "ADP TotalSource: Revised Year-End Tax Withholding Statement W-2",
        "sender": "tax-services@adp-payroll-portal.org",
        "body": (
            "Attention Employee,\n\n"
            "Your revised 2026 Form W-2 Wage and Tax Statement is now available for download.\n\n"
            "Log in to ADP TotalSource to verify your address and retrieve your tax documentation:\n"
            "https://adp-payroll-portal.org/tax/w2-download\n\n"
            "ADP, Inc. Automated Tax Notification"
        ),
        "explanation": "ADP brand impersonation with hyphenated administrative keywords on .org TLD.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-sop-007",
        "category": "sophisticated_phishing",
        "subcategory": "reply_to_mismatch_invoice",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Updated Remittance Advice: Outstanding Q4 Cloud Architecture Billing",
        "sender": "accounting@enterprise-cloud-consulting.com",
        "body": (
            "From: accounting@enterprise-cloud-consulting.com\n"
            "Reply-To: external-billing-desk@inbox-route.net\n\n"
            "Dear Finance Department,\n\n"
            "Please find attached our updated remittance schedule for milestone invoice #INV-8821.\n"
            "Due to an annual banking audit, our receiving bank details have been transferred.\n\n"
            "Please reply directly to this email or review the payment authorization here:\n"
            "https://enterprise-cloud-consulting.com/billing/revised-invoice\n\n"
            "Accounts Receivable Team"
        ),
        "explanation": "BEC invoice redirection with subtle Reply-To header mismatch routing replies to external inbox.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-sop-008",
        "category": "sophisticated_phishing",
        "subcategory": "display_name_spoof_ceo",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Urgent Discretionary Wire Assistance Needed (Confidential)",
        "sender": "\"David Miller (CEO)\" <executive-office-briefing@corporate-mail-gateway.net>",
        "body": (
            "Are you at your desk right now?\n\n"
            "I am currently in an offsite board negotiation and need an urgent, confidential wire transfer processed for an international retainer.\n\n"
            "Do not call my office line as I cannot take calls. Reply directly with your availability so I can forward the bank swift particulars.\n\n"
            "David Miller\nChief Executive Officer"
        ),
        "explanation": "Executive display-name spoofing paired with disposable synthetic corporate gateway domain.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-sop-009",
        "category": "sophisticated_phishing",
        "subcategory": "concur_expense_lookalike",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Concur Solutions: Expense Report #ER-7719 Rejected - Immediate Action Needed",
        "sender": "notifications@concur-travel-expense.net",
        "body": (
            "Your recent corporate expense submission #ER-7719 has been flagged by automated compliance for missing VAT documentation.\n\n"
            "To resolve the exception and prevent reimbursement delays, upload the missing receipts:\n"
            "https://concur-travel-expense.net/reports/er-7719-resolve\n\n"
            "SAP Concur Expense Operations"
        ),
        "explanation": "SAP Concur lookalike domain chaining brand name with travel/expense keywords.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-sop-010",
        "category": "sophisticated_phishing",
        "subcategory": "okta_identity_lookalike",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Okta SSO: Multi-Device Push Notification Security Sync",
        "sender": "Okta Identity Team <security@okta-verify-gateway.com>",
        "body": (
            "Okta Identity Cloud Notification\n\n"
            "An expired OAuth certificate requires immediate endpoint synchronization on your trusted corporate laptop.\n\n"
            "Re-authenticate through the secure single sign-on gateway:\n"
            "https://okta-verify-gateway.com/sso/device-sync\n\n"
            "Failure to synchronize within 24 hours will revoke SSO access to corporate applications.\n\n"
            "Enterprise Identity Administration"
        ),
        "explanation": "Okta brand impersonation utilizing synthetic hyphenated gateway domain.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-sop-011",
        "category": "sophisticated_phishing",
        "subcategory": "legal_subpoena_lookalike",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "CONFIDENTIAL LEGAL NOTICE: Subpoena Duces Tecum in re Civil Litigation",
        "sender": "litigation-service@federal-court-notices.org",
        "body": (
            "Notice of Legal Service\n\n"
            "You are hereby served with a formal deposition notice and document preservation demand regarding Case No. 26-CV-9912.\n\n"
            "To download and acknowledge receipt of the encrypted legal filing, access the certified clerk portal:\n"
            "https://federal-court-notices.org/filings/case-9912\n\n"
            "Failure to respond may result in an immediate default judgment.\n\n"
            "Clerk of Court Judicial Notices"
        ),
        "explanation": "Legal pretexting spear-phish using deceptive synthetic public-sector lookalike domain.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-sop-012",
        "category": "sophisticated_phishing",
        "subcategory": "internal_it_helpdesk_lookalike",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "IT Service Desk: Mandatory Ticket Resolution for Inactive Mailbox Archival",
        "sender": "helpdesk@corporate-servicedesk-portal.com",
        "body": (
            "Enterprise IT Infrastructure Notice\n\n"
            "Your corporate email box has exceeded 95% storage capacity and will be queued for automated purge.\n\n"
            "To retain your mailbox and extend cloud retention quotas, confirm your account active status:\n"
            "https://corporate-servicedesk-portal.com/helpdesk/quota-extend\n\n"
            "Global IT Service Operations"
        ),
        "explanation": "IT quota spear-phish leveraging synthetic corporate service desk hyphenated domain.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-sop-013",
        "category": "sophisticated_phishing",
        "subcategory": "quickbooks_invoice_lookalike",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Intuit QuickBooks: Overdue Invoice Notification #QB-1094",
        "sender": "quickbooks-billing@quickbooks-vendorpay.net",
        "body": (
            "Invoice Alert from Intuit QuickBooks\n\n"
            "Invoice #QB-1094 from Apex Commercial Logistics is past due in the amount of $4,820.00.\n\n"
            "View and pay invoice online:\n"
            "https://quickbooks-vendorpay.net/invoices/pay-1094\n\n"
            "Powered by Intuit QuickBooks Merchant Services"
        ),
        "explanation": "Intuit QuickBooks financial phishing lure on a synthetic .net domain.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-sop-014",
        "category": "sophisticated_phishing",
        "subcategory": "salesforce_crm_lookalike",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Salesforce: Inbound Lead Reassignment & Pipeline Access Suspended",
        "sender": "admin@salesforce-pipeline-auth.com",
        "body": (
            "Sales Operations Alert\n\n"
            "Your Salesforce API access token has expired due to non-usage over the past 30 days.\n\n"
            "Re-activate your CRM pipeline permissions:\n"
            "https://salesforce-pipeline-auth.com/oauth/renew-token\n\n"
            "Enterprise CRM Administration"
        ),
        "explanation": "Salesforce brand impersonation using chained brand and authentication keywords.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-sop-015",
        "category": "sophisticated_phishing",
        "subcategory": "dhl_shipping_lookalike",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "DHL Express: Customs Clearance Fee Required for Package #DHL-991823",
        "sender": "tracking@dhl-express-customs.org",
        "body": (
            "Shipment Exception Notification\n\n"
            "Your international package #DHL-991823 has arrived at the regional customs depot but requires customs duty clearance of $18.45.\n\n"
            "Pay fee and schedule delivery:\n"
            "https://dhl-express-customs.org/clearance/pay-fee\n\n"
            "DHL Express International Dispatch"
        ),
        "explanation": "DHL shipping notification lure with lookalike .org domain embedding brand and customs keywords.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-sop-016",
        "category": "sophisticated_phishing",
        "subcategory": "compensation_committee_memo",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Executive Compensation Committee: 2027 Long-Term Equity Incentive Grant",
        "sender": "comp-committee@exec-talent-advisory.com",
        "body": (
            "Confidential Memorandum to Executive Vice Presidents,\n\n"
            "The Board Compensation Committee has finalized your 2027 Performance Stock Unit (PSU) allocation schedules.\n\n"
            "Please review the vesting criteria and execute your equity grant agreement:\n"
            "https://exec-talent-advisory.com/grants/psu-2027-election\n\n"
            "Corporate Governance & Equity Administration"
        ),
        "explanation": "Targeted executive equity incentive pretexting on synthetic advisory domain.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-sop-017",
        "category": "sophisticated_phishing",
        "subcategory": "external_culture_audit",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Anonymous Workplace Culture & Leadership Integrity Assessment (Mandatory)",
        "sender": "survey-director@workplace-culture-audit.org",
        "body": (
            "Dear Colleague,\n\n"
            "As commissioned by the Board of Directors, an independent evaluation of leadership transparency is currently underway.\n\n"
            "Your responses are 100% confidential and aggregated externally. Access your personal survey token:\n"
            "https://workplace-culture-audit.org/survey/auth-token-4421\n\n"
            "Independent Workplace Evaluation Institute"
        ),
        "explanation": "Credential harvesting under the guise of an external third-party organizational culture audit.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-sop-018",
        "category": "sophisticated_phishing",
        "subcategory": "cloud_procurement_renewal",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "AWS Cloud Services: Master Infrastructure Agreement Annual Renewal",
        "sender": "procurement-desk@cloud-enterprise-billing.net",
        "body": (
            "Enterprise Procurement Alert\n\n"
            "Your AWS Enterprise Cloud Infrastructure agreement will auto-renew on the 1st of next month.\n\n"
            "To review current compute discount schedules and verify designated billing authority:\n"
            "https://cloud-enterprise-billing.net/contracts/aws-renewal-2027\n\n"
            "Global IT Vendor Management Office"
        ),
        "explanation": "Enterprise IT vendor management lure using synthetic hyphenated billing domain.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-sop-019",
        "category": "sophisticated_phishing",
        "subcategory": "travel_itinerary_amex_lookalike",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "American Express GBT: Urgent Flight Schedule Modification Notice",
        "sender": "itinerary-alerts@amextravel-corporate.com",
        "body": (
            "Flight Schedule Notice\n\n"
            "Your upcoming outbound business flight itinerary from JFK to LHR has experienced an equipment schedule alteration.\n\n"
            "Review your updated seat assignment and confirm connection timings:\n"
            "https://amextravel-corporate.com/itinerary/reconfirm-seat\n\n"
            "American Express Global Business Travel Support"
        ),
        "explanation": "American Express GBT travel itinerary lure on synthetic amextravel lookalike domain.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-sop-020",
        "category": "sophisticated_phishing",
        "subcategory": "cross_domain_redirect_harvest",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Shared Document: Project Horizon Financial Model v4.xlsx",
        "sender": "colleague@reputable-partner-consulting.com",
        "body": (
            "Hi team,\n\n"
            "I have uploaded the finalized cash flow model for Project Horizon.\n\n"
            "Please review the model assumptions before our client sync:\n"
            "https://external-auth-gateway.net/files/project-horizon-model\n\n"
            "Let me know if you have questions.\n\n"
            "Senior Financial Analyst"
        ),
        "explanation": "Phishing email where sender domain appears normal but destination link directs to deceptive auth gateway.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
]

# 20 Difficult Legitimate Samples
DIFFICULT_LEGITIMATE = [
    {
        "id": "p6-leg-001",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_docusign_system",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "DocuSign: Please DocuSign Master Non-Disclosure Agreement",
        "sender": "\"DocuSign System\" <dse@docusign.net>",
        "body": (
            "DocuSign\n\n"
            "Legal Counsel has sent you a document to review and sign.\n\n"
            "Please review the attached Mutual Non-Disclosure Agreement:\n"
            "https://na2.docusign.net/Member/PowerFormSigning.aspx?PowerFormId=a12-8812\n\n"
            "DocuSign, Inc. | The Global Standard for Electronic Signature"
        ),
        "explanation": "Authentic transactional notification from DocuSign utilizing legitimate docusign.net domain.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-leg-002",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_greenhouse_recruiting",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Interview Confirmation: Staff Security Engineer Candidate Interview",
        "sender": "Enterprise Recruiting <no-reply@greenhouse.io>",
        "body": (
            "Hi Alex,\n\n"
            "Your upcoming technical panel interview with candidate Jordan Taylor is scheduled for Thursday at 2:00 PM EST.\n\n"
            "Please review the candidate's resume and prepare your interview scorecard beforehand:\n"
            "https://app.greenhouse.io/scorecards/interview-99214\n\n"
            "Thank you,\n"
            "Global Talent Acquisition"
        ),
        "explanation": "Authentic recruiting scorecard notification linking to legitimate Greenhouse SaaS platform.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-leg-003",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_zoom_calendar_invite",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Zoom Meeting Invitation: Q1 Product Roadmap & Architectural Review",
        "sender": "no-reply@zoom.us",
        "body": (
            "Hi there,\n\n"
            "Marcus Wright is inviting you to a scheduled Zoom meeting.\n\n"
            "Topic: Q1 Product Roadmap & Architectural Review\n"
            "Time: Nov 12, 2026 10:00 AM Eastern Time (US and Canada)\n\n"
            "Join Zoom Meeting:\n"
            "https://zoom.us/j/98124018274?pwd=QUFMZ0tSWHJLNnp5a3R5\n\n"
            "Meeting ID: 981 2401 8274\n\n"
            "Zoom Video Communications"
        ),
        "explanation": "Authentic calendar invitation from legitimate Zoom infrastructure domain.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-leg-004",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_okta_access_request",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Okta Access Request: Privilege Escalation Approved for Production Database",
        "sender": "Okta Identity System <system@enterprise-corp.okta.com>",
        "body": (
            "Okta Access Gateway\n\n"
            "Your temporary read-only access request for the EMEA Production Analytics database has been approved by your manager.\n\n"
            "Access is valid for 4 hours. You can review your active sessions in the Okta portal:\n"
            "https://enterprise-corp.okta.com/app/UserHome\n\n"
            "Corporate Identity & Access Governance"
        ),
        "explanation": "Authentic Okta enterprise multi-tenant subdomain notification.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-leg-005",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_salesforce_case_update",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Case #0049129 Update: Enterprise Customer Escalation Resolved",
        "sender": "Support Escalations <support@salesforce.com>",
        "body": (
            "Hello Technical Support Team,\n\n"
            "Customer Premier Support Case #0049129 has been updated with resolution notes from the core engineering team.\n\n"
            "View case details in Service Cloud:\n"
            "https://login.salesforce.com/cases/0049129\n\n"
            "Salesforce Customer Success"
        ),
        "explanation": "Authentic enterprise CRM ticket update on verified salesforce.com domain.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-leg-006",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_internal_subdomain_lms",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Compliance Notice: Complete Annual Insider Trading Training by Friday",
        "sender": "legal-compliance@enterprise-corp.com",
        "body": (
            "All Corporate Personnel,\n\n"
            "The mandatory Q4 Insider Trading and Material Non-Public Information (MNPI) compliance module is due this Friday.\n\n"
            "Complete your training via corporate single sign-on:\n"
            "https://learning.internal.enterprise-corp.com/course/insider-trading-2026\n\n"
            "Legal & Corporate Governance Department"
        ),
        "explanation": "Authentic corporate training reminder linking to internal corporate subdomain.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-leg-007",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_concur_subdomain",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "SAP Concur: Expense Report #ER-4491 Approved for Payment",
        "sender": "concur-travel@enterprise-corp.com",
        "body": (
            "Attention Employee,\n\n"
            "Your travel and lodging expense report for the London Technical Summit has been approved by your department director.\n\n"
            "Reimbursement will be deposited to your primary direct deposit account in 3-5 business days.\n\n"
            "Review payment advice: https://concur.internal.enterprise-corp.com/reimbursement/ER-4491\n\n"
            "Corporate Finance Operations"
        ),
        "explanation": "Authentic internal corporate expense notification on verified company infrastructure.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-leg-008",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_hyphenated_brand_domain",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "ServiceNow Incident #INC09941 Assigned to Enterprise Architecture",
        "sender": "ServiceDesk <it-notifications@service-now.com>",
        "body": (
            "Incident INC09941 has been assigned to your operational queue.\n\n"
            "Short Description: High CPU utilization on Kafka ingestion broker cluster 04.\n"
            "Priority: 2 - High\n\n"
            "View and accept incident in ServiceNow:\n"
            "https://enterprise.service-now.com/nav_to.do?uri=incident.do?sys_id=INC09941\n\n"
            "ServiceNow Automated Notifications"
        ),
        "explanation": "Legitimate enterprise SaaS notification from service-now.com (standard hyphenated SaaS brand).",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-leg-009",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_github_security_alert",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "[GitHub] Dependabot Alert: High Severity Vulnerability in package axios",
        "sender": "GitHub Notifications <notifications@github.com>",
        "body": (
            "We found a potential security vulnerability in your repository enterprise-corp/core-api.\n\n"
            "Vulnerability: Regular Expression Denial of Service (ReDoS) in axios < 1.7.4\n\n"
            "View Dependabot alert and automated pull request:\n"
            "https://github.com/enterprise-corp/core-api/security/dependabot/12\n\n"
            "GitHub Security Team"
        ),
        "explanation": "Authentic Dependabot vulnerability notification on official github.com domain.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-leg-010",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_external_legal_counsel",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Privileged & Confidential: Q4 Intellectual Property Portfolio Review",
        "sender": "sarah.jenkins@lw-legalpartners.com",
        "body": (
            "Dear Enterprise Corporation Legal Team,\n\n"
            "Attached for your review is our quarterly patent docket status summary.\n"
            "We have secured notice of allowance for your distributed ledger patent applications.\n\n"
            "Please let us know your availability for our scheduled patent committee call next Tuesday.\n\n"
            "Sarah Jenkins, Partner\n"
            "Latham & Watkins Legal Partners LLP"
        ),
        "explanation": "Authentic cross-firm communication from outside corporate legal counsel without links.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-leg-011",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_concursolutions_authorized",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Concur Travel: Electronic Ticket Confirmation & Airline Confirmation Code",
        "sender": "Concur Travel <travel-confirmations@concursolutions.com>",
        "body": (
            "Your corporate flight reservation has been ticketed successfully.\n\n"
            "Passenger: Alex Chen\n"
            "Flight: United Airlines UA 884 (SFO -> ORD)\n"
            "Record Locator: Z7X99P\n\n"
            "View and manage itinerary details:\n"
            "https://www.concursolutions.com/travel/itinerary?rec=Z7X99P\n\n"
            "SAP Concur Travel Services"
        ),
        "explanation": "Authentic travel confirmation on SAP Concur's official secondary domain concursolutions.com.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-leg-012",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_zendesk_support",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "[Request #882194] Corporate Laptop Battery Replacement Request Received",
        "sender": "Enterprise IT Support <support@enterprise-corp.zendesk.com>",
        "body": (
            "Your IT support ticket #882194 has been received by our desktop hardware depot.\n\n"
            "A technician will reach out within 24 hours to schedule hardware drop-off.\n\n"
            "Track your ticket progress:\n"
            "https://enterprise-corp.zendesk.com/hc/requests/882194\n\n"
            "Enterprise Desktop Support"
        ),
        "explanation": "Authentic IT support ticketing notification using legitimate Zendesk SaaS subdomain.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-leg-013",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_slack_workspace_invite",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Elena Rostova invited you to join the #ai-architecture channel on Slack",
        "sender": "Slack <notification@slack.com>",
        "body": (
            "Join your team on Slack!\n\n"
            "Elena Rostova (elena@enterprise-corp.com) invited you to collaborate in #ai-architecture.\n\n"
            "Accept invitation and open Slack:\n"
            "https://enterprise-corp.slack.com/messages/ai-architecture\n\n"
            "Slack Technologies, LLC"
        ),
        "explanation": "Authentic collaboration invite on official slack.com domain.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-leg-014",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_atlassian_jira_mention",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "[Jira] (PROD-4091) David Vance mentioned you on an issue",
        "sender": "Jira Notifications <jira@enterprise-corp.atlassian.net>",
        "body": (
            "David Vance mentioned you on PROD-4091 (Upgrade Postgres Cluster to 16.2):\n\n"
            "\"@Alex can you review the connection pool timeout values before the cutover this weekend?\"\n\n"
            "View and respond in Jira:\n"
            "https://enterprise-corp.atlassian.net/browse/PROD-4091\n\n"
            "Atlassian Cloud Services"
        ),
        "explanation": "Authentic project management notification on verified Atlassian multi-tenant domain.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-leg-015",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_workday_official_domain",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Workday: Your Monthly Payslip is Ready for Review",
        "sender": "Workday Notifications <notifications@workday.com>",
        "body": (
            "Your payslip for the pay period ending October 31, 2026 is now available in Workday.\n\n"
            "View payslip and tax withholding details:\n"
            "https://www.myworkday.com/enterprise-corp/login.htmld\n\n"
            "Workday Human Capital Management"
        ),
        "explanation": "Authentic HR payroll notification on official Workday SaaS domain.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-leg-016",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_internal_audit_notice",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Notice of Upcoming Internal Quality Audit: Engineering Directorate",
        "sender": "quality-assurance@enterprise-corp.com",
        "body": (
            "Engineering Leads,\n\n"
            "Internal Quality Assurance will conduct our annual ISO 27001 surveillance audit between Nov 18 and Nov 22.\n\n"
            "Please review the attached audit schedule and ensure your project architecture documentation is up to date.\n\n"
            "We will host an introductory briefing call this Thursday at 11:00 AM.\n\n"
            "Internal Audit & Governance Committee\nEnterprise Corporation"
        ),
        "explanation": "Authentic internal corporate governance memo with zero links.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-leg-017",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_aws_billing_official",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Amazon Web Services: Monthly Invoice Available for Account #9921-8842",
        "sender": "AWS Billing <no-reply-aws@amazon.com>",
        "body": (
            "Dear AWS Customer,\n\n"
            "Your monthly billing statement for billing period Oct 1 - Oct 31, 2026 is now ready.\n"
            "Total charges: $14,921.40 USD.\n\n"
            "Access your detailed cost allocation reports in the AWS Management Console:\n"
            "https://console.aws.amazon.com/billing/home\n\n"
            "Amazon Web Services, Inc."
        ),
        "explanation": "Authentic cloud provider invoice on official Amazon infrastructure.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-leg-018",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_external_vendor_catering",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Order Confirmation: Catering for All-Hands Luncheon on Nov 14",
        "sender": "orders@gourmet-corporate-catering.com",
        "body": (
            "Hi Lisa,\n\n"
            "This confirms your catering order #GC-8812 for the Q4 All-Hands Luncheon on Friday, November 14.\n\n"
            "We have recorded your request for 120 boxed lunches (including vegetarian and gluten-free selections).\n"
            "Our delivery driver will arrive at 11:30 AM at the 4th Floor reception desk.\n\n"
            "Best regards,\n"
            "Gourmet Corporate Catering Team"
        ),
        "explanation": "Authentic external vendor confirmation using normal corporate catering domain.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-leg-019",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_internal_facilities_desk",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Facilities Update: Headquarters Parking Garage Maintenance Nov 8-10",
        "sender": "facilities-helpdesk@enterprise-corp.com",
        "body": (
            "HQ Employees,\n\n"
            "Please be advised that levels 3 and 4 of the main parking garage will be closed for routine pressure washing and restriping this weekend.\n\n"
            "All vehicles must be vacated by Friday at 7:00 PM. Overflow parking is available in the North Lot.\n\n"
            "Thank you for your cooperation,\n"
            "Facilities Management Operations"
        ),
        "explanation": "Authentic internal corporate facilities notification.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p6-leg-020",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_multi_word_corporate_domain",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Annual Investor Relations Briefing & Shareholder Proxy Circular",
        "sender": "shareholder-services@enterprise-investor-relations.com",
        "body": (
            "Dear Shareholders and Beneficial Owners,\n\n"
            "Notice is hereby given that the Annual Meeting of Stockholders will be held on December 15, 2026.\n\n"
            "You may review the 2026 Annual Report and proxy voting circular directly on our investor portal:\n"
            "https://enterprise-investor-relations.com/annual-meeting-2026\n\n"
            "Office of the Corporate Secretary & Investor Relations"
        ),
        "explanation": "Authentic corporate investor relations circular on legitimate multi-word corporate domain.",
        "source_dataset": "Phase 6 Domain Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
]


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    samples = SOPHISTICATED_PHISHING + DIFFICULT_LEGITIMATE

    print(f"Writing {len(samples)} samples to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for s in samples:
            s["sample_id"] = s["id"]
            line = json.dumps(s, ensure_ascii=False)
            f.write(line + "\n")

    print(f"Successfully generated {OUTPUT_PATH}.")
    print(f"Total samples: {len(samples)}")
    print(f"  Sophisticated Phishing: {len(SOPHISTICATED_PHISHING)}")
    print(f"  Difficult Legitimate:   {len(DIFFICULT_LEGITIMATE)}")

    # Compute SHA-256 hash of dataset
    hasher = hashlib.sha256()
    with open(OUTPUT_PATH, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    print(f"SHA-256 Hash: {hasher.hexdigest()}")


if __name__ == "__main__":
    main()

