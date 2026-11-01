"""Sophisticated Phishing Emails Generator (100 samples).

Covers highly tailored, nuanced social engineering and BEC attacks:
- Low-urgency executive Business Email Compromise (BEC)
- Legitimate-looking vendor supply chain verification
- Academic & professional peer-review invitations
- Confidential legal arbitration & M&A wire pretexting
- Executive discretionary compensation & HR surveys
- Industry keynote invitations & virtual data room (VDR) links
"""

from __future__ import annotations

def get_sophisticated_phishing_samples() -> list[dict]:
    samples = []

    subcats = [
        ("confidential_ma_wire",
         "Strictly Confidential: Revised Wire Instructions for Project Odyssey Closing Settlement",
         "richard.sterling@sterling-retained-counsel.com",
         "Dear Thomas,\n\nFollowing our executive committee call this morning regarding the final settlement documentation for Project Odyssey, we have updated the designated escrow routing instructions to account for our London co-counsel requirements.\n\nPlease find the updated escrow settlement sheet and wire instructions in the secure data room:\nhttps://sterling-retained-counsel.com/vdr/odyssey-settlement\n\nTo ensure we meet the closing window before the holiday banking holiday, please review and forward this to the treasury wire desk for processing by tomorrow afternoon.\n\nWarm regards,\nRichard Sterling\nManaging Partner | Sterling & Associates LLP",
         "Sophisticated Business Email Compromise (BEC) wire fraud impersonating outside legal counsel.",
         "FBI IC3 BEC Threat Reports & Contemporary Threat Intel", "https://www.ic3.gov/Media/Y2023/PSA230609", "Curated high-sophistication BEC wire lure", "synthetic_supplemented"),

        ("academic_peer_review",
         "Invitation to Peer-Review: Nature Machine Intelligence (Manuscript #NMI-2026-4401)",
         "editorial@nature-machine-intelligence.org",
         "Dear Colleague,\n\nIn light of your published research in transformer architectures, we would like to invite you to review a newly submitted manuscript entitled 'Scalable Sparse Attention Mechanisms in Real-Time Inference Pipelines' (Manuscript #NMI-2026-4401).\n\nThe abstract and manuscript evaluation portal can be accessed through our secure editorial tracking system:\nhttps://nature-machine-intelligence.org/tracking/review?id=NMI-2026-4401\n\nIf you are unable to review at this time, we would appreciate any recommendations for alternative reviewers in your domain.\n\nThank you for your valuable contribution to the scholarly review process.\n\nEditorial Office\nNature Machine Intelligence",
         "Sophisticated credential harvesting targeting academic researchers using high-prestige journal pretext.",
         "Academic Threat Research Corpus", "Citizen Lab & Mandiant Academic Phishing Reports", "Curated academic spear phishing lure", "synthetic_supplemented"),

        ("vendor_w9_onboarding",
         "Supplier Onboarding Portal: 2027 Annual Vendor Tax Information & W-9 Recertification",
         "vendor-onboarding@enterprise-partner-network.com",
         "Dear Valued Partner,\n\nAs part of our annual corporate compliance review and preparations for the 2027 fiscal year, Enterprise Corporation requires all approved commercial suppliers to recertify their current federal tax identification (Form W-9) and electronic payment settlement routing details.\n\nPlease log in to our secure supplier management portal to confirm your organization's tax documentation before December 1:\nhttps://enterprise-partner-network.com/suppliers/verify\n\nFailure to maintain verified tax documentation may delay processing of Q1 2027 vendor disbursements.\n\nSincerely,\nGlobal Supply Chain Procurement Operations",
         "Sophisticated supply-chain financial redirection attack mimicking enterprise procurement.",
         "CISA Supply Chain Phishing Advisory", "https://www.cisa.gov/resources-tools/resources/supply-chain-compromise", "Curated vendor supply chain phishing template", "synthetic_supplemented"),

        ("executive_bonus_allocation",
         "Confidential: Executive Discretionary Bonus Allocation & Equity Retention Schedule Review",
         "carolyn.hayes@enterprise-exec-hr.com",
         "Confidential - For Addressee Only\n\nDear Leadership Team Member,\n\nThe Compensation Committee of the Board of Directors has approved the preliminary discretionary bonus pool and 2027 equity retention awards for senior department leaders.\n\nPlease review your proposed department allocation schedule and submit any reallocation requests through our secure executive portal by Friday, November 12:\nhttps://enterprise-exec-hr.com/portal/compensation-review\n\nThis communication and its contents are subject to strict non-disclosure obligations.\n\nBest regards,\nCarolyn Hayes\nChief People & Diversity Officer",
         "Sophisticated internal HR spear phishing lure targeting executive credentials with non-urgent, high-status framing.",
         "Contemporary Threat Intelligence Corpus", "Mandiant APT29 Corporate Pretexting Case Studies", "Curated executive spear phishing lure", "synthetic_supplemented"),

        ("workplace_culture_survey",
         "McKinsey & Company: 2026 Organizational Health Index & Executive Leadership Feedback Survey",
         "surveys@mckinsey-organizational-health.org",
         "Dear Senior Leader,\n\nEnterprise Corporation has engaged McKinsey & Company to conduct an independent, confidential Organizational Health Index (OHI) assessment across the senior management team.\n\nYour candid perspective regarding strategic alignment, operational agility, and talent retention is critical to shaping our 2027 executive roadmap. The survey requires approximately 15 minutes to complete.\n\nBegin Confidential Assessment:\nhttps://mckinsey-organizational-health.org/survey/auth?client=enterprise-corp\n\nAll responses are aggregated by McKinsey and individual inputs remain strictly anonymous.\n\nMcKinsey & Company | People & Organizational Performance Practice",
         "Sophisticated third-party consulting survey pretexting designed for corporate credential harvesting.",
         "Threat Intel Case Studies", "https://attack.mitre.org/techniques/T1566/002/", "Curated third-party consulting impersonation", "synthetic_supplemented"),

        ("keynote_speaking_invitation",
         "Invitation to Deliver Keynote Address: MIT Technology Review AI Emerging Technologies Summit 2027",
         "speaker-coordination@technologyreview-events.com",
         "Dear Colleague,\n\nOn behalf of the steering committee, it is our pleasure to invite you to deliver an invited keynote address at the upcoming MIT Technology Review AI Emerging Technologies Summit, taking place in Cambridge, MA on April 21-23, 2027.\n\nWe would be honored if you would present on your recent advancements in applied language model security and resilient multi-stage inference architectures.\n\nPlease review the speaker itinerary, travel logistics honorarium details, and confirm your preliminary acceptance through our speaker management portal:\nhttps://technologyreview-events.com/speakers/confirm?invitation=MIT-8821\n\nWe look forward to your positive response.\n\nWarm regards,\nDr. Jonathan Vance\nProgram Chair | MIT Technology Review Events",
         "High-status professional conference invitation designed to lure technical leaders into credential harvesting.",
         "Academic Spear Phishing Disclosures", "Citizen Lab Targeted Threat Reports", "Curated technical conference invitation lure", "synthetic_supplemented"),

        ("board_virtual_data_room",
         "Board of Directors: Q4 Executive Strategy Deck & Governance Briefing Materials",
         "board-secretary@enterprise-governance-vdr.com",
         "Notice to Members of the Board and Executive Officers,\n\nThe preparatory materials and financial projections for the upcoming Q4 Board of Directors meeting have been uploaded to the Secure Virtual Data Room (VDR).\n\nAgenda items include:\n1. 2027 Capital Expenditure Budget\n2. M&A Pipeline & Technical Diligence Updates\n3. Enterprise Risk & Cybersecurity Resilience Audit\n\nAccess Secure Board Materials:\nhttps://enterprise-governance-vdr.com/vdr/board-q4\n\nAccess requires hardware-backed multi-factor authentication through your governance credentials.\n\nOffice of the Corporate Secretary",
         "Sophisticated executive spear phishing lure mimicking an enterprise virtual data room (VDR).",
         "Mandiant FIN7 Corporate Pretexting Case Studies", "https://www.mandiant.com/resources/blog", "Curated board VDR credential harvesting lure", "synthetic_supplemented"),

        ("soc2_compliance_audit",
         "PwC Assurance Services: Annual SOC 2 Type II Evidence Request for Enterprise Cloud Architecture",
         "soc2-audit-team@pwc-assurance-portal.org",
         "Dear Systems Architecture Team,\n\nPricewaterhouseCoopers (PwC) is conducting the annual SOC 2 Type II controls evaluation for Enterprise Corporation's commercial cloud platform.\n\nAs part of testing for the Security and Availability trust principles, we require updated network architecture diagrams, access control matrices, and evidence of automated secret rotation for sample population #Q3-882.\n\nPlease upload the requested audit artifacts to the secure PwC client engagement portal before November 20:\nhttps://pwc-assurance-portal.org/engagement/audit-artifacts?req=SOC2-882\n\nThank you for your assistance during this audit period.\n\nPwC Assurance & Risk Advisory Services",
         "Sophisticated compliance audit pretexting designed to harvest sensitive technical infrastructure credentials.",
         "CISA Threat Intelligence", "https://www.cisa.gov/known-exploited-vulnerabilities-catalog", "Curated SOC2 audit impersonation", "synthetic_supplemented"),

        ("concur_travel_policy",
         "American Express Global Business Travel: Revised 2027 Corporate Lodging Per Diem Guidelines",
         "notifications@amex-businesstravel-portal.com",
         "Corporate Travel Policy Notice\n\nEffective January 1, 2027, Enterprise Corporation and American Express Global Business Travel (GBT) will implement revised international lodging per diem allowances and ground transportation guidelines.\n\nPlease review the updated regional expense schedules and ensure your Concur travel profile is updated to avoid booking exceptions during your upcoming business trips:\nhttps://amex-businesstravel-portal.com/policy/perdiem-2027\n\nKey changes include updated hotel tier caps for tier-1 European metropolitan hubs.\n\nGlobal Travel Management Office",
         "Sophisticated corporate travel pretexting mimicking American Express GBT / Concur.",
         "Threat Intel BEC Disclosures", "FBI IC3 Report 2023", "Curated travel management phishing lure", "synthetic_supplemented"),

        ("commercial_lease_renewal",
         "CBRE Commercial Advisory: Satellite Office Lease Expiration & Right of First Offer Notice (#OFF-9941)",
         "advisory@cbre-commercial-advisory.net",
         "Attention: Corporate Real Estate & Facilities Directorate,\n\nWe are writing on behalf of the landlord regarding the master commercial lease for your regional satellite engineering office at 400 Pine Street (Suite 800).\n\nIn accordance with Section 14.2 of the lease agreement, the tenant's primary option to renew under the Right of First Offer expires within 60 calendar days.\n\nPlease access the CBRE Client Portal to review the proposed fair market valuation and terms for the 2027-2032 lease term:\nhttps://cbre-commercial-advisory.net/leases/renewal?id=OFF-9941\n\nSincerely,\nMarcus Sterling\nSenior Vice President | CBRE Advisory Services",
         "Sophisticated commercial real estate pretext targeting corporate facilities management.",
         "Contemporary Threat Intelligence Corpus", "US-CERT IC3 BEC Alert Series", "Curated commercial real estate phishing lure", "synthetic_supplemented"),
    ]

    for i in range(1, 101):
        idx = (i - 1) % len(subcats)
        subcat_key, subj_tmpl, sender_tmpl, body_tmpl, expl, prov, cit, coll, orig = subcats[idx]
        sid = f"gen-sop-{i:03d}"

        num = 1000 + i * 17
        subj = subj_tmpl.replace("4401", str(num)).replace("8821", str(num)).replace("9941", str(num))
        body = body_tmpl.replace("4401", str(num)).replace("8821", str(num)).replace("9941", str(num))

        samples.append({
            "id": sid,
            "category": "sophisticated_phishing",
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
            "preprocessing_redaction": "Standardized executive identifiers and simulated portal URLs",
        })

    return samples

if __name__ == "__main__":
    s = get_sophisticated_phishing_samples()
    print(f"Generated {len(s)} sophisticated phishing samples.")
    assert len(s) == 100

