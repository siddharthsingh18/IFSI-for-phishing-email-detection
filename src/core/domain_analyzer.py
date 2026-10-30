"""Domain and Sender Evidence Analyzer for Phishing Email Detection.

Extracts structured domain, header, and URL telemetry to assist Stage 2
classification without relying on unverified external WHOIS/DNS queries.
"""

from __future__ import annotations

import email.utils
import re
import urllib.parse
from typing import Any

KNOWN_BRANDS = [
    "microsoft", "office365", "m365", "outlook", "google", "workspace",
    "apple", "icloud", "amazon", "aws", "paypal", "docu", "docusign",
    "concur", "sap", "adp", "quickbooks", "intuit", "workday", "zoom",
    "slack", "dropbox", "box", "salesforce", "servicenow", "okta",
    "dhl", "fedex", "ups", "usps", "chase", "wellsfargo", "bankofamerica",
    "citi", "santander", "sberbank", "sparkasse", "bnpparibas"
]

SUSPICIOUS_TLDS = {
    "xyz", "top", "click", "buzz", "work", "rest", "icu", "link",
    "live", "store", "online", "site", "space", "fun", "website",
    "support", "tech", "bid", "loan", "win"
}

GENERIC_SUSPICIOUS_KEYWORDS = [
    "verify", "login", "portal", "secure", "auth", "account",
    "update", "confirm", "security", "recovery", "signin", "support",
    "retention", "compliance", "payroll", "reschedule", "corporate",
    "desk", "tax", "billing", "identity", "admin", "service", "services"
]


def extract_sender_info(sender_str: str) -> tuple[str, str, str]:
    """Extract display name, address, and domain from a sender string."""
    sender_str = sender_str.strip()
    display_name, address = email.utils.parseaddr(sender_str)
    if not address and "@" in sender_str:
        # Fallback regex if parseaddr misses bare emails
        match = re.search(r"[\w\.-]+@[\w\.-]+", sender_str)
        if match:
            address = match.group(0)

    address = address.lower().strip()
    domain = address.split("@")[1] if "@" in address else ""
    return display_name.strip(), address, domain


def extract_urls(text: str) -> list[str]:
    """Extract all URLs from text."""
    url_pattern = r"https?://(?:[a-zA-Z0-9_-]+\.)+[a-zA-Z0-9_-]+(?:/[^\s<>'\"()]*)?|www\.(?:[a-zA-Z0-9_-]+\.)+[a-zA-Z0-9_-]+(?:/[^\s<>'\"()]*)?"
    matches = re.findall(url_pattern, text)
    # Deduplicate preserving order
    seen = set()
    cleaned = []
    for u in matches:
        u_clean = u.rstrip(".,;!?:")
        if u_clean not in seen:
            seen.add(u_clean)
            cleaned.append(u_clean)
    return cleaned


def extract_domain_from_url(url: str) -> str:
    """Extract registered or host domain from URL."""
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url
    parsed = urllib.parse.urlparse(url)
    netloc = parsed.netloc.lower()
    # Strip port if present
    if ":" in netloc:
        netloc = netloc.split(":")[0]
    return netloc


def analyze_domain_heuristics(domain: str) -> list[str]:
    """Analyze a single domain for suspicious structural heuristics."""
    indicators = []
    if not domain:
        return indicators

    # IP address host
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", domain):
        indicators.append(f"Raw IP address used as host ({domain})")

    parts = domain.split(".")
    tld = parts[-1] if parts else ""
    if tld in SUSPICIOUS_TLDS:
        indicators.append(f"High-risk top-level domain (.{tld})")

    # Excessive subdomains
    if len(parts) > 4:
        indicators.append(f"Excessive subdomain nesting ({len(parts)} levels in {domain})")

    # Check for brand impersonation in domain
    base_name = parts[-2] if len(parts) >= 2 else domain
    full_str = domain.replace(".", "-")

    for brand in KNOWN_BRANDS:
        if brand in full_str and not domain.endswith(f".{brand}.com") and not domain == f"{brand}.com":
            # Brand appears inside hyphenated or composite domain
            # e.g., quickbooks-vendorpay.net, corporate-concur-portal.org
            indicators.append(f"[CRITICAL RISK - BRAND IMPERSONATION] Unauthorized domain '{domain}' embeds brand name '{brand}' (official domain is NOT '{domain}')")
            break

    # Check for combination of suspicious keywords with hyphens
    hyphen_count = base_name.count("-")
    if hyphen_count >= 1:
        matching_keywords = [kw for kw in GENERIC_SUSPICIOUS_KEYWORDS if kw in base_name]
        if len(matching_keywords) >= 2 or (hyphen_count >= 2 and len(matching_keywords) >= 1):
            indicators.append(f"[HIGH RISK - DECEPTIVE LOOKALIKE DOMAIN] Synthetic domain '{domain}' uses administrative keywords ({', '.join(matching_keywords)}) in hyphenated structure")

    return indicators


