---
name: consent-audit
description: Audits a website or vibe-coded app (Lovable, Bolt, v0, Replit, Next.js, React, plain HTML) for tracking that loads or sends data BEFORE the visitor agrees in the cookie banner - ad pixels (Meta, Google, TikTok, LinkedIn), Google Tag Manager, analytics, session replay, chat widgets, embeds, hosting-injected analytics, and customer emails or IDs sent to trackers. Read-only - a code scan plus a live fresh-visit network check - ending in an inventory and a minimal fix list. Use when someone asks "is my app compliant", "check my cookies", "does my pixel fire before consent", "privacy audit", "am I going to get sued", "check my Lovable apps for tracking", or shares a video or post about tracking-pixel lawsuits.
---

# Consent audit: what runs before anyone clicks Accept?

**The lesson behind this skill** (Dr. Erin Toussaint Jacques, IG reel, Oct 2026): vibe-coded apps are an easy way to get sued, because nobody checks whether the tracking pixel fires before the visitor clicks Accept. A pixel is a small bit of code from Meta, Google and others that tracks what people do on your site. Under California's wiretapping law (CIPA), tracking that starts before consent can be treated as wiretapping, with statutory damages of up to $5,000 per violation, and pixel suits now run into the thousands. **Having a banner and waiting for permission are two different things.** Many sued sites had a banner; the tracking loaded the second the page opened.

So this audit answers one question with evidence: **on a fresh visit, before any click, what loads and what gets sent, and to whom?**

This is an engineering audit, not legal advice. Never tell anyone they are "compliant". Say what was found, what was fixed, what wasn't checked, and that a lawyer should review if they run ads or sell into the EU or California.

## Default: read-only

Change nothing in this skill: no edits, publishing, database or auth changes, new services, or accepting terms. Fixes are `consent-gate`'s job, once the owner agrees.

## Step 1: Inventory the code

If the code is local (or a GitHub clone of a Lovable project), run the scanner:

```bash
python3 ~/.claude/skills/consent-audit/scripts/scan_trackers.py /path/to/app
```

It lists every tracker, pixel, analytics, replay, embed and third-party script signature it finds, by file and line, flags lines that seem to send emails or user IDs, and says whether a consent check appears nearby. A "consent check nearby" note is a lead, not proof. Read the code around each hit to confirm:

- **Where it starts.** `index.html` `<head>`, `main.tsx`, `App.tsx`, `_app`/`layout`, or a provider means it runs on every page, for every visitor.
- **What gates it.** Does the script tag, `import`, or `init()` run only after a stored, affirmative opt-in? A banner that hides itself while `gtag('config')` already ran is **not** a gate.
- **What it sends.** `identify(email)`, `setUser({ email })`, Meta advanced matching (`em`, `ph`), full URLs with `?` query strings or `#` fragments (gift codes, reset tokens, search text), and form fields.
- **Server-side forwarding.** Conversions API, `/api/track`, edge functions posting to Meta/Google/Segment. These must respect the same choice.

If there's no local code (a Lovable project you can only reach in the browser), use the audit-only prompt in `references/prompts.md` inside that project's chat, then verify its report with Step 2.

## Step 2: Check the live site (the part a banner can't fake)

Code can lie by omission (tag managers, hosting add-ons, CMS snippets). Always check the published URL in a **fresh, cookie-free** browser tab:

1. Open the site in a new private context (in Claude's built-in browser: a new tab after clearing storage, or a site never visited there). **Don't click anything.**
2. Read the network requests (`read_network_requests`). Any request to an ad, analytics or replay domain **before a click is a finding**: list the domain, the URL path, and whether it carries identifiers (`fbp`, `_ga`, `cid`, `uid`, `em`, `ttp`).
3. Read cookies and storage via `javascript_tool`: `document.cookie`, `Object.keys(localStorage)`. Note any `_ga`, `_fbp`, `_gcl_au`, `_ttp`, `_hj*`, `ph_*`, `ajs_*`, `_clck` or `_uetsid`.
4. Click **Reject** (or close the banner if there's no reject). Navigate to two more pages. Anything new firing is a finding.
5. Click **Accept** in a fresh context. Confirm the trackers load now, so the gate isn't just broken.
6. Sign in with a test account if one exists (never a real customer's). Check whether the email or user ID leaves in any tracker request.

## Step 3: Check hosting and platform settings

Trackers injected by the host don't appear in the app's code:

- **Lovable:** Project → Settings → **Visitor analytics**. It is on by default; turn it off (or gate it) on every project, including new ones.
- **Vercel** (Web Analytics / Speed Insights), **Netlify** (Analytics), **Cloudflare** (Web Analytics, Zaraz), **Framer/Webflow/Wix/Squarespace** (site settings → custom code / analytics / pixels), **EzyCourse / Systeme / Kajabi** (tracking-code fields, Facebook Pixel field).
- **Tag managers:** open the GTM container and list every tag and its trigger. "All Pages" without a consent condition means it fires before consent.

## Step 4: Sort and report

Classify every item:

| Class | Examples | Rule |
|---|---|---|
| **Necessary** | login session, CSRF, cart, Stripe on the checkout page, fraud/bot checks, saved UI prefs | May run without consent. No banner needed for these alone. |
| **Functional embed** | Mapbox on the map page, YouTube/Vimeo players, Calendly, chat widgets | Load only where used. Prefer click-to-load or privacy modes (youtube-nocookie). |
| **Optional** | ad pixels, GA/GTM, PostHog, Hotjar, Clarity, HeyCatch, session replay, retargeting | Must not load, fetch or initialize until the visitor opts into that category. |

Report format (keep it short and evidence-based):

```
CONSENT AUDIT: <app> (<url>), <date>
Before any click: <N> optional trackers fired  ->  PASS / FAIL

| Vendor | Where it starts (file:line or host setting) | Fires before consent? | Sends identity/URL data? | Class | Minimal fix |

Necessary services (OK without consent): ...
Privacy notice: present/missing, linked from footer? accurate vendor list?
Withdraw choice: is there a persistent "Privacy choices" link?
Global Privacy Control honored? yes/no/untested
Unpublished changes that publishing would also release: ...
Not checked: ...
Not legal advice. Have counsel review if you run ads, serve California/EU visitors, or put pixels on video pages.
```

Then offer `consent-gate` to apply the fixes. If a tracker isn't earning its keep, recommend **removing it** over gating it: no tracker is the cheapest compliance (in real audits, removing an unused analytics tool was often the whole fix).

## Watch-outs from real audits

- **Analytics started from the app's entry file** (`src/main.tsx`) on every page for every visitor, with no consent check, and the login code sent signed-in customers' emails and user IDs to the analytics tool on every sign-in. The tool couldn't strip query strings, so it was removed entirely.
- **Lovable's Visitor analytics** is on by default and is host-injected. It's not in the code.
- **Publishing releases everything unpublished.** Before publishing a privacy fix, list the older unpublished changes it will also ship (login helpers, dependency bumps, payment fixes) and get the owner's OK.
- **Turning off analytics is not the same as turning off data capture.** The app's own database (student work, progress, messages) is first-party and separate. Say so explicitly, because owners worry.
- **Video pages + Meta pixel** add another federal risk (the Video Privacy Protection Act). Course sites with lesson videos should treat any pixel on those pages as high priority.
