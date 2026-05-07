import Link from "next/link";
import { EmailCapture } from "@/components/EmailCapture";

export default function Home() {
  return (
    <>
      <Header />

      {/* HERO */}
      <section className="relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0 grid-bg mask-fade opacity-60" />
        <div className="pointer-events-none absolute -left-40 top-0 size-[60vmax] rounded-full bg-white/[0.03] blur-3xl" />

        <div className="relative mx-auto max-w-5xl px-6 pt-24 pb-32 text-center">
          <div className="mx-auto inline-flex items-center gap-2 rounded-full border-hairline bg-white/[0.03] px-4 py-1.5 font-mono text-[10px] uppercase tracking-ultra text-white/70">
            <span className="size-1.5 rounded-full bg-white animate-pulse" />
            Desktop · Windows · MacOS bientôt
          </div>

          <h1 className="mt-7 font-display font-bold uppercase tracking-widest2 text-glow text-[44px] leading-[1.05] sm:text-[68px]">
            Publie tes beats <br />
            <span className="opacity-70">partout</span>, en un clic.
          </h1>

          <p className="mx-auto mt-6 max-w-xl text-[15px] leading-relaxed text-white/70">
            YouTube, Instagram, TikTok, Audiomack — Beat Cash adapte automatiquement
            le format, génère titre + description + tags via IA, et te rend tes 30 minutes
            par beat.
          </p>

          <div className="mt-9 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
            <Link
              href="/pricing"
              className="rounded-xl bg-white px-7 py-4 font-display text-[13px] font-bold tracking-widest2 text-black transition-transform hover:scale-[1.03] active:scale-95"
            >
              VOIR LES TARIFS
            </Link>
            <Link
              href="/download"
              className="rounded-xl border-hairline-hi bg-white/[0.04] px-7 py-4 font-display text-[13px] font-bold tracking-widest2 hover:bg-white/[0.08]"
            >
              TÉLÉCHARGER GRATUIT
            </Link>
          </div>

          <div className="mt-8 font-mono text-[11px] text-white/40">
            Pas de carte requise. Plan gratuit, 3 publications / mois.
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section className="border-t border-white/5 bg-gradient-to-b from-transparent to-white/[0.015] py-24">
        <div className="mx-auto max-w-5xl px-6">
          <div className="mb-14 text-center">
            <div className="font-mono text-[11px] uppercase tracking-ultra text-white/50">— Workflow —</div>
            <h2 className="mt-3 font-display text-3xl font-bold uppercase tracking-widest2">Un beat. Quatre plateformes. Zéro friction.</h2>
          </div>

          <div className="grid grid-cols-1 gap-5 md:grid-cols-3">
            <Feature
              n="01"
              title="Cross-posting natif"
              body="Vidéo MP4 ou MP3+image → Beat Cash adapte le format pour YouTube long, Reels, Shorts, TikTok vertical. Sans réencoder à la main."
            />
            <Feature
              n="02"
              title="SEO IA"
              body="Titre, description, tags YT et caption IG/hashtags générés par Claude depuis ton profil et ton style. Optimisé pour découverte type beat."
            />
            <Feature
              n="03"
              title="Local-first"
              body="Tes tokens, tes mots de passe, tes beats restent sur ton PC. Aucun upload sur nos serveurs. Tu fermes Beat Cash, on n'a rien."
            />
            <Feature
              n="04"
              title="Watch folder"
              body="Glisse un MP4 dans un dossier surveillé. Beat Cash le détecte, génère le SEO, publie automatiquement. (Pro)"
            />
            <Feature
              n="05"
              title="Analytics agrégées"
              body="Vues YT + lectures Audiomack + reach IG dans un seul tableau. Quel beat performe vraiment ? (Pro)"
            />
            <Feature
              n="06"
              title="Scheduled posts"
              body="Programme tes drops à la minute près sur les 4 plateformes. Pas besoin de rester collé devant l'écran. (Pro)"
            />
          </div>
        </div>
      </section>

      {/* FREE PACK */}
      <section className="border-t border-white/5 py-24">
        <div className="mx-auto max-w-2xl px-6 text-center">
          <div className="font-mono text-[11px] uppercase tracking-ultra text-white/50">— Free pack —</div>
          <h2 className="mt-3 font-display text-3xl font-bold uppercase tracking-widest2">50 type beats, gratuits.</h2>
          <p className="mt-4 text-white/70">
            Trap, drill, lo-fi, boom bap, afro. Free for non-profit avec credit.
            Idéal pour tester le workflow Beat Cash sans rien produire toi-même.
          </p>
          <div className="mt-8">
            <EmailCapture />
            <p className="mt-3 font-mono text-[10px] uppercase tracking-ultra text-white/40">
              Pas de spam. Désabonnement en 1 clic.
            </p>
          </div>
        </div>
      </section>

      {/* PRICING TEASER */}
      <section className="border-t border-white/5 py-24">
        <div className="mx-auto max-w-3xl px-6 text-center">
          <h2 className="font-display text-3xl font-bold uppercase tracking-widest2">Free pour toujours. Pro à 14,99 € / mois.</h2>
          <p className="mt-4 text-white/70">
            Le plan gratuit suffit si tu publies moins de 3 beats par mois.
            Au-delà, Pro débloque les 4 plateformes, le SEO IA illimité et les watch folders.
          </p>
          <Link
            href="/pricing"
            className="mt-8 inline-block rounded-xl bg-white px-7 py-4 font-display text-[13px] font-bold tracking-widest2 text-black transition-transform hover:scale-[1.03]"
          >
            COMPARER LES PLANS →
          </Link>
        </div>
      </section>

      <Footer />
    </>
  );
}

