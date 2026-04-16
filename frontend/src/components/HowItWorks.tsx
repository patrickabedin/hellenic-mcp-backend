'use client';

import { motion } from 'framer-motion';

const steps = [
  {
    number: '01',
    title: 'Connect',
    description: 'Authenticate your Google Ads account through secure OAuth. Takes 60 seconds.',
    detail: 'One-click setup. No passwords stored — just a secure token handshake between your AI assistant and Google Ads.',
  },
  {
    number: '02',
    title: 'Add MCP URL',
    description: 'Paste the endpoint into Claude Desktop, Cursor, or any MCP-compatible client.',
    detail: "Copy the MCP server URL from your dashboard and paste it into your AI client's configuration. Three lines of JSON.",
  },
  {
    number: '03',
    title: 'Start managing',
    description: 'Ask your AI to pause campaigns, pull ROAS, or generate reports. It just works.',
    detail: 'No dashboard to learn. No spreadsheets to wrangle. Just tell your AI what you need in plain English.',
  },
];

const rowVariants = {
  hidden: { opacity: 0, x: -20 },
  show: { opacity: 1, x: 0, transition: { duration: 0.5 } },
};

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="py-24 px-6">
      <div className="mx-auto max-w-4xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="mb-3 text-center text-4xl font-bold tracking-tight text-white md:text-5xl">
            Three steps to start
          </h2>
          <p className="mb-20 text-center text-base text-white/40">
            From connection to control in minutes
          </p>
        </motion.div>

        <motion.div
          initial="hidden"
          whileInView="show"
          viewport={{ once: true }}
          transition={{ staggerChildren: 0.15 }}
        >
          {steps.map((step, i) => (
            <motion.div
              key={i}
              variants={rowVariants}
              className="flex flex-col md:flex-row md:items-start gap-4 md:gap-12 py-8 first:pt-0 border-t border-white/[0.04]"
            >
              <div className="flex items-baseline gap-4 md:w-48 flex-shrink-0">
                <span className="text-[#3B82F6] text-sm font-mono">{step.number}</span>
                <h3 className="text-2xl font-bold text-white">{step.title}</h3>
              </div>
              <div className="md:pt-1">
                <p className="text-base text-white/55 max-w-md mb-2">{step.description}</p>
                <p className="text-sm text-white/30 max-w-md">{step.detail}</p>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
