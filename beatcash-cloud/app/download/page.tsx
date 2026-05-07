import Link from "next/link";

export default function DownloadPage() {
  return (
    <main className="mx-auto w-full max-w-2xl flex-1 px-6 py-20 text-center">
      <Link href="/" className="mb-12 inline-flex items-baseline gap-2">
        <span className="font-display text-[26px] font-bold text-glow leading-none">$</span>
        <span className="font-display text-[15px] font-bold tracking-widest2">BEATCASH</span>
      </Link>

      <div className="font-mono text-[11px] uppercase tracking-ultra text-white/50">— Téléchargement —</div>
      <h1 className="mt-3 font-display text-3xl font-bold uppercase tracking-widest2">Beat Cash desktop</h1>
      <p className="mt-4 text-white/70">Windows 10/11 · 64-bit · ~25 Mo · sans installeur requis pour la version portable.</p>

      <div className="mx-auto mt-10 grid max-w-md grid-cols-1 gap-3">
        <a
          href="#"
          className="rounded-xl bg-white px-7 py-4 font-display text-[13px] font-bold tracking-widest2 text-black"
        >
          ↓ INSTALLEUR (BeatCash_Setup.exe)
        </a>
        <a
          href="#"
          className="rounded-xl border-hairline-hi bg-white/[0.04] px-7 py-4 font-display text-[12px] font-bold tracking-widest2 hover:bg-white/[0.08]"
        >
          ↓ VERSION PORTABLE (.zip)
        </a>
      </div>

      <p className="mt-8 font-mono text-[11px] text-white/40">
        Une fois installé : ouvre Beat Cash → Compte → colle ta license key (Pro) ou continue en mode FREE.
      </p>

      <div className="mt-16 rounded-2xl border-hairline bg-white/[0.02] p-7 text-left">
        <div className="font-mono text-[10px] uppercase tracking-ultra text-white/50">Premiers pas</div>
        <ol className="mt-4 space-y-3 text-[13px] text-white/80">
          <li><span className="font-mono mr-3 text-white/40">01.</span> Connecter ton compte YouTube (OAuth Google)</li>
          <li><span className="font-mono mr-3 text-white/40">02.</span> Connecter Instagram (session ou login)</li>
          <li><span className="font-mono mr-3 text-white/40">03.</span> Connecter TikTok (OAuth)</li>
          <li><span className="font-mono mr-3 text-white/40">04.</span> Drag &amp; drop une vidéo → choisir les plateformes → Publier</li>
        </ol>
      </div>
    </main>
  );
}
