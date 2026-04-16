'use client';

import { motion } from 'framer-motion';
import { ArrowRight, BarChart3, MousePointer, TrendingUp } from 'lucide-react';
import Works from './Works';

export default function Hero() {
  return (
    <section className="relative flex flex-col items-center overflow-hidden px-6 pt-20 pb-4">
      {/* Blue radial glow */}
      <div
        className="pointer-events-none absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 h-[500px] w-[500px] rounded-full"
        style={{
          background: 'radial-gradient(circle, rgba(59, 130, 246, 0.15) 0%, transparent 70%)',
        }}
      />

      {/* Badge */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5 }}
        className="mt-8 mb-6 inline-flex items-center gap-2 rounded-full border border-white/[0.08] bg-white/[0.04] px-4 py-1.5"
      >
        <span className="relative flex h-2 w-2">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#3B82F6] opacity-75" />
          <span className="relative inline-flex h-2 w-2 rounded-full bg-[#3B82F6]" />
        </span>
        <span className="text-xs font-medium text-white/60">Offered for free by hellenicAI</span>
      </motion.div>

      {/* Headline */}
      <motion.h1
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6, delay: 0.1 }}
        className="text-center text-4xl sm:text-5xl md:text-6xl font-bold leading-[1.1] tracking-tight text-white max-w-3xl"
      >
        Manage Google Ads
        <br />
        through conversation.
      </motion.h1>

      {/* Subtext */}
      <motion.p
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="mt-5 max-w-xl text-center text-base leading-relaxed text-[#A1A1AA]"
      >
        Connect your Google Ads accounts to Claude, ChatGPT, Gemini, OpenClaw or hellenicAI. Manage campaigns, analyze performance, and optimize budgets through natural language.
      </motion.p>

      {/* CTAs */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6, delay: 0.3 }}
        className="mt-8 flex flex-wrap items-center justify-center gap-4"
      >
        <a
          href="https://google-ads-mcp.hellenicai.com/mcp"
          className="inline-flex h-11 items-center gap-2 rounded-lg bg-[#3B82F6] px-6 text-sm font-medium text-white transition-colors hover:bg-[#2563EB]"
        >
          Connect Google Ads
          <ArrowRight className="h-4 w-4" />
        </a>
        <a
          href="https://github.com/hellenicai/google-ads-mcp"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex h-11 items-center gap-2 rounded-lg border border-white/[0.08] bg-transparent px-6 text-sm font-medium text-white/70 transition-colors hover:bg-white/[0.04] hover:text-white"
        >
          View on GitHub →
        </a>
      </motion.div>

      {/* Product Screenshot Mockup */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8, delay: 0.5 }}
        className="mt-10 w-full max-w-3xl"
      >
        <div className="rounded-xl border border-white/[0.06] bg-[#111113] overflow-hidden shadow-2xl shadow-black/40">
          {/* Browser toolbar */}
          <div className="flex items-center gap-2 border-b border-white/[0.06] bg-[#0a0a0c] px-4 py-3">
            <div className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full bg-[#EF4444]/70" />
              <span className="h-2.5 w-2.5 rounded-full bg-[#F59E0B]/70" />
              <span className="h-2.5 w-2.5 rounded-full bg-[#10B981]/70" />
            </div>
            <div className="ml-4 flex-1 rounded-md bg-white/[0.04] border border-white/[0.06] px-3 py-1.5 text-xs text-white/30 font-mono">
              mcp.hellenicai.com/dashboard
            </div>
          </div>

          {/* Dashboard content */}
          <div className="p-6">
            {/* Top row — metrics */}
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-4">
                <div className="flex items-center gap-2 mb-2">
                  <MousePointer className="h-3.5 w-3.5 text-[#3B82F6]" />
                  <span className="text-xs text-white/40">CTR</span>
                </div>
                <div className="text-2xl font-bold text-white">4.2%</div>
                <div className="text-xs text-[#10B981] mt-1">+0.8% vs last month</div>
              </div>
              <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-4">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="h-3.5 w-3.5 text-[#3B82F6]" />
                  <span className="text-xs text-white/40">ROAS</span>
                </div>
                <div className="text-2xl font-bold text-white">6.8x</div>
                <div className="text-xs text-[#10B981] mt-1">+1.2x vs last month</div>
              </div>
              <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-4">
                <div className="flex items-center gap-2 mb-2">
                  <BarChart3 className="h-3.5 w-3.5 text-[#3B82F6]" />
                  <span className="text-xs text-white/40">Spend</span>
                </div>
                <div className="text-2xl font-bold text-white">$12,400</div>
                <div className="text-xs text-white/30 mt-1">This month</div>
              </div>
            </div>

            {/* Mini chart area */}
            <div className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-4 mb-6">
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-medium text-white/50">Campaign Performance</span>
                <span className="text-xs text-white/30">Last 30 days</span>
              </div>
              {/* Fake chart bars */}
              <div className="flex items-end gap-1.5 h-16">
                {[35, 42, 38, 55, 48, 62, 58, 70, 65, 78, 72, 85, 80, 90, 88].map((h, i) => (
                  <div
                    key={i}
                    className="flex-1 rounded-sm bg-[#3B82F6]/30"
                    style={{ height: `${h}%` }}
                  />
                ))}
              </div>
            </div>

            {/* AI Chat overlay bubble */}
            <div className="flex justify-end">
              <div className="max-w-sm rounded-xl bg-[#3B82F6]/10 border border-[#3B82F6]/20 px-4 py-3">
                <div className="flex items-center gap-2 mb-1.5">
                  <div className="h-4 w-4 rounded-full bg-[#3B82F6] flex items-center justify-center">
                    <span className="text-[8px] font-bold text-white">AI</span>
                  </div>
                  <span className="text-xs font-medium text-[#3B82F6]">AI Assistant</span>
                </div>
                <p className="text-sm text-white/70">
                  &ldquo;Pause all campaigns under $2 ROAS&rdquo;
                </p>
                <div className="mt-2 flex items-center gap-1.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-[#10B981]" />
                  <span className="text-xs text-[#10B981]">3 campaigns paused</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Works with — directly below mockup */}
      <div className="mt-4 w-full">
        <Works />
      </div>
    </section>
  );
}
