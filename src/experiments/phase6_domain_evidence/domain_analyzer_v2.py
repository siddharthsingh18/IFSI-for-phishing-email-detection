"""Domain Analyzer V2 for Phase 6 Domain Evidence Integration Study.

Design Principles:
1. Purely Factual & Descriptive: Emits observable structural facts without evaluative
   hallucinations or subjective labels.
2. Zero False Reassurance: NEVER asserts a domain is "Clean" or "Standard corporate
   naming patterns". Absence of detected anomalies is reported neutrally.
3. Zero Synthetic Severity Flags: Removes [CRITICAL RISK] and [HIGH RISK] tags.
   Allows Stage 2 LLM to evaluate evidence alongside semantic text and RAG exemplars.
4. Multi-Tenant SaaS & Multi-Domain Brand Awareness: Recognizes legitimate authorized
   domains (e.g., docusign.net, concursolutions.com, zoom.us) without false alarms.
5. Structural Lookalike & Discrepancy Detection: Deterministically flags hyphenated
   brand lookalikes, chained administrative keywords, display-name spoofing, and
   unaligned reply-to headers.
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
    "lever.co",
    "workday.com",
    "service-now.com",
    "zendesk.com",
    "atlassian.net",
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

# Recognized high-target enterprise brands and their authorized registered domains
AUTHORIZED_BRAND_DOMAINS: dict[str, set[str]] = {
    "microsoft": {"microsoft.com", "office.com", "live.com", "outlook.com", "sharepoint.com", "azure.com"},
    "office365": {"office.com", "office365.com", "microsoft.com"},
    "google": {"google.com", "gmail.com", "googlemail.com"},
    "apple": {"apple.com", "icloud.com"},
    "amazon": {"amazon.com", "aws.amazon.com"},
    "paypal": {"paypal.com"},
    "chase": {"chase.com", "jpmorganchase.com"},
    "wellsfargo": {"wellsfargo.com"},
    "bankofamerica": {"bankofamerica.com", "bofa.com"},
    "citibank": {"citi.com", "citibank.com"},
    "adp": {"adp.com"},
    "workday": {"workday.com"},
    "concur": {"concur.com", "concursolutions.com"},
    "amex": {"americanexpress.com", "amexglobalbusinesstravel.com"},
    "americanexpress": {"americanexpress.com", "amexglobalbusinesstravel.com"},
    "docusign": {"docusign.com", "docusign.net"},
    "quickbooks": {"quickbooks.intuit.com", "intuit.com"},
    "intuit": {"intuit.com", "quickbooks.com"},
    "fedex": {"fedex.com"},
    "ups": {"ups.com"},
    "dhl": {"dhl.com"},
    "zoom": {"zoom.us", "zoom.com"},
    "salesforce": {"salesforce.com", "force.com"},
    "okta": {"okta.com"},
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


def analyze_email_domains(
    subject: str,
    sender: str,
    email_text: str,
) -> dict[str, Any]:
    """Extract and analyze structured domain telemetry from email headers and body.

    Returns deterministic observables without evaluative bias or hallucinated safety claims.
    """
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

    observations: list[str] = []

    # 1. Reply-To discrepancy check
    if reply_to_domain and sender_domain and reply_to_domain != sender_domain:
        observations.append(
            f"Reply-To Mismatch: Inbound email sender is '@{sender_domain}' but replies are routed to '@{reply_to_domain}'."
        )

    # 2. Sender Domain Lookalike / Hyphenated Pattern Check
    sender_domain_parts = sender_domain.split(".")[0].split("-") if sender_domain else []
    brand_found_in_sender = None
    for brand, auth_domains in AUTHORIZED_BRAND_DOMAINS.items():
        if brand in sender_domain:
            # Check if it is an authorized domain for that brand
            if sender_reg_domain in auth_domains or any(sender_domain.endswith("." + d) for d in auth_domains):
                continue
            brand_found_in_sender = brand
            break

    if brand_found_in_sender:
        auth_domains = sorted(list(AUTHORIZED_BRAND_DOMAINS[brand_found_in_sender]))
        observations.append(
            f"Synthetic Brand Lookalike: Sender domain '{sender_domain}' embeds brand name '{brand_found_in_sender}' "
            f"with hyphenated or extra words; does not match authorized domain(s) ({', '.join(auth_domains)})."
        )

    # Check for chained administrative keywords in sender domain (e.g. enterprise-governance-vdr.com)
    admin_keywords_in_sender = [kw for kw in SUSPICIOUS_ADMIN_KEYWORDS if kw in sender_domain_parts or f"-{kw}" in sender_domain or f"{kw}-" in sender_domain]
    if len(admin_keywords_in_sender) >= 2 and not brand_found_in_sender:
        observations.append(
            f"Administrative Lookalike Construction: Sender domain '{sender_domain}' chains multiple administrative/service keywords "
            f"({', '.join(admin_keywords_in_sender)}) in a synthetic hyphenated structure."
        )

    # 3. Display Name / Claimed Entity vs Sender Domain Alignment
    combined_header = f"{display_name} {subject}".lower()
    for brand, auth_domains in AUTHORIZED_BRAND_DOMAINS.items():
        if brand in combined_header:
            if sender_reg_domain and sender_reg_domain not in auth_domains and not any(sender_domain.endswith("." + d) for d in auth_domains):
                brand_alert = (
                    f"Identity Mismatch: Header/Subject references '{brand.title()}' but sender domain is '{sender_domain}' "
                    f"(authorized domains: {', '.join(sorted(list(auth_domains)))})."
                )
                if brand_alert not in observations:
                    observations.append(brand_alert)

    # 4. Destination Link Analysis
    if url_data:
        aligned_links = 0
        saas_links = 0
        external_links = 0

        for link_info in url_data:
            host = link_info["host"]
            link_reg = link_info["registered_domain"]

            # Subdomain or exact domain match
            if sender_reg_domain and (link_reg == sender_reg_domain or host.endswith("." + sender_reg_domain)):
                aligned_links += 1
            elif link_reg in RECOGNIZED_SAAS_DOMAINS or any(host.endswith("." + s) for s in RECOGNIZED_SAAS_DOMAINS):
                saas_links += 1
                observations.append(
                    f"Third-Party SaaS Destination: Link points to established enterprise provider '{host}' (common multi-tenant cross-domain workflow)."
                )
            else:
                external_links += 1
                # Check if external link has lookalike or brand impersonation
                for brand, auth_domains in AUTHORIZED_BRAND_DOMAINS.items():
                    if brand in link_reg and link_reg not in auth_domains:
                        observations.append(
                            f"Deceptive Link Destination: Link host '{host}' embeds brand name '{brand}' in an unofficial domain (authorized: {', '.join(sorted(list(auth_domains)))})."
                        )
                        break

        if external_links > 0 and aligned_links == 0 and saas_links == 0:
            observations.append(
                f"External Destination: All extracted destination links ({', '.join(unique_link_domains)}) point outside sender domain '{sender_domain}' to unverified third-party hosts."
            )
        elif aligned_links > 0 and external_links == 0:
            if brand_found_in_sender or len(admin_keywords_in_sender) >= 2:
                observations.append(
                    f"Link Destination: Destination URL points to the same synthetic/unverified sender domain ('{sender_domain}')."
                )
            else:
                observations.append(
                    f"Domain Alignment: Destination link hosts are internal subdomains or exact matches of sender domain '{sender_domain}'."
                )
    else:
        observations.append("No active web links detected in email body.")

    # 5. Neutral fallback if no anomalous observations
    if not observations:
        observations.append(
            f"Sender domain '@{sender_domain}' and available headers exhibit standard structural alignment; no lookalike patterns or display mismatches observed."
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
        "observations": observations,
    }


def format_domain_evidence_block(analysis: dict[str, Any]) -> str:
    """Format domain telemetry into a strictly factual, neutral evidence block for Stage 2."""
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

    obs = analysis.get("observations", [])
    lines.append("- Observable Structural Facts:")
    for o in obs:
        lines.append(f"  * {o}")

    return "\n".join(lines)
