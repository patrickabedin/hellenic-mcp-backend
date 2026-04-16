'use client';

import { motion } from 'framer-motion';
import ChatDemo from './ChatDemo';

const promptChips = [
  'Pause underperforming campaigns',
  'Show me ROAS by campaign',
  'Increase budget for top performers',
];

export default function SeeItInAction() {
  return (
    <section className="py-24 px-6">
      <div className="mx-auto max-w-3xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="mb-10 text-center"
        >
          <h2 className="text-3xl font-bold tracking-tight text-white mb-3">
            Ask anything. Get results instantly.
          </h2>
          <p className="text-base text-[#A1A1AA]">
            See how natural language becomes real Google Ads actions.
          </p>
        </motion.div>

        {/* Prompt chips */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.15 }}
          className="mb-8 flex flex-wrap items-center justify-center gap-3"
        >
          {promptChips.map((chip, i) => (
            <span
              key={i}
              className="rounded-full border border-white/[0.06] bg-white/[0.03] px-4 py-2 text-xs text-white/50"
            >
              &ldquo;{chip}&rdquo;
            </span>
          ))}
        </motion.div>

        {/* ChatDemo */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, delay: 0.3 }}
        >
          <ChatDemo />
        </motion.div>
      </div>
    </section>
  );
}