/* ─── helpers ─────────────────────────────────────────── */

function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-white/5 bg-black/70 backdrop-blur-xl">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-5">
        <Link href="/" className="flex items-baseline gap-2">
          <span className="font-display text-[26px] font-bold text-white text-glow leading-none">$</span>
          <span className="font-display text-[15px] font-bold tracking-widest2">BEATCASH</span>
        </Link>
        <nav className="flex items-center gap-7 font-mono text-[12px] uppercase tracking-widest2">
          <Link href="/pricing" className="hover:text-white text-white/70">Tarifs</Link>
          <Link href="/download" className="hover:text-white text-white/70">Download</Link>
          <Link href="/login" className="rounded-full border-hairline px-4 py-2 hover:bg-white/[0.04]">Connexion</Link>
        </nav>
      </div>
    </header>
  );
}

function Feature({ n, title, body }: { n: string; title: string; body: string }) {
  return (
    <div className="rounded-2xl border-hairline bg-white/[0.02] p-6 transition-colors hover:border-white/15 hover:bg-white/[0.04]">
      <div className="font-mono text-[11px] tracking-ultra text-white/40">{n}</div>
      <div className="mt-3 font-display text-[14px] font-bold tracking-widest2">{title}</div>
      <p className="mt-3 text-[13px] leading-relaxed text-white/70">{body}</p>
    </div>
  );
}

function Footer() {
  return (
    <footer className="mt-auto border-t border-white/5 py-10">
      <div className="mx-auto flex max-w-5xl flex-col items-center justify-between gap-4 px-6 sm:flex-row">
        <div className="flex items-baseline gap-2">
          <span className="font-display text-[18px] font-bold text-glow leading-none">$</span>
          <span className="font-display text-[12px] font-bold tracking-widest2">BEATCASH</span>
        </div>
        <div className="flex gap-6 font-mono text-[11px] uppercase tracking-ultra text-white/40">
          <Link href="/pricing" className="hover:text-white">Tarifs</Link>
          <Link href="/legal/terms" className="hover:text-white">CGU</Link>
          <Link href="/legal/privacy" className="hover:text-white">Confidentialité</Link>
          <a href="mailto:hello@beatcash.app" className="hover:text-white">Contact</a>
        </div>
      </div>
    </footer>
  );
}
