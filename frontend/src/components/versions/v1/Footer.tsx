'use client';

import { Zap, ExternalLink } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="border-t border-[#27272A] py-12 px-6">
      <div className="mx-auto max-w-6xl">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-6">
          {/* Left */}
          <div className="flex items-center gap-2">
            <div className="h-4 w-4 rounded-full bg-[#0042BF] flex items-center justify-center">
              <Zap className="h-2.5 w-2.5 text-white" />
            </div>
            <span className="text-sm font-semibold text-white">
              Google Ads MCP
            </span>
            <span className="text-xs text-white/30">by hellenicAI</span>
          </div>

          {/* Right */}
          <div className="flex items-center gap-6">
            <a
              href="https://github.com/hellenicai/google-ads-mcp"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-xs text-white/40 hover:text-white transition-colors"
            >
              GitHub <ExternalLink className="h-3 w-3" />
            </a>
            <a
              href="https://hellenicai.com/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-xs text-white/40 hover:text-white transition-colors"
            >
              Docs <ExternalLink className="h-3 w-3" />
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
