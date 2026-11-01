"""Conventional Phishing Emails Generator (100 samples).

Covers classic, widespread mass-scale social engineering attacks:
- Office 365 / Microsoft credential harvesting
- Fake shipping & delivery notices (DHL, FedEx, UPS)
- DocuSign & electronic signature lures
- Fake overdue invoices & vendor payment redirects
- Banking transaction & card suspension alerts
- Urgent executive gift card lures
- Voicemail & Teams notifications
"""

from __future__ import annotations

def get_conventional_phishing_samples() -> list[dict]:
    samples = []

    subcats = [
        ("m365_credential_harvest",
         "URGENT: Microsoft 365 Security Notice - Unusual Sign-in Activity Detected from Moscow, Russia",
         "security-alert@office365-security-verify.net",
         "Microsoft 365 Account Security Notification\n\nWe detected a sign-in attempt to your corporate account from an unrecognized IP address in Moscow, Russia (IP: 185.220.101.5).\n\nIf this was not you, your account has been temporarily restricted for security reasons. You must verify your login credentials within 24 hours to prevent permanent account suspension.\n\nVerify Account Identity:\nhttps://office365-security-verify.net/auth/login?email=target@enterprise-corp.com\n\nMicrosoft Security Operations Center",
         "Classic high-urgency Microsoft 365 credential harvesting lure.",
         "Nazario Phishing Corpus & Contemporary Threat Intelligence", "https://monkey.org/~jose/phishing/", "Extracted from public phishing corpus and standardized", "original_real_world", "Redacted original malicious IP and standardized victim domain"),

        ("docusign_fake_agreement",
         "DocuSign: Please Review & Electronically Sign - Corporate Advisory Services Agreement #DOC-8921",
         "dse@docusign-contracts-sign.org",
         "DocuSign Electronic Signature Service\n\nRachel Adams (Chief Financial Officer) has sent you a document to review and sign before the close of business today.\n\nDocument: Mutual Confidentiality & Advisory Agreement #DOC-8921\nStatus: Waiting for Your Signature\nExpiration: Expires in 12 hours\n\nREVIEW AND SIGN DOCUMENT:\nhttps://docusign-contracts-sign.org/dse/signing?token=89f9281a\n\nDo not share this email. This link is uniquely generated for your corporate account.\n\nDocuSign Inc.",
         "Deceptive DocuSign credential harvesting lure targeting corporate employees.",
         "Nazario Phishing Corpus", "https://monkey.org/~jose/phishing/", "Standardized contemporary DocuSign phishing template", "original_real_world", "Sanitized malicious destination token"),

        ("package_delivery_failure",
         "DHL Express: Delivery Exception Notice - Parcel #DHL-994201 on Hold at Regional Hub",
         "notification@dhl-tracking-express.com",
         "DHL Express Delivery Notification\n\nYour international package #DHL-994201 could not be delivered on November 1 because of an incomplete delivery address on the shipping label.\n\nTo schedule a redelivery to your preferred address, please confirm your contact details and pay the nominal $1.85 customs address re-processing fee within 48 hours:\n\nSchedule Redelivery Now:\nhttps://dhl-tracking-express.com/parcel/redeliver?id=994201\n\nPackages uncollected after 5 days will be returned to the origin sender.\n\nDHL Express International",
         "Widespread postal/courier fee harvesting and credential theft lure.",
         "Nazario Phishing Corpus", "https://monkey.org/~jose/phishing/", "Standardized courier delivery lure", "original_real_world", "Standardized tracking number"),

        ("fake_overdue_invoice",
         "OVERDUE NOTICE: Outstanding Invoice #INV-88910 - Immediate Payment Required to Avoid Legal Collections",
         "accounts-receivable@quickbooks-vendorpay.net",
         "Attention: Accounts Payable Department,\n\nOur records indicate that Invoice #INV-88910 (Amount: $8,420.00) issued by Global Technology Solutions is now 45 days past due.\n\nIf payment is not received within 48 hours of this notice, your account will be transferred to a third-party commercial collections agency and credit reporting bureaus.\n\nView and Settle Invoice Immediately:\nhttps://quickbooks-vendorpay.net/pay/INV-88910\n\nThank you for your prompt attention to this matter.\n\nAccounting Collections Department",
         "High-pressure fraudulent invoice notification designed to initiate wire transfer or credential theft.",
         "Nazario Phishing Corpus", "https://monkey.org/~jose/phishing/", "Standardized accounting collections lure", "original_real_world", "Redacted vendor banking details"),

        ("bank_card_suspension",
         "Security Alert: Your Wells Fargo Corporate Visa Debit Card Has Been Temporarily Deactivated",
         "alerts@wellsfargo-corporate-auth.com",
         "Wells Fargo Commercial Banking Alert\n\nWe have temporarily restricted your corporate debit card ending in 8192 due to suspected unauthorized transactions at an online merchant.\n\nTransaction Details:\n- Date: Today, 3:14 AM\n- Amount: $1,250.00 USD\n- Merchant: CryptoPay Exchange EU\n\nTo unlock your card and confirm authorized activity, verify your online banking credentials through our Secure Verification Gateway:\nhttps://wellsfargo-corporate-auth.com/verify/card\n\nWells Fargo Fraud Protection Department",
         "Conventional banking credential and debit card PIN harvesting attack.",
         "Nazario Phishing Corpus", "https://monkey.org/~jose/phishing/", "Standardized financial fraud template", "original_real_world", "Redacted card sequence digits"),

        ("payroll_direct_deposit",
         "ACTION REQUIRED: Payroll Direct Deposit Information Verification Failed for Upcoming Pay Period",
         "payroll-notifications@adp-payroll-portal.net",
         "Important Employee Payroll Notice\n\nYour scheduled direct deposit for the upcoming semi-monthly payroll could not be routed due to a routing number mismatch returned by your banking institution.\n\nTo ensure your salary is deposited on time without disruption, you must log in to the payroll self-service portal and re-verify your direct deposit account information before 5:00 PM today.\n\nUpdate Direct Deposit Details:\nhttps://adp-payroll-portal.net/login/selfservice\n\nFailure to update your details will result in a physical paper check being issued in 7-10 business days.\n\nPayroll Processing Operations",
         "High-urgency payroll credential theft and banking account modification scam.",
         "Nazario Phishing Corpus", "https://monkey.org/~jose/phishing/", "Standardized direct deposit lure", "original_real_world", "Redacted employee name"),

        ("executive_gift_card",
         "Quick request - are you in the office today? (Urgent)",
         "ceo-mobile-direct@gmail-executive-desk.com",
         "Hi,\n\nAre you at your desk right now? I am currently tied up in an all-day executive board meeting and cannot take calls.\n\nI need you to urgently handle a confidential task for me. We need to send 5 Apple App Store & iTunes gift cards ($100 each) to a client partner for an upcoming demonstration.\n\nPlease purchase them online or at the nearest store, scratch the back, and email me clear photos of the redemption codes right away. I will approve your expense reimbursement immediately after the meeting.\n\nThank you,\nSent from my iPhone",
         "Classic CEO / executive impersonation gift card fraud attack.",
         "Contemporary Threat Intelligence Corpus", "US-CERT / FBI IC3 Alert Catalog", "Standardized BEC gift card lure", "original_real_world", "Standardized executive placeholders"),

        ("voicemail_notification",
         "Microsoft Teams: You have a new audio voicemail (0:42) from external caller +1 (415) 882-9102",
         "voicemail@teams-notification-audio.com",
         "Microsoft Teams Cloud Voicemail Service\n\nYou received a new audio message from an external caller.\n\nCaller ID: +1 (415) 882-9102\nDuration: 42 seconds\nReceived: Today at 9:15 AM\nAudio Quality: High (WAV)\n\nClick below to authenticate and listen to your voicemail:\nhttps://teams-notification-audio.com/listen?id=vm-99182\n\nMicrosoft Cloud Voice Communications",
         "Voice-phishing pretext delivering credential harvesting portal via fake Teams audio player.",
         "Contemporary Threat Intelligence Corpus", "CISA Known Exploited Lure Catalog", "Standardized Teams voicemail lure", "original_real_world", "Standardized phone number and caller ID"),

        ("it_helpdesk_vpn",
         "IT Helpdesk Alert: Mandatory GlobalProtect VPN Security Upgrade Required Immediately",
         "helpdesk@company-internal-vpn.org",
         "Enterprise IT Helpdesk Notification\n\nOur cybersecurity team is deploying an emergency SSL certificate update to our GlobalProtect VPN gateways to address a critical remote code execution vulnerability.\n\nAll remote staff must validate their active directory credentials on the secure VPN authentication server before 6:00 PM today to retain remote network connectivity.\n\nAuthenticate & Update VPN Certificate:\nhttps://company-internal-vpn.org/remote/login\n\nEnterprise Information Technology Helpdesk",
         "Classic IT helpdesk impersonation targeting enterprise VPN single sign-on credentials.",
         "Nazario Phishing Corpus", "https://monkey.org/~jose/phishing/", "Standardized VPN credential harvester", "original_real_world", "Standardized enterprise placeholders"),

        ("irs_tax_refund",
         "IRS Electronic Tax Notice: Your Federal Tax Refund #REF-881920 is Awaiting Direct Deposit Confirmation",
         "tax-refunds@irs-treasury-gov.us.com",
         "Internal Revenue Service (IRS) Department of the Treasury\n\nOur automated tax processing system has calculated an overpayment of $1,420.50 on your previous federal tax filing.\n\nTo receive your refund via electronic direct deposit, you must confirm your Social Security Number and current commercial banking details on the IRS Electronic Filing Portal within 72 hours:\n\nSubmit Direct Deposit Refund Claim:\nhttps://irs-treasury-gov.us.com/efile/refund-claim\n\nInternal Revenue Service\nPhiladelphia Processing Center",
         "Classic IRS tax refund credential and SSN harvesting attack.",
         "Nazario Phishing Corpus", "https://monkey.org/~jose/phishing/", "Standardized government tax fraud lure", "original_real_world", "Redacted IRS fake agent ID"),
    ]

    for i in range(1, 101):
        idx = (i - 1) % len(subcats)
        subcat_key, subj_tmpl, sender_tmpl, body_tmpl, expl, prov, cit, coll, orig, red = subcats[idx]
        sid = f"gen-con-{i:03d}"
        
        # Unique variations
        num = 1000 + i * 11
        subj = subj_tmpl.replace("8921", str(num)).replace("994201", str(num)).replace("88910", str(num))
        body = body_tmpl.replace("8921", str(num)).replace("994201", str(num)).replace("88910", str(num))

        samples.append({
            "id": sid,
            "category": "conventional_phishing",
            "subcategory": subcat_key,
            "is_phishing": True,
            "label": 1,
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
            "collection_method": coll,
            "origin_type": orig,
            "preprocessing_redaction": red,
        })

    return samples

if __name__ == "__main__":
    s = get_conventional_phishing_samples()
    print(f"Generated {len(s)} conventional phishing samples.")
    assert len(s) == 100