def analyze_email_domains(
    subject: str,
    sender: str,
    body: str,
    reply_to: str = "",
) -> dict[str, Any]:
    """Comprehensive domain and sender evidence analysis."""
    disp_name, sender_addr, sender_dom = extract_sender_info(sender)
    _, reply_addr, reply_dom = extract_sender_info(reply_to)

    urls = extract_urls(body)
    link_domains = list({extract_domain_from_url(u) for u in urls if extract_domain_from_url(u)})

    # Domain mismatch checks
    reply_mismatch = False
    if reply_dom and sender_dom and reply_dom != sender_dom:
        reply_mismatch = True

    link_mismatches = []
    if sender_dom:
        # Check if root domain matches
        sender_root = ".".join(sender_dom.split(".")[-2:]) if len(sender_dom.split(".")) >= 2 else sender_dom
        for ld in link_domains:
            ld_root = ".".join(ld.split(".")[-2:]) if len(ld.split(".")) >= 2 else ld
            if ld_root != sender_root and not ld.endswith("." + sender_root):
                link_mismatches.append(ld)

    # Collect all domain heuristic signals
    all_indicators = []
    for ind in analyze_domain_heuristics(sender_dom):
        all_indicators.append(f"Sender Domain: {ind}")

    for ld in link_domains:
        for ind in analyze_domain_heuristics(ld):
            all_indicators.append(f"Link Domain: {ind}")

    if reply_mismatch:
        all_indicators.append(f"Reply-To Mismatch: sender @{sender_dom} vs reply-to @{reply_dom}")

    if link_mismatches:
        mismatch_str = ", ".join(link_mismatches[:3])
        if len(link_mismatches) > 3:
            mismatch_str += f" (+{len(link_mismatches)-3} more)"
        all_indicators.append(f"Link Domain Mismatch: Email from @{sender_dom} directs users to external domain(s) ({mismatch_str})")

    has_suspicious_evidence = len(all_indicators) > 0

    return {
        "display_name": disp_name,
        "sender_address": sender_addr,
        "sender_domain": sender_dom,
        "reply_to_address": reply_addr,
        "reply_to_domain": reply_dom,
        "reply_to_mismatch": reply_mismatch,
        "urls_found_count": len(urls),
        "link_domains": link_domains,
        "link_domain_mismatches": link_mismatches,
        "indicators": all_indicators,
        "has_suspicious_evidence": has_suspicious_evidence,
    }


def format_domain_evidence_block(analysis: dict[str, Any]) -> str:
    """Format structured domain evidence as clear contextual input for Stage 2."""
    lines = [
        "[STRUCTURED SENDER & DOMAIN EVIDENCE (VERIFIED FACTS)]",
        f"- Sender Address: {analysis.get('sender_address') or 'Unknown'} (Domain: @{analysis.get('sender_domain') or 'Unknown'})",
    ]
    if analysis.get("display_name"):
        lines.append(f"- Display Name: {analysis['display_name']}")
    if analysis.get("reply_to_address"):
        lines.append(f"- Reply-To Address: {analysis['reply_to_address']} (Mismatch: {'YES ⚠️' if analysis.get('reply_to_mismatch') else 'No'})")

    link_doms = analysis.get("link_domains", [])
    if link_doms:
        lines.append(f"- Extracted Link Domains: {', '.join(link_doms[:5])}")
    else:
        lines.append("- Extracted Link Domains: None (No external URLs detected)")

    mismatches = analysis.get("link_domain_mismatches", [])
    if mismatches:
        lines.append(f"- Sender vs Link Domain Alignment: MISMATCH DETECTED ⚠️ (Links point outside sender domain to: {', '.join(mismatches[:3])})")
    elif link_doms:
        lines.append("- Sender vs Link Domain Alignment: Links match sender domain.")

    indicators = analysis.get("indicators", [])
    if indicators:
        lines.append("- Observable Domain Signals:")
        for ind in indicators[:5]:
            lines.append(f"  • {ind}")
    else:
        lines.append("- Observable Domain Signals: Clean / Standard corporate naming patterns.")

    lines.append("[END STRUCTURED EVIDENCE]")
    return "\n".join(lines)
