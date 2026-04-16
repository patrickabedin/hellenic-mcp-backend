'use client';

import { ExternalLink } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="border-t border-white/[0.06] py-12 px-6">
      <div className="mx-auto max-w-6xl">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-6">
          {/* Left — logo */}
          <div className="flex items-center gap-2">
            <span className="text-sm font-bold text-white">
              hellenic<span className="text-[#3B82F6]">AI</span>
            </span>
            <span className="text-xs text-white/30">Google Ads MCP</span>
          </div>

          {/* Right — links */}
          <div className="flex flex-wrap items-center justify-center gap-6">
            <a
              href="https://hellenicai.com"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-xs text-white/40 hover:text-white transition-colors"
            >
              hellenicAI.com <ExternalLink className="h-3 w-3" />
            </a>
            <a
              href="https://hellenictechnologies.com"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-xs text-white/40 hover:text-white transition-colors"
            >
              Built by Hellenic Technologies <ExternalLink className="h-3 w-3" />
            </a>
            <a
              href="/privacy"
              className="inline-flex items-center gap-1.5 text-xs text-white/40 hover:text-white transition-colors"
            >
              Privacy Policy
            </a>
            <a
              href="/terms"
              className="inline-flex items-center gap-1.5 text-xs text-white/40 hover:text-white transition-colors"
            >
              Terms &amp; Conditions
            </a>
          </div>
        </div>

        {/* Bottom */}
        <div className="mt-8 border-t border-white/[0.04] pt-6 text-center">
          <p className="text-xs text-white/20">
            © 2026 Hellenic Technologies. MIT License.
          </p>
        </div>
      </div>


    </footer>
  );
}
