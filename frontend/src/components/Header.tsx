'use client';

import { useState, useEffect } from 'react';

export default function Header() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? 'backdrop-blur-xl bg-black/60 border-b border-white/[0.06]'
          : 'bg-transparent'
      }`}
    >
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        {/* Logo */}
        <a href="#" className="flex items-center gap-2">
          <span className="text-base font-bold text-white">
            hellenic<span className="text-[#3B82F6]">AI</span>
          </span>
          <span className="text-xs text-white/40 font-medium">Google Ads MCP</span>
        </a>

        {/* Nav — desktop */}
        <nav className="hidden md:flex items-center gap-8">
          <a href="#features" className="text-sm text-white/50 hover:text-white transition-colors">
            Features
          </a>
          <a href="#how-it-works" className="text-sm text-white/50 hover:text-white transition-colors">
            How It Works
          </a>
          <a href="#faq" className="text-sm text-white/50 hover:text-white transition-colors">
            FAQ
          </a>
        </nav>

        {/* CTA */}
        <a
          href="https://google-ads-mcp.hellenicai.com/mcp"
          className="inline-flex h-9 items-center rounded-lg bg-[#3B82F6] px-4 text-sm font-medium text-white transition-colors hover:bg-[#2563EB]"
        >
          Get Started Free
        </a>
      </div>
    </header>
  );
}
