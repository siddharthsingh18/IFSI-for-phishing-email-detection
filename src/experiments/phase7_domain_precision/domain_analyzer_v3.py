"""Domain Analyzer V3 for Phase 7 Domain Evidence Precision Refinement.

Key Precision Enhancements:
1. Auditable Multi-Domain Registry: Explicitly models authorized secondary domains
   (e.g., amazon-business.com) and tenant application portals (e.g., myworkday.com).
2. Internal Corporate Sender Context: Differentiates internal corporate tool references
   (e.g., @enterprise-corp.com referencing SAP Concur) from external brand impersonation.
3. Explicit Evidence Semantics: Categorizes facts into:
   - Observed Header & Routing Facts
   - Verified Organizational Relationships
   - Structural Anomalies & Discrepancies
   - Reputation Notice (unknown domains are never translated to 'clean')
4. Zero Evaluative Hallucinations: Zero synthetic risk scores, zero [CRITICAL RISK]
   tags, zero false reassurance.
"""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

# Well-known multi-tenant SaaS / enterprise infrastructure domains
RECOGNIZED_SAAS_DOMAINS = {
    "docusign.net",
    "docusign.com",
    "salesforce.com",
    "force.com",
    "zoom.us",
    "zoom.com",
    "okta.com",
    "oktapreview.com",
    "slack.com",
    "greenhouse.io",
    "ghire.com",
    "lever.co",
    "workday.com",
    "myworkday.com",
    "service-now.com",
    "servicenow.com",
    "zendesk.com",
    "atlassian.net",
    "atlassian.com",
    "jira.com",
    "confluence.com",
    "github.com",
    "gitlab.com",
    "box.com",
    "dropbox.com",
    "microsoft.com",
    "office.com",
    "sharepoint.com",
    "google.com",
    "webex.com",
}

