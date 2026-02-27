import "./globals.css";

import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "importNumpy Dashboard",
  description: "Globe + phase-by-phase pipeline dashboard (latest run)."
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-950 text-slate-100">
        <header className="border-b border-slate-800 bg-slate-950/70 backdrop-blur">
          <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
            <Link href="/" className="text-sm font-semibold tracking-wide">
              importNumpy — Dashboard
            </Link>
            <nav className="flex gap-4 text-sm text-slate-200">
              <Link className="hover:text-white" href="/globe">
                Globe
              </Link>
              <Link className="hover:text-white" href="/pipeline">
                Pipeline
              </Link>
              <Link className="hover:text-white" href="/phases">
                Phases
              </Link>
              <Link className="hover:text-white" href="/analysis">
                Analysis
              </Link>
              <Link className="hover:text-white" href="/ml-diagnostic">
                ML Diagnostic
              </Link>
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-6xl px-4 py-6">{children}</main>
      </body>
    </html>
  );
}

