'use client';

import { motion } from 'framer-motion';

const cards = [
  { icon: '📊', title: 'Autonomous Performance Monitoring', desc: 'Your OpenClaw agent checks campaign performance on a schedule and alerts you when ROAS drops, CPC spikes, or budgets are about to run out.' },
  { icon: '⚡', title: 'Instant Budget Adjustments', desc: 'Tell your agent "increase budget on all campaigns with ROAS above 4x by 20%" — it executes immediately, no dashboard needed.' },
  { icon: '🛑', title: 'Auto-Pause Underperformers', desc: 'Set rules in plain language: "Pause any ad group spending more than €50 with zero conversions this month." Your agent enforces them automatically.' },
  { icon: '📋', title: 'Weekly Reports on Autopilot', desc: 'Schedule your agent to send you a performance summary every Monday morning — spend, clicks, conversions, ROAS — across all accounts.' },
  { icon: '🔍', title: 'Keyword Intelligence', desc: 'Ask "which keywords are wasting my budget with zero conversions?" and get an instant answer with actionable recommendations.' },
  { icon: '🏢', title: 'Multi-Account Agency Management', desc: 'Manage all your client accounts from one OpenClaw agent. Ask "which client is overspending their monthly budget?" across your entire portfolio.' },
];

export default function OpenClaw() {
  return (
    <section id="openclaw" className="py-20">
      <div className="mx-auto max-w-[1400px] px-8">
        <div className="mb-12 text-center">
          <div className="mb-4 inline-block rounded-full bg-brand-blue/10 px-4 py-1.5 text-sm font-medium text-brand-blue">
            🦾 OpenClaw Integration
          </div>
          <h2 className="font-heading text-3xl font-bold md:text-4xl">Built for OpenClaw agents</h2>
          <p className="mx-auto mt-3 max-w-xl text-brand-text-secondary">
            OpenClaw agents can autonomously manage your Google Ads campaigns — monitoring performance, adjusting budgets, pausing underperformers, and reporting back — without you lifting a finger.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3">
          {cards.map((card, i) => (
            <motion.div
              key={card.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: i * 0.08 }}
              className="rounded-xl border border-white/6 bg-brand-surface p-6 transition-colors hover:border-brand-blue/30"
            >
              <div className="mb-4 text-2xl">{card.icon}</div>
              <h3 className="mb-2 font-heading text-sm font-bold text-white">{card.title}</h3>
              <p className="text-xs leading-relaxed text-white/55">{card.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
