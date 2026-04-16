'use client';

import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';
import ChatDemo from './ChatDemo';
import Works from './Works';

export default function Hero() {
  return (
    <section className="relative flex flex-col items-center overflow-hidden px-6 pt-20 pb-4">
      {/* Blue radial glow */}
      <div
        className="pointer-events-none absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 h-[500px] w-[500px] rounded-full"
        style={{
          background: 'radial-gradient(circle, rgba(0, 66, 191, 0.18) 0%, transparent 70%)',
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
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#0042BF] opacity-75" />
          <span className="relative inline-flex h-2 w-2 rounded-full bg-[#0042BF]" />
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
          href="#get-started"
          className="inline-flex h-11 items-center gap-2 rounded-lg bg-[#0042BF] px-6 text-sm font-medium text-white transition-colors hover:bg-[#0035A0]"
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

      {/* Chat Demo — wider, professional */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8, delay: 0.5 }}
        className="mt-10 w-full max-w-2xl"
      >
        <ChatDemo />
      </motion.div>

      {/* Works with — directly below chatbox, tight spacing */}
      <div className="mt-4 w-full">
        <Works />
      </div>
    </section>
  );
}
