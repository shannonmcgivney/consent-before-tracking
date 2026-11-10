/**
 * Default-deny consent loader. Framework-agnostic; works in React/Vite,
 * Next.js (client components), Svelte, or plain TS.
 *
 * Nothing optional is fetched or initialized until the visitor opts into
 * that category. Bump CONSENT_VERSION whenever the vendor list changes.
 *
 * Usage:
 *   registerLoader("analytics", async () => {
 *     const { default: posthog } = await import("posthog-js");
 *     posthog.init(KEY, { autocapture: false, persistence: "localStorage",
 *       sanitize_properties: stripUrls });
 *   });
 *   registerLoader("advertising", () => injectScript("https://connect.facebook.net/en_US/fbevents.js"));
 *   applyStoredConsent();           // call once on app start
 *   // banner buttons:
 *   saveConsent({ analytics: true, advertising: false });
 *   rejectAll();
 *   // footer "Privacy choices" link opens your settings UI; withdrawing:
 *   rejectAll();                    // clears optional storage, keeps auth
 */

export type Category = "analytics" | "advertising" | "functional";
export type Choice = Record<Category, boolean>;

const CONSENT_VERSION = 1;
const STORAGE_KEY = "privacy-choice";
const MAX_AGE_DAYS = 180;

// App-owned optional cookies/storage to clear on reject or withdraw.
// Never list auth/session keys here.
const OPTIONAL_COOKIE_PREFIXES = ["_ga", "_gid", "_gcl_", "_fbp", "_fbc", "_ttp", "_uet", "_clck", "_clsk", "_hj", "ajs_", "ph_", "mp_", "amp_"];
const OPTIONAL_STORAGE_PREFIXES = ["ph_", "ajs_", "mp_", "amp_", "_hj", "posthog", "AMP_"];

const DENY_ALL: Choice = { analytics: false, advertising: false, functional: false };

type Loader = () => void | Promise<void>;
const loaders: Record<Category, Loader[]> = { analytics: [], advertising: [], functional: [] };
const loaded = new Set<Category>();

export function gpcEnabled(): boolean {
  return typeof navigator !== "undefined" && (navigator as any).globalPrivacyControl === true;
}

export function registerLoader(category: Category, loader: Loader): void {
  loaders[category].push(loader);
}

type Stored = { v: number; at: number; choice: Choice };

export function getStoredConsent(): Choice | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const s = JSON.parse(raw) as Stored;
    const expired = Date.now() - s.at > MAX_AGE_DAYS * 864e5;
    if (s.v !== CONSENT_VERSION || expired) return null;
    return s.choice;
  } catch {
    return null; // storage blocked: treat as no choice (deny)
  }
}

/** True when the banner should be shown (no valid saved choice). */
export function needsChoice(): boolean {
  return getStoredConsent() === null;
}

export function saveConsent(choice: Partial<Choice>): void {
  const final: Choice = { ...DENY_ALL, ...choice };
  if (gpcEnabled()) final.advertising = false; // GPC = opt out of sale/share
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ v: CONSENT_VERSION, at: Date.now(), choice: final } satisfies Stored));
  } catch {
    /* storage blocked: choice applies to this page view only */
  }
  apply(final);
}

export function rejectAll(): void {
  saveConsent(DENY_ALL);
  clearOptionalStorage();
  // Scripts already loaded this page view can't be unloaded cleanly:
  // reload so nothing optional keeps running.
  if (loaded.size > 0 && typeof location !== "undefined") location.reload();
}

/** Call once on startup. With no valid saved choice, nothing loads. */
export function applyStoredConsent(): void {
  const choice = getStoredConsent();
  if (choice) apply(choice);
}

function apply(choice: Choice): void {
  (Object.keys(choice) as Category[]).forEach((cat) => {
    if (!choice[cat] || loaded.has(cat)) return;
    loaded.add(cat);
    for (const run of loaders[cat]) {
      Promise.resolve()
        .then(run)
        .catch(() => {
          /* a tracker failing must never break the app */
        });
    }
  });
}

/** Header value for server-side forwarding: send with /api/track etc. */
export function consentHeader(): string {
  const c = getStoredConsent() ?? DENY_ALL;
  return (Object.keys(c) as Category[]).filter((k) => c[k]).join(",") || "none";
}

export function injectScript(src: string, attrs: Record<string, string> = {}): void {
  const s = document.createElement("script");
  s.async = true;
  s.src = src;
  for (const [k, v] of Object.entries(attrs)) s.setAttribute(k, v);
  document.head.appendChild(s);
}

/** Strip query strings and fragments before anything is sent to a vendor. */
export function stripUrl(url: string): string {
  try {
    const u = new URL(url, location.origin);
    return u.origin + u.pathname;
  } catch {
    return url.split(/[?#]/)[0];
  }
}

export function stripUrls<T extends Record<string, unknown>>(props: T): T {
  const out: Record<string, unknown> = { ...props };
  for (const k of Object.keys(out)) {
    const v = out[k];
    if (typeof v === "string" && /^(https?:\/\/|\/)/.test(v)) out[k] = stripUrl(v);
    if (/email|phone|name|birth|answer|message/i.test(k)) delete out[k];
  }
  return out as T;
}

export function clearOptionalStorage(): void {
  try {
    const host = location.hostname;
    const domains = [host, "." + host, "." + host.split(".").slice(-2).join(".")];
    for (const part of document.cookie.split(";")) {
      const name = part.split("=")[0].trim();
      if (!OPTIONAL_COOKIE_PREFIXES.some((p) => name.startsWith(p))) continue;
      for (const d of domains) {
        document.cookie = `${name}=; Max-Age=0; path=/; domain=${d}`;
      }
      document.cookie = `${name}=; Max-Age=0; path=/`;
    }
    for (const store of [localStorage, sessionStorage]) {
      for (const key of Object.keys(store)) {
        if (OPTIONAL_STORAGE_PREFIXES.some((p) => key.startsWith(p))) store.removeItem(key);
      }
    }
  } catch {
    /* storage blocked: nothing to clear */
  }
}