# Explicit, auditable multi-domain enterprise mappings:
# Maps brand identifier to authorized sender domains, tenant/link domains, and evidence scope.
VERIFIED_ENTERPRISE_RELATIONSHIPS: dict[str, dict[str, Any]] = {
    "amazon": {
        "authorized_sender_domains": {"amazon.com", "aws.amazon.com", "amazon-business.com"},
        "authorized_link_domains": {"amazon.com", "aws.amazon.com", "amazon-business.com"},
        "description": "Amazon Corporate & B2B Procurement Infrastructure",
        "evidence_source": "Enterprise B2B Purchasing Portals & AWS Public Registry",
    },
    "workday": {
        "authorized_sender_domains": {"workday.com", "myworkday.com"},
        "authorized_link_domains": {"workday.com", "myworkday.com"},
        "description": "Workday HCM & Multi-Tenant Application Portal",
        "evidence_source": "Workday Customer Tenant Architecture Documentation",
    },
    "concur": {
        "authorized_sender_domains": {"concur.com", "concursolutions.com"},
        "authorized_link_domains": {"concur.com", "concursolutions.com"},
        "description": "SAP Concur Corporate Travel & Solutions Portal",
        "evidence_source": "SAP Concur Architecture & Enterprise Integration Guide",
    },
    "docusign": {
        "authorized_sender_domains": {"docusign.com", "docusign.net"},
        "authorized_link_domains": {"docusign.com", "docusign.net"},
        "description": "DocuSign e-Signature Platform & Secondary Processing",
        "evidence_source": "DocuSign API & Infrastructure Routing Documentation",
    },
    "microsoft": {
        "authorized_sender_domains": {"microsoft.com", "office.com", "live.com", "outlook.com", "sharepoint.com", "azure.com"},
        "authorized_link_domains": {"microsoft.com", "office.com", "live.com", "outlook.com", "sharepoint.com", "azure.com"},
        "description": "Microsoft 365, Office & Cloud Infrastructure",
        "evidence_source": "Microsoft Enterprise Identity & M365 Endpoint Registry",
    },
    "office365": {
        "authorized_sender_domains": {"office.com", "office365.com", "microsoft.com"},
        "authorized_link_domains": {"office.com", "office365.com", "microsoft.com"},
        "description": "Microsoft 365 Enterprise Services",
        "evidence_source": "Microsoft 365 Domain List",
    },
    "google": {
        "authorized_sender_domains": {"google.com", "gmail.com", "googlemail.com"},
        "authorized_link_domains": {"google.com", "gmail.com"},
        "description": "Google Workspace & Identity",
        "evidence_source": "Google Workspace Documentation",
    },
    "apple": {
        "authorized_sender_domains": {"apple.com", "icloud.com"},
        "authorized_link_domains": {"apple.com", "icloud.com"},
        "description": "Apple Corporate & iCloud Services",
        "evidence_source": "Apple Corporate Registry",
    },
    "chase": {
        "authorized_sender_domains": {"chase.com", "jpmorganchase.com"},
        "authorized_link_domains": {"chase.com", "jpmorganchase.com"},
        "description": "JPMorgan Chase Enterprise Financial Services",
        "evidence_source": "JPMorgan Chase Corporate Registry",
    },
    "wellsfargo": {
        "authorized_sender_domains": {"wellsfargo.com"},
        "authorized_link_domains": {"wellsfargo.com"},
        "description": "Wells Fargo Financial Services",
        "evidence_source": "Wells Fargo Corporate Registry",
    },
    "bankofamerica": {
        "authorized_sender_domains": {"bankofamerica.com", "bofa.com"},
        "authorized_link_domains": {"bankofamerica.com", "bofa.com"},
        "description": "Bank of America Financial Services",
        "evidence_source": "Bank of America Corporate Registry",
    },
    "adp": {
        "authorized_sender_domains": {"adp.com"},
        "authorized_link_domains": {"adp.com"},
        "description": "ADP TotalSource & Payroll Portal",
        "evidence_source": "ADP Enterprise Documentation",
    },
    "amex": {
        "authorized_sender_domains": {"americanexpress.com", "amexglobalbusinesstravel.com"},
        "authorized_link_domains": {"americanexpress.com", "amexglobalbusinesstravel.com"},
        "description": "American Express Corporate & GBT Travel Management",
        "evidence_source": "American Express GBT Global Registry",
    },
    "quickbooks": {
        "authorized_sender_domains": {"quickbooks.com", "intuit.com"},
        "authorized_link_domains": {"quickbooks.com", "intuit.com"},
        "description": "Intuit QuickBooks Cloud Accounting",
        "evidence_source": "Intuit Merchant Services Documentation",
    },
    "zoom": {
        "authorized_sender_domains": {"zoom.us", "zoom.com"},
        "authorized_link_domains": {"zoom.us", "zoom.com"},
        "description": "Zoom Video Communications Infrastructure",
        "evidence_source": "Zoom Infrastructure Registry",
    },
    "salesforce": {
        "authorized_sender_domains": {"salesforce.com", "force.com"},
        "authorized_link_domains": {"salesforce.com", "force.com"},
        "description": "Salesforce CRM & Cloud Infrastructure",
        "evidence_source": "Salesforce Infrastructure Documentation",
    },
    "okta": {
        "authorized_sender_domains": {"okta.com", "oktapreview.com"},
        "authorized_link_domains": {"okta.com", "oktapreview.com"},
        "description": "Okta Identity Cloud & Tenant Subdomains",
        "evidence_source": "Okta Enterprise Documentation",
    },
    "servicenow": {
        "authorized_sender_domains": {"service-now.com", "servicenow.com"},
        "authorized_link_domains": {"service-now.com", "servicenow.com"},
        "description": "ServiceNow Enterprise Cloud & Tenant Instances",
        "evidence_source": "ServiceNow Architecture Documentation",
    },
    "atlassian": {
        "authorized_sender_domains": {"atlassian.com", "atlassian.net", "jira.com", "confluence.com"},
        "authorized_link_domains": {"atlassian.com", "atlassian.net", "jira.com", "confluence.com"},
        "description": "Atlassian Cloud Productivity Suite",
        "evidence_source": "Atlassian Cloud Infrastructure Guide",
    },
    "greenhouse": {
        "authorized_sender_domains": {"greenhouse.io", "ghire.com"},
        "authorized_link_domains": {"greenhouse.io", "app.greenhouse.io"},
        "description": "Greenhouse Recruiting Platform",
        "evidence_source": "Greenhouse Infrastructure Guide",
    },
}

# Administrative / credential lure keywords commonly found in synthetic lookalike domains
SUSPICIOUS_ADMIN_KEYWORDS = {
    "portal", "auth", "login", "verify", "verification", "update", "security",
    "account", "billing", "invoice", "payroll", "benefits", "vdr", "corporate",
    "internal", "support", "desk", "service", "services", "gateway", "access",
    "sync", "sso", "credentials", "compliance", "identity", "governance",
    "board", "executive", "exec", "advisory", "audit", "memo", "talent",
    "contractor", "contractors", "consulting",
}

