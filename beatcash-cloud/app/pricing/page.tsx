import Link from "next/link";
import { PricingCard } from "@/components/PricingCard";

export default function PricingPage() {
  return (
    <>
      <header className="sticky top-0 z-50 border-b border-white/5 bg-black/70 backdrop-blur-xl">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-5">
          <Link href="/" className="flex items-baseline gap-2">
            <span className="font-display text-[26px] font-bold text-white text-glow leading-none">$</span>
            <span className="font-display text-[15px] font-bold tracking-widest2">BEATCASH</span>
          </Link>
          <Link href="/login" className="font-mono text-[12px] uppercase tracking-widest2 rounded-full border-hairline px-4 py-2 hover:bg-white/[0.04]">Connexion</Link>
        </div>
      </header>

      <section className="mx-auto max-w-5xl px-6 py-24">
        <div className="text-center">
          <div className="font-mono text-[11px] uppercase tracking-ultra text-white/50">— Tarifs —</div>
          <h1 className="mt-3 font-display text-4xl font-bold uppercase tracking-widest2 text-glow">Choisis ton plan.</h1>
          <p className="mt-4 text-white/70">Simple. Transparent. Annule quand tu veux.</p>
        </div>

        <div className="mt-14 grid grid-cols-1 gap-5 md:grid-cols-3">
          <PricingCard
            name="Free"
            price="0 €"
            period="à vie"
            features={[
              "3 publications / mois",
              "2 plateformes (YouTube + 1 au choix)",
              "SEO basique (templates)",
              "Stockage local",
              "Mises à jour gratuites",
            ]}
          />
          <PricingCard
            name="Pro · mensuel"
            price="14,99 €"
            period="mois"
            plan="pro_monthly"
            highlight
            features={[
              "Publications illimitées",
              "4 plateformes (YT + IG + TikTok + Audiomack)",
              "SEO IA (Claude) illimité",
              "1 watch folder automatique",
              "Analytics 30 jours",
              "Programmation des posts",
              "Support prioritaire",
            ]}
          />
          <PricingCard
            name="Pro · annuel"
            price="119 €"
            period="an"
            plan="pro_yearly"
            features={[
              "Tout de Pro mensuel",
              "→ 2 mois gratuits",
              "5 watch folders",
              "Analytics 12 mois",
              "Bulk operations (jusqu'à 50)",
              "Export comptable",
            ]}
          />
        </div>

        {/* FAQ */}
        <div className="mt-24">
          <div className="text-center">
            <div className="font-mono text-[11px] uppercase tracking-ultra text-white/50">— FAQ —</div>
            <h2 className="mt-3 font-display text-2xl font-bold uppercase tracking-widest2">Questions fréquentes</h2>
          </div>

          <div className="mx-auto mt-10 max-w-2xl space-y-3">
            <Faq q="Comment fonctionne l'essai ?">
              Plan Free actif tout de suite, sans carte. Tu peux upgrader vers Pro à tout moment.
              Annule en 1 clic depuis ton compte si Pro ne te sert pas — pas d'engagement.
            </Faq>
            <Faq q="Mes tokens YouTube/Instagram sont-ils sécurisés ?">
              Oui. Beat Cash est local-first : tes tokens OAuth restent stockés sur ton ordinateur,
              jamais envoyés sur nos serveurs. On ne sait pas combien de vues tu fais ni qui tu es,
              au-delà de ton email Pro.
            </Faq>
            <Faq q="Si TikTok casse son API, vous corrigez ?">
              Oui — c'est inclus dans Pro. Les APIs des plateformes changent souvent (3-5 fois par an
              pour TikTok), Beat Cash absorbe les changements via les mises à jour auto.
            </Faq>
            <Faq q="Je peux migrer Free → Pro plus tard ?">
              Oui, instantané. Ta license est mise à jour, le desktop la détecte au prochain démarrage
              (ou en cliquant Vérifier dans le menu).
            </Faq>
            <Faq q="Est-ce que ça remplace DistroKid / TuneCore ?">
              Non. Beat Cash s'adresse aux producteurs qui publient des type beats sur les réseaux
              (YT, IG, TikTok). DistroKid distribue sur Spotify/Apple Music/etc. — c'est complémentaire.
            </Faq>
            <Faq q="Mac / Linux ?">
              Windows pour l'instant. macOS sur la roadmap Q1 — Linux selon la demande.
            </Faq>
          </div>
        </div>
      </section>
    </>
  );
}

function Faq({ q, children }: { q: string; children: React.ReactNode }) {
  return (
    <details className="group rounded-xl border-hairline bg-white/[0.02] p-5 open:border-white/15 open:bg-white/[0.04]">
      <summary className="cursor-pointer list-none font-display text-[13px] font-bold tracking-widest2 marker:hidden">
        <span className="mr-3 inline-block transition-transform group-open:rotate-45">+</span>
        {q}
      </summary>
      <p className="mt-3 pl-7 text-[13px] leading-relaxed text-white/70">{children}</p>
    </details>
  );
}
