# Consent Before Tracking: Claude skill pack

Vibe coding gets you a working app in an afternoon. It can also get you sued. The common mistake: a tracking pixel from Meta, Google or TikTok that starts the moment the page opens, **before** the visitor clicks Accept. In California, tracking before consent can be treated as wiretapping, at up to $5,000 per violation. A cookie banner doesn't protect you if the pixel has already fired. **Having a banner and waiting for permission are two different things.**

These three Claude skills check your app for that mistake, fix it, and give you a quick check to run before every publish.

**[⬇️ Download the pack](https://github.com/shannonmcgivney/consent-before-tracking/releases/latest/download/Consent-Before-Tracking-Pack-UNZIP-FIRST.zip)** (or grab just the 3 skill zips from [`claude-ai-uploads/`](claude-ai-uploads/)).

## What's inside

| Skill | What it does |
|---|---|
| `consent-preflight` | **Start here.** 10 pass/fail checks before you publish: does anything track people before they click Accept? |
| `consent-audit` | Finds every pixel, analytics tool, session recorder and third-party script, where it starts, and whether it waits for consent. Read-only. Includes a code scanner and paste-ready prompts for Lovable, Bolt, v0 and Replit |
| `consent-gate` | The fix: nothing optional loads until the visitor says yes, a fair banner (Reject as easy as Accept), a way to change your mind, no customer emails sent to trackers, and tests that prove it |

## Install

### Option A: Claude.ai or the Claude desktop app

> **Don't upload the pack zip itself.** Claude takes one skill per file, so uploading the whole pack shows "Zip cannot contain nested zip files." Unzip the pack first, then upload the 3 small zips inside.

1. **Unzip** the pack you downloaded (double-click it on a Mac; on Windows, right-click → *Extract All*).
2. Open the `claude-ai-uploads/` folder inside. It has 3 zips, one per skill.
3. In Claude, go to **Customize → Skills**, click **+ Add → Upload skill**.
4. Select all 3 zips at once, then click **Upload**. If only one goes in at a time, repeat for each zip.
5. Check **Customize → Skills → Yours**: you should see all 3, each switched on.
6. Start a new chat and type: **"Run a privacy preflight on my app"** and give it your site's URL.

### Option B: Claude Code

```bash
cp -R skills/* ~/.claude/skills/
```

Or install the whole folder as a plugin (it already has `.claude-plugin/plugin.json`). In Claude Code the audit can also scan your code:

```bash
python3 ~/.claude/skills/consent-audit/scripts/scan_trackers.py path/to/your-app
```

## How to use it

- **Before you publish:** "Run a privacy preflight on https://my-app.lovable.app"
- **Full check:** "Audit my app for tracking that runs before cookie consent."
- **Fix it:** "Make sure no tracking pixels, analytics, or third-party scripts load until the user clicks Accept on my cookie banner." (That one sentence is the heart of it.)
- **Not running ads yet?** You probably don't need a pixel yet. No tracker means no banner and nothing to get wrong.

## What it won't do

These are engineering checks, not legal advice. The skills never tell you you're "compliant". They tell you what loads, what's sent, and what was tested. If you run ads, sell to California or EU visitors, or put pixels on pages with video, have a lawyer look too.

## Credit

Based on Dr. Erin Toussaint Jacques's (@dr.erinjacques) Instagram reel on tracking-pixel lawsuits and vibe coding. The skill text, checklists, scanner and code are original material by McGivney Media.