# Multi-part TLD suffixes
MULTI_PART_TLDS = {
    "co.uk", "org.uk", "gov.uk", "ac.uk", "com.au", "net.au", "org.au",
    "co.jp", "ne.jp", "com.br", "co.nz", "com.sg", "co.in", "net.in",
}


def extract_registered_domain(hostname: str) -> str:
    """Extract registered domain (e.g. 'sub.example.com' -> 'example.com', 'foo.co.uk' -> 'foo.co.uk')."""
    if not hostname:
        return ""
    host = hostname.lower().strip().rstrip(".")
    if ":" in host:
        host = host.split(":")[0]

    parts = host.split(".")
    if len(parts) <= 2:
        return host

    two_part = ".".join(parts[-2:])
    if two_part in MULTI_PART_TLDS and len(parts) >= 3:
        return ".".join(parts[-3:])

    return ".".join(parts[-2:])


def parse_sender_header(sender_str: str) -> tuple[str, str, str]:
    """Parse 'Display Name <email@domain.com>' or 'email@domain.com'.

    Returns (display_name, email_address, domain).
    """
    if not sender_str:
        return "", "", ""

    sender_str = sender_str.strip()
    match = re.search(r"^(.*?)(?:<([^<>@\s]+@[^<>@\s]+)>)?$", sender_str)
    if match and match.group(2):
        display_name = match.group(1).strip(" \"'")
        email_addr = match.group(2).strip().lower()
    else:
        m_email = re.search(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", sender_str)
        if m_email:
            email_addr = m_email.group(1).lower()
            display_name = sender_str.replace(email_addr, "").strip(" \"'<>")
        else:
            email_addr = ""
            display_name = sender_str.strip(" \"'")

    domain = email_addr.split("@")[-1].lower() if "@" in email_addr else ""
    return display_name, email_addr, domain


def extract_urls(text: str) -> list[str]:
    """Extract all HTTP/HTTPS URLs from text."""
    if not text:
        return []
    url_pattern = r"https?://[a-zA-Z0-9\-._~:/?#\[\]@!$&'()*+,;=%]+"
    urls = re.findall(url_pattern, text)
    cleaned = []
    for u in urls:
        u_clean = u.rstrip(".,;!?:)'\"]}")
        if u_clean not in cleaned:
            cleaned.append(u_clean)
    return cleaned


def analyze_email_domains_v3(
    subject: str,
    sender: str,
    email_text: str,
) -> dict[str, Any]:
    """Domain Analyzer V3 with high-precision contextual relationship modeling."""
    display_name, sender_email, sender_domain = parse_sender_header(sender)
    sender_reg_domain = extract_registered_domain(sender_domain)

    # Extract Reply-To from text if present
    reply_to = ""
    reply_to_domain = ""
    m_reply = re.search(r"^Reply-To:\s*(.+)$", email_text, re.MULTILINE | re.IGNORECASE)
    if m_reply:
        _, reply_to, reply_to_domain = parse_sender_header(m_reply.group(1))

    # Extract all destination URLs
    urls = extract_urls(email_text)
    url_data = []
    unique_link_domains = set()

    for u in urls:
        try:
            parsed = urlparse(u)
            host = (parsed.hostname or "").lower()
            reg_domain = extract_registered_domain(host)
            if reg_domain:
                unique_link_domains.add(reg_domain)
            url_data.append({
                "url": u,
                "host": host,
                "registered_domain": reg_domain,
            })
        except Exception:
            continue

    # Semantic Evidence Categories
    structural_facts: list[str] = []
    verified_relationships: list[str] = []
    structural_anomalies: list[str] = []

    # 1. Routing Facts & Reply-To Check
    if reply_to_domain and sender_domain and reply_to_domain != sender_domain:
        structural_anomalies.append(
            f"Routing Discrepancy (Reply-To Mismatch): Sender address is '@{sender_domain}' but replies are routed to external domain '@{reply_to_domain}'."
        )

    # 2. Check for Verified Enterprise Secondary Domains
    sender_is_verified_secondary = False
    for brand, info in VERIFIED_ENTERPRISE_RELATIONSHIPS.items():
        auth_senders = info["authorized_sender_domains"]
        if sender_reg_domain in auth_senders or any(sender_domain.endswith("." + d) for d in auth_senders):
            sender_is_verified_secondary = True
            verified_relationships.append(
                f"Verified Enterprise Domain: Sender domain '{sender_domain}' is an authorized domain for {info['description']}."
            )
            break

    # 3. Check for Synthetic Lookalike Brand Domains (if not verified)
    brand_found_in_sender = None
    if not sender_is_verified_secondary:
        for brand, info in VERIFIED_ENTERPRISE_RELATIONSHIPS.items():
            if brand in sender_domain:
                brand_found_in_sender = brand
                auth_senders = sorted(list(info["authorized_sender_domains"]))
                structural_anomalies.append(
                    f"Synthetic Brand Lookalike: Sender domain '{sender_domain}' embeds brand name '{brand}' "
                    f"with hyphenated or extra words; does not match authorized domain(s) ({', '.join(auth_senders)})."
                )
                break

    # 4. Check for Chained Administrative Keywords (e.g. enterprise-governance-vdr.com)
    sender_domain_parts = sender_domain.split(".")[0].split("-") if sender_domain else []
    admin_keywords_in_sender = [
        kw for kw in SUSPICIOUS_ADMIN_KEYWORDS
        if kw in sender_domain_parts or f"-{kw}" in sender_domain or f"{kw}-" in sender_domain
    ]
    if len(admin_keywords_in_sender) >= 2 and not sender_is_verified_secondary and not brand_found_in_sender:
        structural_anomalies.append(
            f"Administrative Lookalike Construction: Sender domain '{sender_domain}' chains multiple administrative/service keywords "
            f"({', '.join(admin_keywords_in_sender)}) in a synthetic hyphenated structure."
        )

    # 5. Display Name vs. Sender Domain Alignment (Context-Aware)
    # Check if display name claims to represent a major brand (e.g. "DocuSign System", "Microsoft Support")
    if display_name:
        display_lower = display_name.lower()
        for brand, info in VERIFIED_ENTERPRISE_RELATIONSHIPS.items():
            if brand in display_lower:
                auth_senders = info["authorized_sender_domains"]
                if sender_reg_domain not in auth_senders and not any(sender_domain.endswith("." + d) for d in auth_senders):
                    structural_anomalies.append(
                        f"Display Identity Mismatch: Display Name claims identity '{display_name}' but email is sent from "
                        f"unaffiliated domain '@{sender_domain}' (expected: {', '.join(sorted(list(auth_senders)))})."
                    )

    # 6. Internal Corporate Sender Context & Subject Line Checking
    # If the email originates from an internal domain (e.g., enterprise-corp.com) and subject mentions an enterprise tool (e.g. SAP Concur):
    subject_lower = subject.lower()
    for brand, info in VERIFIED_ENTERPRISE_RELATIONSHIPS.items():
        if brand in subject_lower:
            # Check if sender is internal or destination links point to internal infrastructure
            internal_aligned = any(
                link_info["host"].endswith("." + sender_domain) or link_info["registered_domain"] == sender_reg_domain
                for link_info in url_data
            )
            # If sender domain is NOT the brand domain, but is internal and links are internal:
            if not sender_is_verified_secondary and internal_aligned:
                verified_relationships.append(
                    f"Internal Corporate Tool Reference: Subject references '{brand.title()}' while email originates from "
                    f"internal corporate domain '@{sender_domain}'; destination links point to verified internal subdomains."
                )
            elif not sender_is_verified_secondary and not brand_found_in_sender and not display_name:
                # If an external unverified domain mentions a brand in subject with zero internal links
                if not any(link_info["registered_domain"] in info["authorized_link_domains"] for link_info in url_data):
                    pass  # Don't trigger false alarm on subject alone unless display name or domain is spoofed

    # 7. Destination Link Alignment
    if url_data:
        aligned_links = 0
        saas_tenant_links = 0
        external_links = 0

        for link_info in url_data:
            host = link_info["host"]
            link_reg = link_info["registered_domain"]

            # Subdomain or exact domain match
            if sender_reg_domain and (link_reg == sender_reg_domain or host.endswith("." + sender_reg_domain)):
                aligned_links += 1
            else:
                # Check verified enterprise relationships (e.g., workday.com -> myworkday.com)
                matched_relationship = None
                for brand, info in VERIFIED_ENTERPRISE_RELATIONSHIPS.items():
                    if link_reg in info["authorized_link_domains"] or any(host.endswith("." + d) for d in info["authorized_link_domains"]):
                        matched_relationship = info
                        break

                if matched_relationship:
                    saas_tenant_links += 1
                    verified_relationships.append(
                        f"Authorized Enterprise Destination: Destination host '{host}' is a verified application/tenant domain "
                        f"for {matched_relationship['description']}."
                    )
                elif link_reg in RECOGNIZED_SAAS_DOMAINS or any(host.endswith("." + s) for s in RECOGNIZED_SAAS_DOMAINS):
                    saas_tenant_links += 1
                    structural_facts.append(
                        f"Multi-Tenant SaaS Destination: Link directs to established enterprise provider '{host}' (standard cross-domain workflow)."
                    )
                else:
                    external_links += 1
                    # Check if external link has lookalike or brand impersonation
                    for brand, info in VERIFIED_ENTERPRISE_RELATIONSHIPS.items():
                        if brand in link_reg and link_reg not in info["authorized_link_domains"]:
                            structural_anomalies.append(
                                f"Deceptive Link Destination: Link host '{host}' embeds brand name '{brand}' in an unofficial domain (authorized: {', '.join(sorted(list(info['authorized_link_domains'])))})."
                            )
                            break

        if external_links > 0 and aligned_links == 0 and saas_tenant_links == 0:
            structural_anomalies.append(
                f"External Destination: All extracted destination links ({', '.join(unique_link_domains)}) point outside sender domain '{sender_domain}' to unverified third-party hosts."
            )
        elif aligned_links > 0 and external_links == 0:
            if brand_found_in_sender or len(admin_keywords_in_sender) >= 2:
                structural_anomalies.append(
                    f"Link Destination: Destination URL points to the same synthetic/unverified sender domain ('{sender_domain}')."
                )
            else:
                structural_facts.append(
                    f"Domain Alignment: Destination link hosts are internal subdomains or exact matches of sender domain '{sender_domain}'."
                )
    else:
        structural_facts.append("No active web links detected in email body.")

    # Neutral fallback if no observations
    if not structural_facts and not verified_relationships and not structural_anomalies:
        structural_facts.append(
            f"Sender domain '@{sender_domain}' and available headers exhibit standard structural alignment; no lookalike patterns or routing anomalies observed."
        )

    return {
        "display_name": display_name,
        "sender_email": sender_email,
        "sender_domain": sender_domain,
        "sender_reg_domain": sender_reg_domain,
        "reply_to": reply_to,
        "reply_to_domain": reply_to_domain,
        "destination_urls": url_data,
        "unique_link_domains": sorted(list(unique_link_domains)),
        "structural_facts": structural_facts,
        "verified_relationships": verified_relationships,
        "structural_anomalies": structural_anomalies,
    }


def format_domain_evidence_block_v3(analysis: dict[str, Any]) -> str:
    """Format domain telemetry into a structured, categorized evidence block for Stage 2."""
    lines = ["[STRUCTURED SENDER & DOMAIN EVIDENCE]"]

    sender_email = analysis.get("sender_email") or "Not specified"
    sender_domain = analysis.get("sender_domain") or "Not specified"
    display_name = analysis.get("display_name") or "None"
    reply_to = analysis.get("reply_to") or "None"

    lines.append(f"- Sender Address: {sender_email}")
    lines.append(f"- Sender Domain: {sender_domain}")
    if display_name and display_name != "None":
        lines.append(f"- Display Name: {display_name}")
    if reply_to and reply_to != "None":
        lines.append(f"- Reply-To Address: {reply_to}")

    urls = analysis.get("destination_urls", [])
    if urls:
        lines.append("- Extracted Destination Links:")
        seen_hosts = set()
        count = 0
        for u in urls:
            host = u["host"]
            if host not in seen_hosts and count < 4:
                lines.append(f"  * {u['url']} (Host: {host})")
                seen_hosts.add(host)
                count += 1
    else:
        lines.append("- Extracted Destination Links: None")

    # Grouped Categorized Observations
    verified = analysis.get("verified_relationships", [])
    if verified:
        lines.append("- Verified Organizational Relationships:")
        for v in verified:
            lines.append(f"  * {v}")

    facts = analysis.get("structural_facts", [])
    if facts:
        lines.append("- Observable Structural Facts:")
        for f in facts:
            lines.append(f"  * {f}")

    anomalies = analysis.get("structural_anomalies", [])
    if anomalies:
        lines.append("- Observed Structural Anomalies:")
        for a in anomalies:
            lines.append(f"  * {a}")

    lines.append("- Reputation Notice: Absence of structural anomalies does not prove safety; unknown external domains remain unverified.")

    return "\n".join(lines)

