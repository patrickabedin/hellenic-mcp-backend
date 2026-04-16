'use client';

import { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const questions = [
  {
    q: 'Is this really free?',
    a: 'Yes — completely. The Google Ads MCP Server is open source (MIT license) and free forever. There are no hidden tiers, no usage limits, and no credit card required. We built it to demonstrate what\'s possible when AI meets performance marketing. Use it, fork it, build on it.',
  },
  {
    q: 'Which AI assistants does it work with?',
    a: 'Any MCP-compatible assistant: Claude Desktop, Claude.ai, ChatGPT (Plus/Team), Gemini, Cursor, Windsurf, OpenClaw, and hellenicAI. If your AI platform supports MCP Streamable HTTP transport, it works. New platforms are adding MCP support every month.',
  },
  {
    q: 'Is my Google Ads data safe?',
    a: 'Your data flows directly between your AI assistant and the Google Ads API — we act as an authenticated relay, not a data store. We don\'t log your campaign data, store your ad performance, or share anything with third parties. OAuth tokens are session-scoped and never persisted beyond your session.',
  },
  {
    q: 'Do I need to know how to code?',
    a: 'No. The setup takes about 3 minutes: connect your Google Ads account via OAuth, copy your session ID, paste one config block into your AI client. That\'s it. No terminal, no npm, no config files to edit by hand — unless you want to (we support that too).',
  },
  {
    q: 'What can I actually do with it?',
    a: 'Everything you\'d normally do in the Google Ads dashboard — but in plain English. List and manage campaigns, ad groups, and keywords. Pull ROAS, CTR, CPC, and conversion reports. Pause underperforming campaigns. Adjust bids. Create new ad groups. Generate performance summaries. Ask "which campaigns are wasting budget?" and get a real answer.',
  },
  {
    q: 'How is this different from the Google Ads dashboard?',
    a: 'The dashboard shows you data. The MCP lets you act on it through conversation. Instead of clicking through 6 screens to pause a campaign, you say "pause all campaigns with ROAS below 1.5x this month" and it\'s done. Instead of exporting a CSV to analyze, you ask "what\'s my best-performing ad group by conversion value?" and get the answer instantly.',
  },
  {
    q: 'Can I manage multiple Google Ads accounts (MCC)?',
    a: 'Yes. If you have a Manager Account (MCC), you can connect it and access all child accounts through a single session. Ask your AI to "list all accounts" and then work across them in the same conversation.',
  },
  {
    q: 'What\'s the difference between using this and hiring an agency?',
    a: 'The MCP gives you the tools. An agency gives you the strategy, the expertise, and the execution. The MCP is great for teams who already know what they\'re doing and want to move faster. If you want a team that combines senior performance marketers, BI analysts, web analytics engineers, and AI specialists — that\'s what Hellenic Technologies does. The MCP is how we show you what that looks like.',
  },
  {
    q: 'Can I automate Google Ads management with this?',
    a: 'Yes — especially with OpenClaw or hellenicAI. You can set up scheduled agents that check campaign performance daily, pause underperformers, flag anomalies, and send you a summary. Full autonomous Google Ads management without a dashboard.',
  },
  {
    q: 'What does Hellenic Technologies actually do?',
    a: 'We\'re a digital performance agency with four specialist teams: Web Analytics & Server-Side Tracking, Business Intelligence (BigQuery, Clickhouse, Metabase), AI & Marketing Technology (we build tools like this MCP), and Google Ads & Meta Ads Performance. We work with businesses that want data-driven results — not agencies that guess. The MCP is free because we want you to see the difference.',
  },
];

const containerVariants = {
  hidden: {},
  show: {
    transition: {
      staggerChildren: 0.06,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4 } },
};

export default function FAQ() {
  const [open, setOpen] = useState<number | null>(null);

  return (
    <section id="faq" className="border-t border-white/6 py-20 px-6">
      <div className="mx-auto max-w-2xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="mb-10 text-center"
        >
          <div className="mb-3 text-xs font-semibold uppercase tracking-wider text-brand-text-secondary">
            FAQ
          </div>
          <h2 className="font-heading text-3xl font-bold text-white">
            Frequently asked questions
          </h2>
        </motion.div>

        <motion.div
          className="divide-y divide-[#27272A]"
          variants={containerVariants}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true }}
        >
          {questions.map((item, i) => (
            <motion.div key={i} variants={itemVariants}>
              <button
                onClick={() => setOpen(open === i ? null : i)}
                className="flex w-full items-center justify-between py-5 text-left"
              >
                <span className="pr-4 text-sm font-medium text-white">{item.q}</span>
                <ChevronDown
                  className={`h-4 w-4 flex-shrink-0 text-white/30 transition-transform duration-200 ${
                    open === i ? 'rotate-180' : ''
                  }`}
                />
              </button>
              <AnimatePresence>
                {open === i && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="overflow-hidden"
                  >
                    <p className="pb-5 text-sm leading-relaxed text-[#A1A1AA]">
                      {item.a}
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
