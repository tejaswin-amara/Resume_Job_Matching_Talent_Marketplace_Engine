'use client';

import { Badge } from '@/components/ui/badge';
import { isMockEnabled } from '@/lib/api-client';
import { Bot, BrainCircuit, Briefcase, FileSearch, Sparkles } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import * as React from 'react';

export function Navbar() {
  const pathname = usePathname();
  const [mockActive, setMockActive] = React.useState(true);

  React.useEffect(() => {
    setMockActive(isMockEnabled());
  }, []);

  const navLinks = [
    { href: '/', label: 'Overview', icon: BrainCircuit },
    { href: '/recruiter/candidates', label: 'Match Studio', icon: FileSearch },
    { href: '/recruiter/post-job', label: 'Post Job', icon: Briefcase },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800 bg-slate-950/80 backdrop-blur-md">
      <div className="container mx-auto flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Brand */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-500 shadow-md shadow-blue-500/20 group-hover:scale-105 transition-transform">
            <Bot className="h-5 w-5 text-white" />
          </div>
          <div className="flex flex-col">
            <span className="text-base font-bold tracking-tight text-white group-hover:text-blue-400 transition-colors">
              TalentEngine
            </span>
            <span className="text-[10px] font-medium tracking-wider text-slate-400 uppercase">
              Semantic Matching
            </span>
          </div>
        </Link>

        {/* Navigation */}
        <nav className="flex items-center gap-1 sm:gap-2">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs sm:text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30'
                    : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{link.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Engine Status Badge */}
        <div className="flex items-center gap-2">
          <Badge
            variant={mockActive ? 'secondary' : 'success'}
            className="hidden sm:flex items-center gap-1 text-[11px] font-mono py-1 px-2.5 border-slate-800"
          >
            <Sparkles className="h-3 w-3 text-blue-400" />
            <span>{mockActive ? 'Mock Engine' : 'Python NLP Active'}</span>
          </Badge>
        </div>
      </div>
    </header>
  );
}
