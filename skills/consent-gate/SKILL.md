---
name: consent-gate
description: Fixes a website or vibe-coded app so no ad pixel, analytics, session replay or optional third-party script loads, fetches or sends anything until the visitor opts in - a default-deny consent loader, an honest banner (equal Accept and Reject, unchecked categories), withdrawal, Global Privacy Control, no customer emails or full URLs in tracking payloads, and an accurate privacy notice - then proves it with fresh-visit tests. Use after consent-audit finds tracking before consent, or when someone says "fix my cookie banner", "make tracking wait for consent", "gate my pixel", "add a cookie banner", "make my Lovable app compliant", or pastes the "make sure no tracking pixels load until the user clicks accept" prompt.
---

# Consent gate: nothing optional runs until they say yes

The rule from the video, in one line: **no tracking pixels, analytics or third-party scripts load until the user clicks Accept on the cookie banner.** A banner that shows up while the pixel has already fired doesn't fix anything. This skill builds the waiting part.

Not legal advice. Never write "fully compliant" in code, copy or reports. Say what the app now does and what was tested.

## Before you touch anything

1. **Have an audit.** If there's no `consent-audit` report for this app, run that first. You need the inventory: which vendors, where they start, what they send.
2. **Ask the owner one question per tracker: keep, gate, or remove?** If a tracker isn't used for decisions or ads, removing it beats gating it. A site with only necessary storage needs **no banner at all**; don't add one.
3. **Know what publishing will release.** Hosted builders (Lovable etc.) ship every unpublished change together. List them and get an OK before publishing.
4. **Protect first-party data.** Gating trackers must not touch login, payments, or the app's own database writes (student work, progress, forms). Say so in the report.

## What "gated" means (the checklist the fix must meet)

**Loading**
- [ ] One central loader (`src/lib/consent.ts`, see `references/consent.ts`). No pixel, GTM, gtag, PostHog or replay `<script>` in `index.html`, the root layout or `main.tsx`.
- [ ] Optional scripts are **not fetched**, not just not initialized: dynamic `import()` or script injection happens only after opt-in.
- [ ] No queued events are replayed: pageviews from before consent are dropped, not sent late.
- [ ] Server-side forwarding (Meta Conversions API, `/api/track`, edge functions) checks the same stored choice, sent with the request.
- [ ] Host-injected analytics is turned off at the source (Lovable → Settings → Visitor analytics off; Vercel/Netlify/Cloudflare analytics off), or gated before injection. Removing a script after it loads is too late, because the first request already left.
- [ ] Google Consent Mode (if GA/Ads stay): `gtag('consent','default',{ad_storage:'denied',analytics_storage:'denied',ad_user_data:'denied',ad_personalization:'denied'})` **and** the gtag script itself still waits for opt-in in this skill's default setup. Consent Mode "basic", not "advanced", because advanced sends cookieless pings before consent.

**The banner**
- [ ] **Accept optional** and **Reject optional** are equally prominent: same size, same style, same click count. Plus a **Settings** option.
- [ ] Category toggles (Analytics, Advertising, and so on) start **unchecked**.
- [ ] Closing the banner (X / Escape) means reject.
- [ ] The choice is saved with a **version** and an **expiry** (6 to 12 months). Changing the vendor list bumps the version and asks again.
- [ ] A persistent **"Privacy choices"** link in the footer reopens settings.
- [ ] Withdrawing stops future calls and deletes app-owned optional cookies and storage (`_ga*`, `_fbp`, `_gcl_au`, `_ttp`, `ph_*`, `ajs_*`, `_hj*`, `_clck`) without touching auth.
- [ ] **Global Privacy Control** (`navigator.globalPrivacyControl === true`) is treated as Reject for advertising/sale/share, and the banner says it was honored.

**What gets sent, even after consent**
- [ ] No emails, phone numbers, names or birth data in pixel or analytics payloads (no Meta advanced matching, no `identify(email)`). Use an opaque ID only if truly needed.
- [ ] URLs are sent without `?query` and `#fragment` (gift codes, reset tokens, search terms). If a vendor can't strip them, remove the vendor.
- [ ] Nothing from quiz answers, chat content, health/finance/birth data, or form fields.
- [ ] **Video pages:** no ad pixel on pages that play lesson or course videos (the federal Video Privacy Protection Act risk), unless counsel says otherwise.

**Notice**
- [ ] A privacy/cookie notice on a public route, linked from the footer and the sign-up/login page, listing the actual vendors and categories. Use only the real operator name and contact email; never invent addresses, DPOs or legal claims.

## How to implement

- **Local code / Claude Code:** copy `references/consent.ts` into the app, register each optional vendor as a `loader`, delete the hard-coded tags, build the banner with the app's own components, and wire the footer link. Keep the diff small and in the app's style.
- **Lovable / Bolt / v0 / Replit (agent-built):** paste the **Fix** prompt from `~/.claude/skills/consent-audit/references/prompts.md` (or the **Remove** prompt). Then verify it yourself; don't trust the agent's summary.

## Prove it (required before saying done)

Run these against the preview, then again on the live URL after publishing. In Claude's built-in browser, use a fresh tab with cleared storage, then `read_network_requests` and `javascript_tool` (`document.cookie`, `localStorage`):

| Test | Pass when |
|---|---|
| Fresh visit, no click | 0 requests to ad, analytics or replay domains; no optional cookies or storage |
| Reject, then 2 page navigations | still 0; banner stays gone; choice saved |
| Accept analytics only | analytics loads; ad pixels don't |
| Reload | choice remembered; no banner |
| Withdraw via footer link | future calls stop; optional cookies cleared; still signed in |
| GPC on (`navigator.globalPrivacyControl` forced true) | advertising denied without a click |
| Client-side navigation (SPA) | no tracker sneaks in on route change |
| Sign in with a test account | no email or user ID in any tracker request |
| Build + type check | pass |

Report: files changed, each test's result with evidence (domains seen or "none"), tests not run and why, unpublished changes shipped with it, and "Not legal advice. Have counsel review if you run ads or serve California/EU visitors."
