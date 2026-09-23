import '@/app/globals.css';
import { Navbar } from '@/components/layout/navbar';
import { QueryProvider } from '@/components/providers/query-provider';
import type { Metadata } from 'next';
import type * as React from 'react';

export const metadata: Metadata = {
  title: 'TalentEngine | AI Resume & Job Matching Marketplace',
  description:
    'Next-generation semantic resume matching engine powered by NLP vector embeddings, skill ontology normalization, and min-cost flow talent allocation.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-slate-950 text-slate-100 min-h-screen flex flex-col antialiased selection:bg-blue-600 selection:text-white">
        <QueryProvider>
          <Navbar />
          <main className="flex-1 flex flex-col">{children}</main>
          <footer className="border-t border-slate-900 bg-slate-950/60 py-6 text-center text-xs text-slate-500">
            <div className="container mx-auto px-4">
              <p>
                TalentEngine &copy; {new Date().getFullYear()} &bull; Awesome Dev Pipeline &bull;
                Stack B Modern Full-Stack Web
              </p>
            </div>
          </footer>
        </QueryProvider>
      </body>
    </html>
  );
}
