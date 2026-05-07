import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "$ BEATCASH — desktop upload studio for beatmakers",
  description:
    "Publie tes beats sur YouTube + Instagram + TikTok + Audiomack en 1 clic. SEO IA, analytics, cross-posting. Built for type beat producers.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="fr" className="h-full antialiased">
      <body className="min-h-full bg-black text-white font-sans flex flex-col">
        {children}
      </body>
    </html>
  );
}
