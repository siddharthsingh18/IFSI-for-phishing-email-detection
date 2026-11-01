"""Build Phase 7 Precision Challenge Dataset (40 focused samples).

Categories:
- 20 Sophisticated Phishing Attacks (lookalike domains, external impersonation,
  reply-to mismatches, synthetic VDRs, financial wire fraud).
- 20 Precision Legitimate Cases (secondary corporate domains, internal senders
  referencing software tools, multi-tenant SaaS authentication portals,
  legitimate external vendor communications).

Strict Verification:
- Complete provenance metadata and explicit ground truth.
- Zero lexical or hash overlap with FAISS index or previous evaluation benchmarks.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

OUTPUT_PATH = Path("data/evaluation/phase7_precision_challenge.jsonl")

# 20 Sophisticated Phishing Attacks
SOPHISTICATED_PHISHING = [
    {
        "id": "p7-sop-001",
        "category": "sophisticated_phishing",
        "subcategory": "board_vdr_lookalike",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Confidential Board Deck: FY2027 Executive Restructuring & Divestiture Plan",
        "sender": "board-advisory@boardroom-strategy-vdr.net",
        "body": (
            "Members of the Board of Directors,\n\n"
            "The confidential materials and risk modeling for Project Apex have been published to the Board Virtual Data Room.\n\n"
            "Please review the valuation schedules and submit committee approvals by 5:00 PM EST:\n"
            "https://boardroom-strategy-vdr.net/vdr/project-apex-fy2027\n\n"
            "Access requires hardware token authentication.\n\n"
            "Office of the Corporate Secretary"
        ),
        "explanation": "Executive spear-phishing utilizing synthetic hyphenated VDR domain.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-sop-002",
        "category": "sophisticated_phishing",
        "subcategory": "docusign_lookalike",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "DocuSign: Please review and execute Settlement & Release Agreement",
        "sender": "DocuSign Legal <notifications@docusign-secure-signing.net>",
        "body": (
            "DocuSign Notification\n\n"
            "Corporate Legal Counsel has requested your signature on: Mutual Separation and General Release.\n\n"
            "View and Sign Envelope:\n"
            "https://docusign-secure-signing.net/signing/envelope-44129\n\n"
            "This document link will expire in 24 hours.\n\n"
            "DocuSign Secure Electronic Signature Operations"
        ),
        "explanation": "DocuSign brand lookalike typosquat domain on synthetic .net infrastructure.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-sop-003",
        "category": "sophisticated_phishing",
        "subcategory": "zoom_webinar_lookalike",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Zoom Meeting: Re-authenticate Corporate Single Sign-On for Enterprise Host License",
        "sender": "Zoom Account Security <support@zoom-webinar-auth.com>",
        "body": (
            "Zoom Cloud Video Communications\n\n"
            "Your enterprise host license has been selected for annual security compliance verification.\n\n"
            "Log in to confirm your corporate credentials and maintain uninterrupted meeting hosting:\n"
            "https://zoom-webinar-auth.com/sso/verify-license\n\n"
            "Zoom Identity & Compliance Directorate"
        ),
        "explanation": "Zoom brand impersonation using synthetic hyphenated authentication domain.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-sop-004",
        "category": "sophisticated_phishing",
        "subcategory": "microsoft_recovery_lookalike",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Microsoft 365: Inactive Mailbox Archival Scheduled for Purge",
        "sender": "Microsoft Cloud Services <admin@microsoft-online-recovery.org>",
        "body": (
            "Microsoft 365 Security Operations\n\n"
            "Your enterprise mailbox quota has exceeded retention policies and will be scheduled for permanent deletion.\n\n"
            "To retain your mailbox and extend cloud storage quotas:\n"
            "https://microsoft-online-recovery.org/exchange/retain-mailbox\n\n"
            "Microsoft Corporation Cloud Services"
        ),
        "explanation": "Microsoft 365 credential harvesting on lookalike .org domain.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-sop-005",
        "category": "sophisticated_phishing",
        "subcategory": "okta_sso_gateway_lookalike",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Okta Verify: Critical Firmware & Multi-Factor Push Notification Update",
        "sender": "Okta Support <notifications@okta-sso-gateway.net>",
        "body": (
            "Okta Identity Notice\n\n"
            "A critical OAuth token expiration requires immediate browser certificate synchronization.\n\n"
            "Re-authenticate your Okta SSO token to maintain VPN and internal application connectivity:\n"
            "https://okta-sso-gateway.net/auth/token-refresh\n\n"
            "Okta Identity Operations"
        ),
        "explanation": "Okta lookalike domain chaining brand name and administrative gateway keywords.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-sop-006",
        "category": "sophisticated_phishing",
        "subcategory": "external_hr_impersonation",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "HR Notice: Mandatory Review of Revised 2027 Remote Work & Severance Terms",
        "sender": "People Operations <hr-payroll-desk.net@external-mail-route.com>",
        "body": (
            "All Personnel,\n\n"
            "Please review the updated 2027 enterprise remote work guidelines and return your signed acknowledgement.\n\n"
            "Access your employee portal:\n"
            "https://hr-payroll-desk.net/portal/remote-work-2027\n\n"
            "Corporate Human Resources"
        ),
        "explanation": "External sender masquerading as internal HR using synthetic portal domain.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-sop-007",
        "category": "sophisticated_phishing",
        "subcategory": "workday_portal_lookalike",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Workday HCM: Action Required - Correct Direct Deposit Routing Number",
        "sender": "Workday Payroll Team <payroll-admin@workday-hr-portal.com>",
        "body": (
            "Workday Automated Payroll Notice\n\n"
            "An ACH bank routing exception occurred during our pre-payroll cycle test.\n\n"
            "Log in to Workday to confirm your direct deposit transit number:\n"
            "https://workday-hr-portal.com/payroll/direct-deposit-fix\n\n"
            "Workday Payroll Administration"
        ),
        "explanation": "Workday brand typosquat using synthetic hyphenated portal domain.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-sop-008",
        "category": "sophisticated_phishing",
        "subcategory": "reply_to_mismatch_invoice",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "REVISED INVOICE: Milestone 3 Core Cloud Migration Completion (#INV-4491)",
        "sender": "finance@trusted-contractor-services.com",
        "body": (
            "From: finance@trusted-contractor-services.com\n"
            "Reply-To: treasury-wire-inbox@fastmail-route.net\n\n"
            "Dear Accounts Payable,\n\n"
            "Attached is our revised invoice #INV-4491.\n"
            "Please note our receiving banking details have been transitioned to our secondary custodian bank.\n\n"
            "Authorize payment schedule: https://trusted-contractor-services.com/billing/invoice-4491\n\n"
            "Accounts Receivable Department"
        ),
        "explanation": "BEC invoice alteration with hidden Reply-To header mismatch redirecting remittance replies.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-sop-009",
        "category": "sophisticated_phishing",
        "subcategory": "financial_wire_alteration",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "CONFIDENTIAL: Updated Escrow Wire Details for Corporate Property Acquisition",
        "sender": "settlement-officer@escrow-closing-portal.net",
        "body": (
            "Attention Treasury Department,\n\n"
            "Due to an automated clearing house maintenance window, the closing escrow account for the commercial lease has been updated.\n\n"
            "Please log in to retrieve the certified wire transfer instruction sheet:\n"
            "https://escrow-closing-portal.net/escrow/wire-instructions-2027\n\n"
            "Certified Escrow & Closing Services"
        ),
        "explanation": "Real-estate escrow wire fraud on synthetic hyphenated portal domain.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-sop-010",
        "category": "sophisticated_phishing",
        "subcategory": "concur_expense_lookalike",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "SAP Concur: Mandatory Travel Profile & Corporate Card Security Update",
        "sender": "Concur Operations <security@concur-travel-portal.org>",
        "body": (
            "SAP Concur Automated Travel Services\n\n"
            "A mandatory PCI-DSS compliance update requires re-entering your corporate credit card billing address.\n\n"
            "Update your travel profile:\n"
            "https://concur-travel-portal.org/profile/card-revalidate\n\n"
            "SAP Concur Travel & Expense Solutions"
        ),
        "explanation": "SAP Concur lookalike domain chaining brand name and administrative keywords on .org.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-sop-011",
        "category": "sophisticated_phishing",
        "subcategory": "it_servicedesk_quota",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "IT Support Notice: Urgent Server Migration - Confirm Mailbox Credentials",
        "sender": "helpdesk@corporate-support-portal.net",
        "body": (
            "Global IT Support Center\n\n"
            "Our engineering team is conducting a primary mail exchange server cutover tonight.\n\n"
            "To prevent mailbox synchronization failure, verify your active login status:\n"
            "https://corporate-support-portal.net/migration/auth-sync\n\n"
            "Enterprise Service Desk"
        ),
        "explanation": "IT infrastructure quota spear-phish on synthetic corporate support domain.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-sop-012",
        "category": "sophisticated_phishing",
        "subcategory": "adp_tax_w2_lookalike",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "ADP TotalSource: 2026 Year-End W-2 Verification and Delivery Election",
        "sender": "ADP Tax Operations <tax-docs@adp-portal-online.net>",
        "body": (
            "Attention Employee,\n\n"
            "Your 2026 Form W-2 statement is ready for review.\n\n"
            "Log in to ADP TotalSource to select electronic delivery:\n"
            "https://adp-portal-online.net/w2/delivery-selection\n\n"
            "ADP, Inc. Automated Tax Notification"
        ),
        "explanation": "ADP brand impersonation utilizing hyphenated lookalike .net domain.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-sop-013",
        "category": "sophisticated_phishing",
        "subcategory": "salesforce_pipeline_lookalike",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Salesforce Security: Inbound Lead Opportunity Sync Failed",
        "sender": "admin@salesforce-pipeline-auth.com",
        "body": (
            "Sales Operations Alert\n\n"
            "Lead assignment rules failed to sync for enterprise opportunity #OPP-99214.\n\n"
            "Re-authenticate your Salesforce API credentials:\n"
            "https://salesforce-pipeline-auth.com/oauth/token-sync\n\n"
            "Enterprise CRM Administration"
        ),
        "explanation": "Salesforce brand impersonation using synthetic hyphenated authentication domain.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-sop-014",
        "category": "sophisticated_phishing",
        "subcategory": "dhl_customs_lookalike",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "DHL Express: Unclaimed International Shipment #DHL-881923 - Clearance Required",
        "sender": "customs@dhl-express-customs.org",
        "body": (
            "Shipment Notification\n\n"
            "Your parcel is held at the airport customs facility due to missing clearance documentation.\n\n"
            "Complete customs clearance and schedule dispatch:\n"
            "https://dhl-express-customs.org/tracking/clearance-portal\n\n"
            "DHL Express Logistics"
        ),
        "explanation": "DHL shipping notification lure with lookalike .org domain.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-sop-015",
        "category": "sophisticated_phishing",
        "subcategory": "executive_bonus_census",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "CONFIDENTIAL: Executive Performance Bonus & Equity Deferral Election Form",
        "sender": "exec-compensation@board-executive-census.com",
        "body": (
            "Confidential Memorandum,\n\n"
            "The Board Compensation Committee requires all Senior Vice Presidents to submit their annual bonus allocation deferrals.\n\n"
            "Submit your election form online:\n"
            "https://board-executive-census.com/census/bonus-election-2027\n\n"
            "Executive Compensation Directorate"
        ),
        "explanation": "Targeted executive spear-phishing on synthetic executive census domain.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-sop-016",
        "category": "sophisticated_phishing",
        "subcategory": "reply_to_mismatch_legal",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Privileged Legal Memorandum: Regulatory Inquiry & Deposition Preparation",
        "sender": "counsel@outside-legal-advisory.com",
        "body": (
            "From: counsel@outside-legal-advisory.com\n"
            "Reply-To: external-litigation-desk@sec-mail-gateway.net\n\n"
            "Dear General Counsel,\n\n"
            "Please review our preliminary response strategy regarding the upcoming civil deposition.\n\n"
            "Review legal strategy brief: https://outside-legal-advisory.com/filings/strategy-brief-v2\n\n"
            "Partner, Corporate Defense Practice"
        ),
        "explanation": "Outside legal counsel pretext with hidden Reply-To header mismatch routing replies to attacker gateway.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-sop-017",
        "category": "sophisticated_phishing",
        "subcategory": "cloud_procurement_renewal",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "AWS Cloud Services: Master Infrastructure Agreement Auto-Renewal Notice",
        "sender": "billing-support@cloud-enterprise-billing.net",
        "body": (
            "Enterprise Procurement Notice\n\n"
            "Your enterprise cloud infrastructure contract auto-renews at the end of this billing cycle.\n\n"
            "Review compute commitments and billing authority:\n"
            "https://cloud-enterprise-billing.net/contracts/aws-renewal-2027\n\n"
            "Global IT Vendor Management"
        ),
        "explanation": "Enterprise IT cloud procurement pretext on synthetic hyphenated billing domain.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-sop-018",
        "category": "sophisticated_phishing",
        "subcategory": "amex_gbt_flight_schedule",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "American Express GBT: Urgent Schedule Alteration for Flight AA-8812",
        "sender": "itinerary-alerts@amextravel-corporate.com",
        "body": (
            "Travel Schedule Alteration Notice\n\n"
            "Your outbound flight from SFO to JFK has experienced a scheduled equipment change.\n\n"
            "Re-confirm your seat assignment and boarding priority:\n"
            "https://amextravel-corporate.com/itinerary/reconfirm-seat\n\n"
            "American Express Global Business Travel"
        ),
        "explanation": "American Express GBT travel itinerary lure on synthetic lookalike domain.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-sop-019",
        "category": "sophisticated_phishing",
        "subcategory": "culture_audit_token",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Mandatory Anonymous Workplace Culture & Ethical Leadership Assessment",
        "sender": "audit-director@workplace-culture-audit.org",
        "body": (
            "Dear Colleague,\n\n"
            "An independent assessment of organizational transparency commissioned by the Board is currently underway.\n\n"
            "Access your single-use survey token:\n"
            "https://workplace-culture-audit.org/survey/auth-token-8812\n\n"
            "Independent Workplace Evaluation Institute"
        ),
        "explanation": "Credential harvesting lure mimicking an external third-party organizational culture audit.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-sop-020",
        "category": "sophisticated_phishing",
        "subcategory": "cross_domain_auth_redirect",
        "is_phishing": True,
        "label": 1,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Final Review: Project Vanguard Q4 Financial Audit Model.xlsx",
        "sender": "lead-analyst@consulting-partner-firm.com",
        "body": (
            "Hi team,\n\n"
            "Here is the audited cash flow model for Project Vanguard.\n\n"
            "Access the secure financial workbook:\n"
            "https://external-auth-gateway.net/workbooks/vanguard-model-2027\n\n"
            "Please review before our call.\n\n"
            "Senior Financial Analyst"
        ),
        "explanation": "Phishing lure where sender domain appears normal but destination link directs to external auth gateway.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
]

# 20 Precision Legitimate Cases
PRECISION_LEGITIMATE = [
    {
        "id": "p7-leg-001",
        "category": "difficult_legitimate",
        "subcategory": "historical_fp_amazon_business_variant",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Your Amazon Business order #114-9921402 has shipped",
        "sender": "order-update@amazon-business.com",
        "body": (
            "Hello Corporate Purchasing Team,\n\n"
            "Your order of 10x Logitech 4K Pro Webcams has shipped via UPS Ground (Tracking: 1Z882910482104).\n\n"
            "Estimated Delivery: Thursday by 4:00 PM.\n"
            "Delivery Address: Receiving Bay 2, Tech Operations Center.\n\n"
            "Thank you for shopping with Amazon Business."
        ),
        "explanation": "Authentic corporate order shipment notification from verified Amazon Business secondary domain.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-leg-002",
        "category": "difficult_legitimate",
        "subcategory": "historical_fp_internal_concur_variant",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "SAP Concur: Expense Report #ER-9912 Approved by Vice President",
        "sender": "concur-travel@enterprise-corp.com",
        "body": (
            "Attention Employee,\n\n"
            "Your travel and lodging expense report for the Singapore Technical Leadership Summit has been approved.\n\n"
            "Reimbursement will be deposited to your primary bank account within 3 business days.\n\n"
            "Review payment advice: https://concur.internal.enterprise-corp.com/reimbursement/ER-9912\n\n"
            "Corporate Finance Operations\nEnterprise Corporation"
        ),
        "explanation": "Authentic internal corporate email from company domain referencing SAP Concur and internal subdomain link.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-leg-003",
        "category": "difficult_legitimate",
        "subcategory": "historical_fp_workday_tenant_variant",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Workday: Your Annual Total Rewards Compensation Statement is Ready",
        "sender": "Workday Notifications <notifications@workday.com>",
        "body": (
            "Your 2026 Total Rewards Summary is now available for review in Workday.\n\n"
            "View your complete salary, health benefits, and equity vesting breakdown:\n"
            "https://www.myworkday.com/enterprise-corp/login.htmld\n\n"
            "Workday Human Capital Management"
        ),
        "explanation": "Authentic Workday notification linking to verified myworkday.com customer tenant portal.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-leg-004",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_docusign_system",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "DocuSign: Please review and sign Q4 Master Services Agreement Amendment",
        "sender": "\"DocuSign System\" <dse@docusign.net>",
        "body": (
            "DocuSign\n\n"
            "Corporate Procurement has sent you a document for digital execution.\n\n"
            "Please review the attached contract amendment:\n"
            "https://na2.docusign.net/Member/PowerFormSigning.aspx?PowerFormId=msa-4491\n\n"
            "DocuSign, Inc. | Electronic Signature Services"
        ),
        "explanation": "Authentic transactional document notification from DocuSign's official docusign.net infrastructure.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-leg-005",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_concursolutions_authorized",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Concur Travel: Electronic Ticket Confirmation & Airline E-Receipt",
        "sender": "Concur Travel <travel-confirmations@concursolutions.com>",
        "body": (
            "Your upcoming business travel flight reservation has been ticketed successfully.\n\n"
            "Passenger: Sarah Jenkins\n"
            "Flight: Delta Air Lines DL 492 (JFK -> BOS)\n"
            "Record Locator: K9X21M\n\n"
            "View itinerary details: https://www.concursolutions.com/travel/itinerary?rec=K9X21M\n\n"
            "SAP Concur Travel Solutions"
        ),
        "explanation": "Authentic flight confirmation from SAP Concur's official concursolutions.com domain.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-leg-006",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_zoom_calendar_invite",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Zoom Meeting: Q4 Global Architecture Review & Microservices Strategy",
        "sender": "no-reply@zoom.us",
        "body": (
            "Hello,\n\n"
            "David Vance is inviting you to a scheduled Zoom meeting.\n\n"
            "Topic: Q4 Global Architecture Review\n"
            "Time: Nov 18, 2026 02:00 PM Eastern Time\n\n"
            "Join Zoom Meeting:\n"
            "https://zoom.us/j/88129401824?pwd=UVBSRm10a0xZWHJLNnp5a3R5\n\n"
            "Meeting ID: 881 2940 1824\n\n"
            "Zoom Cloud Video Communications"
        ),
        "explanation": "Authentic calendar invite on official zoom.us domain.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-leg-007",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_internal_workday_mention",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "People Ops: Set Your 2027 Annual Performance Goals in Workday",
        "sender": "people-operations@enterprise-corp.com",
        "body": (
            "All Employees,\n\n"
            "The FY2027 goal-setting cycle is officially open. Please collaborate with your people manager to enter your key deliverables.\n\n"
            "Access the internal goal-setting dashboard via SSO:\n"
            "https://hr.internal.enterprise-corp.com/goals/fy2027\n\n"
            "Please complete your submissions by Friday, December 1.\n\n"
            "People Operations & Talent Development\nEnterprise Corporation"
        ),
        "explanation": "Internal HR email from company domain mentioning Workday in subject while linking to internal subdomain.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-leg-008",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_internal_zoom_mention",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "IT Infrastructure: Annual Renewal of Corporate Zoom Large-Meeting Add-ons",
        "sender": "it-procurement@enterprise-corp.com",
        "body": (
            "Department Heads,\n\n"
            "We are compiling the annual departmental headcount requirements for Zoom 500-seat and 1000-seat webinar licenses.\n\n"
            "If your team requires hosting licenses for external client webinars next quarter, submit your request here:\n"
            "https://servicedesk.internal.enterprise-corp.com/licenses/zoom-addons\n\n"
            "IT Procurement & Asset Management"
        ),
        "explanation": "Internal IT procurement memo referencing Zoom in subject while keeping all links on internal company subdomains.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-leg-009",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_greenhouse_scorecard",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Interview Scorecard: Senior Staff Security Engineer Candidate Interview",
        "sender": "Enterprise Recruiting <no-reply@greenhouse.io>",
        "body": (
            "Hi Alex,\n\n"
            "Thank you for interviewing candidate Morgan Reed for the Senior Staff Security Engineer position.\n\n"
            "Please submit your technical evaluation scorecard before the end of the day:\n"
            "https://app.greenhouse.io/scorecards/interview-881294\n\n"
            "Global Talent Acquisition"
        ),
        "explanation": "Authentic recruiting scorecard notification linking to legitimate Greenhouse SaaS platform.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-leg-010",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_okta_subdomain",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Okta Access Request: Production Cloud IAM Role Granted",
        "sender": "Okta Identity System <system@enterprise-corp.okta.com>",
        "body": (
            "Okta Identity Cloud\n\n"
            "Your temporary access request for the Production Cloud ReadOnly IAM role has been approved.\n\n"
            "Access is valid for 8 hours. View your active sessions in the Okta application portal:\n"
            "https://enterprise-corp.okta.com/app/UserHome\n\n"
            "Enterprise Identity & Access Governance"
        ),
        "explanation": "Authentic enterprise multi-tenant Okta subdomain notification.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-leg-011",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_salesforce_case",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Service Cloud: Premier Customer Support Case #0099182 Status Resolved",
        "sender": "Support Escalations <support@salesforce.com>",
        "body": (
            "Hello Customer Support Leads,\n\n"
            "Premier Support Case #0099182 has been updated with resolution comments from the database core team.\n\n"
            "Review case resolution in Salesforce:\n"
            "https://login.salesforce.com/cases/0099182\n\n"
            "Salesforce Customer Success"
        ),
        "explanation": "Authentic CRM notification on verified salesforce.com domain.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-leg-012",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_servicenow_incident",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "ServiceNow Incident #INC08821 Assigned to Cloud Infrastructure Operations",
        "sender": "Enterprise ServiceDesk <it-notifications@service-now.com>",
        "body": (
            "Incident INC08821 has been assigned to your queue.\n\n"
            "Summary: Latency spike observed on Redis caching layer in us-east-1.\n"
            "Priority: 2 - High\n\n"
            "View incident details in ServiceNow:\n"
            "https://enterprise.service-now.com/nav_to.do?uri=incident.do?sys_id=INC08821\n\n"
            "ServiceNow Cloud Platform"
        ),
        "explanation": "Authentic enterprise incident notification from service-now.com.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-leg-013",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_github_security",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "[GitHub] Dependabot Alert: Security Advisory published for urllib3",
        "sender": "GitHub Notifications <notifications@github.com>",
        "body": (
            "We found a potential security vulnerability in your repository enterprise-corp/identity-service.\n\n"
            "Vulnerability: Proxy header stripping bypass in urllib3 < 2.2.2\n\n"
            "View Dependabot alert and automated pull request:\n"
            "https://github.com/enterprise-corp/identity-service/security/dependabot/19\n\n"
            "GitHub Security Operations"
        ),
        "explanation": "Authentic security advisory from github.com.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-leg-014",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_jira_mention",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "[Jira] (SEC-8812) Sarah Jenkins assigned an issue to you",
        "sender": "Jira Notifications <jira@enterprise-corp.atlassian.net>",
        "body": (
            "Sarah Jenkins assigned SEC-8812 (Deploy Mutual TLS on Internal Service Mesh) to you.\n\n"
            "Please review the rollout steps and testing criteria:\n"
            "https://enterprise-corp.atlassian.net/browse/SEC-8812\n\n"
            "Atlassian Cloud Services"
        ),
        "explanation": "Authentic Jira notification on enterprise Atlassian multi-tenant domain.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-leg-015",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_zendesk_support",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "[Request #991823] New Corporate YubiKey Hardware Token Shipped",
        "sender": "Enterprise IT Support <support@enterprise-corp.zendesk.com>",
        "body": (
            "Your hardware security key replacement request #991823 has been fulfilled by the IT Depot.\n\n"
            "Tracking details and activation instructions are available in your ticket:\n"
            "https://enterprise-corp.zendesk.com/hc/requests/991823\n\n"
            "Enterprise Desktop Services"
        ),
        "explanation": "Authentic IT support notification on Zendesk enterprise subdomain.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-leg-016",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_outside_counsel",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Privileged Legal Communication: Q4 SEC Form 10-K Disclosure Committee Draft",
        "sender": "marcus.vance@gibsondunn-legal.com",
        "body": (
            "Dear Enterprise Corporation Legal Team,\n\n"
            "Attached for your review is our marked draft of the Item 1A Risk Factors section for the upcoming Form 10-K.\n\n"
            "We have scheduled our disclosure review conference call for Wednesday at 10:00 AM EST.\n\n"
            "Best regards,\n"
            "Marcus Vance, Partner\n"
            "Gibson, Dunn & Crutcher LLP"
        ),
        "explanation": "Authentic outside legal counsel correspondence with zero links.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-leg-017",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_aws_invoice",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Amazon Web Services: Monthly Billing Statement for Account #1184-9921",
        "sender": "AWS Billing <no-reply-aws@amazon.com>",
        "body": (
            "Dear AWS Customer,\n\n"
            "Your monthly invoice for the billing period ending October 31, 2026 is now available.\n"
            "Total Amount: $18,492.15 USD.\n\n"
            "Review your cost explorer breakdown and detailed PDF invoice:\n"
            "https://console.aws.amazon.com/billing/home\n\n"
            "Amazon Web Services, Inc."
        ),
        "explanation": "Authentic AWS billing notification on official Amazon domain.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-leg-018",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_external_catering",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Order Confirmation: Executive Committee Dinner Catering for Dec 5",
        "sender": "events@metropolitan-corporate-catering.com",
        "body": (
            "Hi David,\n\n"
            "This confirms your catering booking for the Executive Committee Dinner on Friday, December 5.\n\n"
            "We have noted your menu selections for 24 attendees including dietary requests.\n"
            "Our staff will arrive at 5:30 PM at the 8th Floor Board Dining Room.\n\n"
            "Metropolitan Corporate Catering"
        ),
        "explanation": "Authentic external vendor invoice/order confirmation from normal corporate catering domain.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-leg-019",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_facilities_maintenance",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Headquarters Facility Advisory: Main Data Center Fire Suppression System Testing",
        "sender": "facilities-management@enterprise-corp.com",
        "body": (
            "All Campus Personnel,\n\n"
            "Please be advised that annual maintenance and sound testing of the inert gas fire suppression systems will take place this Saturday between 8:00 AM and 1:00 PM.\n\n"
            "No building evacuation is required, but access to Building B Level 1 will be restricted to authorized engineers.\n\n"
            "Facilities Operations Directorate\nEnterprise Corporation"
        ),
        "explanation": "Authentic internal corporate facilities notice with zero links.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
    {
        "id": "p7-leg-020",
        "category": "difficult_legitimate",
        "subcategory": "legitimate_investor_relations",
        "is_phishing": False,
        "label": 0,
        "has_prompt_injection": False,
        "active_prompt_injection": False,
        "quoted_prompt_injection": False,
        "injection_type": "none",
        "subject": "Enterprise Corporation: Notice of Q3 Earnings Conference Call & Webcast",
        "sender": "investor-relations@enterprise-investor-relations.com",
        "body": (
            "Shareholders and Financial Analysts,\n\n"
            "Enterprise Corporation will report third-quarter financial results on Tuesday, November 25, followed by a live webcast at 4:30 PM EST.\n\n"
            "Listen to the live webcast and download the supplementary investor presentation deck:\n"
            "https://enterprise-investor-relations.com/earnings/q3-2026-webcast\n\n"
            "Investor Relations Directorate"
        ),
        "explanation": "Authentic investor relations webcast circular on legitimate multi-word corporate domain.",
        "source_dataset": "Phase 7 Precision Challenge Benchmark",
        "origin_type": "synthetic_domain_challenge",
    },
]


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    samples = SOPHISTICATED_PHISHING + PRECISION_LEGITIMATE

    print(f"Writing {len(samples)} samples to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for s in samples:
            s["sample_id"] = s["id"]
            line = json.dumps(s, ensure_ascii=False)
            f.write(line + "\n")

    print(f"Successfully generated {OUTPUT_PATH}.")
    print(f"Total samples: {len(samples)}")
    print(f"  Sophisticated Phishing: {len(SOPHISTICATED_PHISHING)}")
    print(f"  Precision Legitimate:   {len(PRECISION_LEGITIMATE)}")

    hasher = hashlib.sha256()
    with open(OUTPUT_PATH, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    print(f"SHA-256 Hash: {hasher.hexdigest()}")


if __name__ == "__main__":
    main()

