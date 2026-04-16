'use client';

import { motion } from 'framer-motion';

export default function CTA() {
  return (
    <section className="py-24 px-6">
      <div className="mx-auto max-w-4xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="rounded-2xl bg-gradient-to-br from-[#1d4ed8] to-[#1e3a8a] py-20 px-6 md:px-16 text-center"
        >
          <h2 className="mb-4 text-4xl md:text-5xl font-bold tracking-tight text-white">
            Start managing Google Ads<br />with AI today.
          </h2>
          <p className="mb-10 text-base text-white/70">
            Free forever. Open source. Works with Claude, ChatGPT, and more.
          </p>
          <a
            href="#get-started"
            id="get-started"
            className="inline-flex h-11 items-center rounded-lg bg-white px-8 text-sm font-medium text-[#1d4ed8] transition-colors hover:bg-white/90"
          >
            Get Started Free
          </a>
        </motion.div>
      </div>
    </section>
  );
}
