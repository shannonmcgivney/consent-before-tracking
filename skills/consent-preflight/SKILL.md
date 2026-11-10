---
name: consent-preflight
description: A 10-minute privacy check to run before publishing any new or changed vibe-coded app, landing page, course site or funnel - ten pass/fail checks centered on "does anything track people before they click Accept?", the lesson from the tracking-pixel lawsuit video. Hands off to consent-audit and consent-gate when a check fails. Also a teachable lesson for students who build with Lovable, Bolt, v0 or Replit. Use when someone says "I'm about to publish", "ready to launch", "pre-launch check", "new Lovable app", "is this safe to go live", or when teaching students how to avoid privacy lawsuits while vibe coding.
---

# Consent preflight: check before you publish

**Why (teach it this way):** vibe coding makes it easy to ship an app in an afternoon, and just as easy to ship a lawsuit. The usual trap is a tracking pixel (Meta, Google, TikTok) that starts the moment the page opens. In California, tracking before consent can be treated as wiretapping, at up to $5,000 per violation. A cookie banner doesn't protect you if the pixel fires before anyone clicks it. **Having a banner and waiting for permission are two completely different things.** The fix is one instruction to your AI builder, plus checking that it worked.

> **The one prompt to remember:** "Make sure no tracking pixels, analytics, or third-party scripts load until the user clicks Accept on my cookie banner."

Not legal advice. This catches the common, expensive mistakes; it doesn't certify anything.

## The 10 checks

Run them on the **preview or live URL in a fresh, cookie-free tab** (Claude's built-in browser: cleared storage, then `read_network_requests` before any click), plus the code scan if code is available:
`python3 ~/.claude/skills/consent-audit/scripts/scan_trackers.py <app-dir>`

| # | Check | Pass |
|---|---|---|
| 1 | **Fresh visit, no click:** any request to an ad/analytics/replay domain (facebook, google-analytics, googletagmanager, tiktok, licdn, hotjar, clarity, posthog, segment, heycatch…)? | None |
| 2 | **Cookies before click:** `_ga`, `_fbp`, `_gcl_au`, `_ttp`, `_hj*`, `ph_*`? | None |
| 3 | **Host add-ons off or gated:** Lovable Visitor analytics, Vercel/Netlify/Cloudflare analytics, site-builder pixel fields | Off, or gated |
| 4 | **Reject works:** click Reject, browse 2 pages, nothing optional fires | Yes |
| 5 | **Banner is fair:** Accept and Reject equally prominent; toggles unchecked. If there are **no** optional trackers, there's **no** banner (none needed) | Yes |
| 6 | **Way back:** a footer "Privacy choices" link to change or withdraw | Yes (if banner exists) |
| 7 | **No identity to trackers:** sign in with a test account; no email or user ID in tracker requests | None sent |
| 8 | **No secrets in URLs sent out:** no `?code=`, `?token=`, `?email=` or search text in tracker requests | None |
| 9 | **Privacy notice:** public page, linked in footer and on sign-up, names the real vendors and real contact | Yes |
| 10 | **Publishing scope:** you know every unpublished change this publish will release | Listed and OK'd |

## Result

```
PREFLIGHT: <app> - <PASS / FIX FIRST>   (<date>)
1 ✅/❌ ... 10 ✅/❌   (one line of evidence each: domains seen, cookies found, or "none")
Fix first: <the failing checks, in order of risk: 1, 7, 2, 3 first>
```

- **All pass:** publish, then rerun checks 1, 2 and 4 on the live URL. Hosting can add scripts that the preview didn't have.
- **Any of 1-4 or 7-8 fail:** don't publish. Run `consent-audit` for the full inventory, then `consent-gate` (or remove the tracker).
- **Only 5, 6 or 9 fail:** fix with `consent-gate`'s banner/notice section, then publish.

## Teaching notes (for students)

- **Show, don't tell:** open their site in a fresh tab with DevTools → Network, filter by "facebook" or "google", reload, and let them watch the pixel fire before they touch the banner. That moment makes the lesson stick.
- **Fewer trackers is the easy win.** If they aren't running ads yet, they don't need a pixel yet. No tracker means no banner and no risk.
- **Analytics vs. your own data:** turning off trackers doesn't delete what their app saves for users (accounts, progress, form answers). That's first-party data, and it's covered by their privacy notice, not the banner.
- **Course and video sites:** a Meta pixel on pages that play videos carries an extra federal risk (VPPA). Keep pixels off lesson pages.
