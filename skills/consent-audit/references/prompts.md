# Paste-ready prompts for vibe-coding tools

Use these in Lovable, Bolt, v0, Replit Agent, Cursor or Claude Code when you can't read the code yourself. Always run the **audit** prompt first, read the report, then run the **fix** prompt. Afterwards verify with the live fresh-visit check in `consent-audit` Step 2, since the agent's report isn't proof.

## 1. The one-liner (from the video)

> Make sure no tracking pixels, analytics, or third-party scripts load until the user clicks Accept on my cookie banner.

Good for a quick check on a simple site. For anything with logins, payments or customer data, use the full prompts below.

## 2. Audit only (no changes)

> Privacy/tracking audit only for now; do not edit, publish, migrate databases, change auth, or add services. Inspect this project for advertising pixels, Google/Meta/TikTok/LinkedIn tracking, Google Tag Manager, analytics, session replay, third-party embeds and cookies/storage. Identify exact files, the consent implementation, and anything that can load or send identifiers before opt-in. Distinguish necessary auth/payment/security functions from optional tracking. Check whether a privacy policy and change-consent controls exist. Check whether any customer email, user ID, form answer or full URL (query string or fragment) is sent to a third party. Report a concise inventory and specific minimal fixes, with evidence; do not claim legal compliance. Also identify whether unpublished changes already exist that publishing would release.

## 3. Fix (after the audit, with the owner's OK)

> Implement a focused tracking/privacy hardening pass for this existing published app. Preserve its design, content, auth, payments, user data and core features. Fix any nonessential tracking that starts without explicit consent: centralize a default-deny loader; do not even fetch or initialize optional tracking scripts before an affirmative category opt-in; no pageview/conversion replay of pre-consent events; keep essential auth/security/payment functions working. If optional tracking exists, provide equally prominent "Accept optional" and "Reject optional" choices plus Settings; category toggles unchecked by default; a versioned, time-limited saved choice; persistent "Privacy choices" access in the footer; withdrawal stops future calls and removes app-owned nonessential cookies/storage without touching auth; honor Global Privacy Control by denying advertising/sale/share tracking. Do not add analytics that is absent, and do not add a cookie popup solely for necessary storage. Gate server-side event forwarding the same way; never send sensitive answers, birth data, chat content, contact details or full query strings in tracking payloads. Keep or correct an accurate app-specific privacy/cookie notice and link it, using existing operator/contact details only; do not invent legal facts, promise legal compliance or claim all laws apply. Run build/type checks and consent tests (fresh visit, reject, category accept, reload, withdraw, GPC, client-side navigation) and say which could not be run. Do not publish, revert unrelated unpublished changes, change database/auth policies, accept terms, purchase anything or add paid services. Finish by listing files changed, test evidence and remaining risks.

## 4. Remove instead of gate (when the tracker isn't worth it)

> Remove <vendor> from this app entirely: its package, initialization, identify/track calls, consent code that existed only for it, and any leftover cookies/storage it set (clear them on next load without touching login). Do not replace it with another tracker. If no optional trackers remain, remove the cookie banner and keep an accurate privacy notice that says no analytics or advertising trackers are used. Run build/type checks and confirm with a source search that no <vendor> code or key remains. Do not publish.
