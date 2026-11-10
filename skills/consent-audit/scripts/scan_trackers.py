#!/usr/bin/env python3
"""Scan a web project for trackers, pixels, analytics and third-party scripts.

Usage: python3 scan_trackers.py <project-dir> [--json]

Read-only. Standard library only. Prints a Markdown report (or JSON) listing
each signature hit with file:line, the vendor, its class, whether the line
looks like it sends identity data, and whether a consent check appears
within a few lines. "Consent nearby" is a hint to read the code, not proof
of a gate.
"""
import json
import os
import re
import sys

SKIP_DIRS = {
    "node_modules", ".git", "dist", "build", ".next", ".nuxt", ".output",
    ".vercel", ".netlify", "coverage", ".turbo", ".cache", "vendor",
    "__pycache__", ".svelte-kit", "out", "public/build",
}
EXTS = {
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte",
    ".astro", ".html", ".htm", ".php", ".liquid", ".hbs", ".ejs", ".md",
    ".mdx", ".json", ".toml", ".yaml", ".yml", ".env.example",
}
MAX_BYTES = 2_000_000

# (vendor, class, regex). Classes: ads, analytics, replay, tagmanager,
# embed, chat, fonts, necessary
SIGNATURES = [
    ("Meta Pixel", "ads", r"connect\.facebook\.net|fbevents\.js|\bfbq\s*\("),
    ("Meta Conversions API", "ads", r"graph\.facebook\.com/.+/events|conversions[-_ ]?api"),
    ("Google Tag Manager", "tagmanager", r"googletagmanager\.com/gtm|\bGTM-[A-Z0-9]{4,}"),
    ("Google Analytics / gtag", "analytics", r"googletagmanager\.com/gtag|google-analytics\.com|\bgtag\s*\(|\bG-[A-Z0-9]{6,}\b|react-ga4?|@next/third-parties"),
    ("Google Ads", "ads", r"googleadservices\.com|\bAW-\d{6,}|doubleclick\.net"),
    ("TikTok Pixel", "ads", r"analytics\.tiktok\.com|\bttq\.(load|page|track)"),
    ("LinkedIn Insight", "ads", r"snap\.licdn\.com|_linkedin_partner_id|\blintrk\s*\("),
    ("X/Twitter Pixel", "ads", r"static\.ads-twitter\.com|\btwq\s*\("),
    ("Pinterest Tag", "ads", r"s\.pinimg\.com/ct|\bpintrk\s*\("),
    ("Snap Pixel", "ads", r"sc-static\.net/scevent|\bsnaptr\s*\("),
    ("Reddit Pixel", "ads", r"redditstatic\.com/ads|\brdt\s*\("),
    ("Microsoft UET/Bing", "ads", r"bat\.bing\.com|\buetq\b"),
    ("Hotjar", "replay", r"static\.hotjar\.com|\bhj\s*\(|hotjar"),
    ("Microsoft Clarity", "replay", r"clarity\.ms|@microsoft/clarity"),
    ("FullStory", "replay", r"fullstory\.com|@fullstory"),
    ("LogRocket", "replay", r"logrocket"),
    ("Smartlook/Mouseflow/Lucky Orange", "replay", r"smartlook|mouseflow|luckyorange"),
    ("PostHog", "analytics", r"posthog"),
    ("Mixpanel", "analytics", r"mixpanel"),
    ("Segment", "analytics", r"cdn\.segment\.com|@segment/analytics|analytics\.load\s*\("),
    ("Amplitude", "analytics", r"amplitude"),
    ("Heap", "analytics", r"heapanalytics|\bheap\.(load|track|identify)"),
    ("HeyCatch", "analytics", r"heycatch"),
    ("Plausible", "analytics", r"plausible\.io"),
    ("Umami", "analytics", r"umami"),
    ("Fathom", "analytics", r"usefathom\.com"),
    ("Vercel Analytics", "analytics", r"@vercel/analytics|@vercel/speed-insights"),
    ("Cloudflare Web Analytics", "analytics", r"static\.cloudflareinsights\.com|beacon\.min\.js"),
    ("Sentry (may capture PII/replay)", "analytics", r"@sentry/|sentry\.io|replayIntegration"),
    ("Intercom", "chat", r"widget\.intercom\.io|intercom"),
    ("Crisp", "chat", r"client\.crisp\.chat"),
    ("Drift/HubSpot chat", "chat", r"js\.driftt\.com|js\.hs-scripts\.com|js\.hs-analytics\.net"),
    ("Tawk.to", "chat", r"embed\.tawk\.to"),
    ("YouTube embed", "embed", r"youtube\.com/embed|youtube\.com/iframe_api"),
    ("Vimeo embed", "embed", r"player\.vimeo\.com"),
    ("Calendly embed", "embed", r"assets\.calendly\.com|calendly\.com/.*embed"),
    ("Google Maps", "embed", r"maps\.googleapis\.com|google\.com/maps/embed"),
    ("Mapbox", "embed", r"api\.mapbox\.com|mapbox-gl"),
    ("Google Fonts (visitor IP to Google)", "fonts", r"fonts\.googleapis\.com|fonts\.gstatic\.com"),
    ("Stripe.js", "necessary", r"js\.stripe\.com|@stripe/stripe-js|loadStripe\s*\("),
    ("reCAPTCHA/Turnstile", "necessary", r"google\.com/recaptcha|challenges\.cloudflare\.com/turnstile"),
]
COMPILED = [(v, c, re.compile(p, re.I)) for v, c, p in SIGNATURES]

