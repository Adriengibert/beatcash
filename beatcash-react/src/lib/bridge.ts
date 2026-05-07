/**
 * Pont vers Python via PyWebView. En mode dev navigateur (sans PyWebView),
 * on retourne des stubs pour ne pas casser l'UI.
 */

declare global {
  interface Window {
    pywebview?: { api: Record<string, (...args: any[]) => Promise<any>> };
  }
}

const inWebview = () =>
  typeof window !== "undefined" && !!window.pywebview?.api;

async function call<T = any>(method: string, ...args: any[]): Promise<T> {
  if (inWebview()) {
    return (window.pywebview!.api as any)[method](...args);
  }
  // Stubs en mode dev navigateur
  return stubs[method]?.(...args) as T;
}

const stubs: Record<string, (...args: any[]) => any> = {
  ping: () => ({ ok: true, msg: "stub", beta: false }),
  env: () => ({ beta: false, modules: {} }),
  select_file: () => "",
  // YouTube
  youtube_status: () => ({ connected: false }),
  connect_youtube: () => ({ ok: false, error: "PyWebView requis" }),
  disconnect_youtube: () => ({ ok: true }),
  // Instagram
  instagram_status: () => ({ connected: false }),
  connect_instagram: () => ({ ok: false, error: "PyWebView requis" }),
  disconnect_instagram: () => ({ ok: true }),
  // TikTok
  tiktok_status: () => ({ connected: false }),
  connect_tiktok: () => ({ ok: false, error: "PyWebView requis" }),
  tiktok_connect: () => ({ ok: false, error: "PyWebView requis" }),
  tiktok_disconnect: () => ({ ok: true }),
  tiktok_publish: () => ({ ok: false, error: "stub" }),
  // Publish
  publish: () => ({ ok: false, results: {} }),
  // License
  license_status: () => ({ plan: "FREE", key: null, online: false }),
  license_activate: (key: string) => ({ ok: false, error: "PyWebView requis", key }),
  license_recheck: () => ({ plan: "FREE" }),
  license_deactivate: () => ({ ok: true }),
  is_pro: () => false,
};

type ConnStatus = { connected: boolean; cached?: boolean; expired?: boolean; error?: string };
type ActionResult = { ok: boolean; error?: string };
type PublishOpts  = { file: string; title?: string; description?: string; targets: string[]; yt_privacy?: string; tt_privacy?: string; ig_caption?: string };

export const bridge = {
  ping: () => call<{ ok: boolean; msg: string; beta: boolean }>("ping"),
  env: () => call<{ beta: boolean; log_path: string; modules: Record<string, boolean> }>("env"),
  selectFile: (kind?: "video" | "audio" | "image") => call<string>("select_file", kind),

  // YouTube
  youtubeStatus:    () => call<ConnStatus>("youtube_status"),
  connectYoutube:   () => call<ActionResult>("connect_youtube"),
  disconnectYoutube:() => call<ActionResult>("disconnect_youtube"),

  // Instagram
  instagramStatus:    () => call<ConnStatus>("instagram_status"),
  connectInstagram:   (login?: string, password?: string, code?: string) =>
    call<ActionResult>("connect_instagram", login, password, code),
  disconnectInstagram:() => call<ActionResult>("disconnect_instagram"),

  // TikTok
  tiktokStatus:    () => call<ConnStatus>("tiktok_status"),
  tiktokConnect:   () => call<ActionResult>("connect_tiktok"),
  tiktokDisconnect:() => call<ActionResult>("tiktok_disconnect"),
  tiktokPublish:   (file: string, title: string, opts?: object) =>
    call<ActionResult>("tiktok_publish", file, title, opts),

  // Publish (orchestré)
  publish: (opts: PublishOpts) =>
    call<{ ok: boolean; error?: string; results: Record<string, ActionResult & { url?: string; id?: string }> }>("publish", opts),

  // License
  licenseStatus: () => call<{
    plan: "FREE" | "PRO";
    key: string | null;
    valid_until: number | null;
    needs_recheck: boolean;
    online: boolean;
    device_id?: string;
  }>("license_status"),
  licenseActivate: (key: string) =>
    call<{ ok: boolean; error?: string; plan?: "FREE" | "PRO"; key?: string }>("license_activate", key),
  licenseRecheck: () => call("license_recheck"),
  licenseDeactivate: () => call<{ ok: boolean }>("license_deactivate"),
  isPro: () => call<boolean>("is_pro"),
};

export const isInWebview = inWebview;