IDENTITY = re.compile(
    r"identify\s*\(|setUser\s*\(|set_user|setUserId|user_id\s*[:=]|userId\s*[:=]|"
    r"\bemail\b|\bem\s*:|\bph\s*:|advanced_matching|external_id|"
    r"location\.href|window\.location\.search|document\.URL",
    re.I,
)
CONSENT = re.compile(
    r"consent|cookieyes|onetrust|cookiebot|klaro|osano|termly|iubenda|"
    r"hasOptedIn|opt_?in|optIn|granted|analytics_storage|ad_storage|gpc|globalPrivacyControl",
    re.I,
)
CONSENT_WINDOW = 15


def iter_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        dirnames[:] = [
            d for d in dirnames
            if d not in SKIP_DIRS and os.path.join(rel, d).lstrip("./") not in SKIP_DIRS
        ]
        for name in filenames:
            path = os.path.join(dirpath, name)
            lower = name.lower()
            if lower.endswith((".min.js", ".map", ".lock")) or lower in ("package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb"):
                continue
            ext = os.path.splitext(lower)[1]
            if ext in EXTS or lower.startswith(".env") or lower in ("index.html", "_document.tsx", "_app.tsx"):
                try:
                    if os.path.getsize(path) <= MAX_BYTES:
                        yield path
                except OSError:
                    pass


def scan(root):
    hits = []
    for path in iter_files(root):
        try:
            with open(path, encoding="utf-8", errors="ignore") as fh:
                lines = fh.read().splitlines()
        except OSError:
            continue
        rel = os.path.relpath(path, root)
        is_manifest = os.path.basename(path) == "package.json"
        for i, line in enumerate(lines):
            for vendor, cls, rx in COMPILED:
                if rx.search(line):
                    lo, hi = max(0, i - CONSENT_WINDOW), min(len(lines), i + CONSENT_WINDOW + 1)
                    window = "\n".join(lines[lo:hi])
                    hits.append({
                        "vendor": vendor,
                        "class": cls,
                        "file": rel,
                        "line": i + 1,
                        "code": line.strip()[:160],
                        "identity": bool(IDENTITY.search(line)) and cls not in ("necessary", "fonts", "embed"),
                        "consent_nearby": bool(CONSENT.search(window)),
                        "dependency_only": is_manifest,
                    })
    return hits


def entry_point(file):
    f = file.lower()
    return any(k in f for k in ("index.html", "main.", "app.", "_app", "_document", "layout.", "root.", "head", "provider"))


def report_md(root, hits):
    out = [f"# Tracker scan: {os.path.abspath(root)}", ""]
    optional = [h for h in hits if h["class"] not in ("necessary",)]
    vendors = sorted({h["vendor"] for h in optional})
    out.append(f"**{len(hits)} hits, {len(vendors)} optional/third-party vendors:** " + (", ".join(vendors) or "none"))
    risky = [h for h in optional if h["class"] in ("ads", "analytics", "replay", "tagmanager") and not h["consent_nearby"] and not h["dependency_only"]]
    ident = [h for h in optional if h["identity"]]
    out.append("")
    out.append(f"- Ads/analytics/replay lines with **no consent check nearby**: {len(risky)}")
    out.append(f"- Lines that look like they **send identity or URL data**: {len(ident)}")
    out.append(f"- Starts in an app-wide entry file (index.html, main, App, layout, provider): {sum(1 for h in risky if entry_point(h['file']))}")
    out.append("")
    out.append("| Vendor | Class | File:line | Consent nearby | Identity/URL | Code |")
    out.append("|---|---|---|---|---|---|")
    order = {"ads": 0, "tagmanager": 1, "replay": 2, "analytics": 3, "chat": 4, "embed": 5, "fonts": 6, "necessary": 7}
    for h in sorted(hits, key=lambda h: (order.get(h["class"], 9), h["vendor"], h["file"], h["line"])):
        code = h["code"].replace("|", "\\|").replace("`", "'")
        dep = " (dependency)" if h["dependency_only"] else ""
        out.append(
            f"| {h['vendor']}{dep} | {h['class']} | `{h['file']}:{h['line']}` | "
            f"{'yes' if h['consent_nearby'] else '**no**'} | {'**yes**' if h['identity'] else ''} | `{code}` |"
        )
    out.append("")
    out.append("Next: read each flagged line in context, then run the live fresh-visit network check "
               "(consent-audit Step 2). Host-injected analytics (Lovable Visitor analytics, Vercel, "
               "Cloudflare, GTM tags) will not show up here.")
    return "\n".join(out)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(2)
    root = args[0]
    if not os.path.isdir(root):
        print(f"Not a directory: {root}", file=sys.stderr)
        sys.exit(2)
    hits = scan(root)
    if "--json" in sys.argv:
        print(json.dumps(hits, indent=2))
    else:
        print(report_md(root, hits))


if __name__ == "__main__":
    main()
