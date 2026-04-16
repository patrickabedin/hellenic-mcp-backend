'use client';

import { motion } from 'framer-motion';
import { BarChart3, Brain, Target, ArrowRight, CheckCircle2 } from 'lucide-react';

const teams = [
  {
    icon: BarChart3,
    label: 'Web Analytics',
    title: 'Server-Side Tracking & Attribution',
    desc: 'Most agencies track clicks. We track revenue. Our senior analytics team implements server-side tracking, custom attribution models, and cross-channel data pipelines — so every euro you spend is connected to a real business outcome.',
    points: ['Server-side GTM & GA4', 'Custom attribution models', 'Cross-channel revenue mapping', 'BigQuery data warehouse'],
  },
  {
    icon: Brain,
    label: 'Business Intelligence',
    title: 'Data That Drives Decisions',
    desc: 'Raw data is noise. Our BI team turns it into signal. We build dashboards in Metabase and Looker, run cohort analyses, and surface the insights that actually move the needle — not vanity metrics.',
    points: ['BigQuery & Clickhouse pipelines', 'Metabase & Looker dashboards', 'Cohort & LTV analysis', 'Automated weekly reports'],
  },
  {
    icon: Brain,
    label: 'AI & MarTech',
    title: 'AI Built for Marketing Outcomes',
    desc: 'We don&apos;t just use AI — we build it. The Google Ads MCP Server is one example. Our AI teams focus on the business and marketing perspective, bridging cutting-edge models with real campaign performance.',
    points: ['Custom MCP servers (Google Ads, Meta Ads)', 'AI-powered bid strategy automation', 'Predictive audience modeling', 'LLM-powered creative testing'],
  },
  {
    icon: Target,
    label: 'Performance',
    title: 'Google Ads & Meta Ads Management',
    desc: 'Senior performance marketers who use every tool at their disposal — analytics, BI, and AI — to run campaigns that outperform. Not account managers reading dashboards. Strategists who understand your full funnel.',
    points: ['Google Ads & Meta Ads', 'Full-funnel ROAS optimization', 'Creative strategy & testing', 'Monthly strategy reviews'],
  },
];

const containerVariants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.1 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 24 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5 } },
};

export default function ManagedService() {
  return (
    <section id="managed-service" className="border-t border-white/[0.06] py-24 px-6">
      <div className="mx-auto max-w-5xl">

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="mb-4 text-center"
        >
          <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-[#3B82F6]/30 bg-[#3B82F6]/10 px-4 py-1.5 text-xs font-semibold uppercase tracking-wider text-[#3B82F6]">
            Why We Built This
          </div>
          <h2 className="text-3xl font-bold tracking-tight text-white md:text-4xl">
            The MCP is free.<br />
            <span className="text-[#3B82F6]">The expertise behind it isn&apos;t.</span>
          </h2>
          <p className="mx-auto mt-5 max-w-2xl text-base leading-relaxed text-[#A1A1AA]">
            We give away the Google Ads MCP Server because we want you to see how far ahead we are.
            Most digital agencies are still exporting CSVs. We&apos;re building AI that manages campaigns autonomously.
            When you&apos;re ready to hand the wheel to a team that operates at this level — we&apos;re here.
          </p>
        </motion.div>

        {/* Stat bar */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.15 }}
          className="mx-auto mb-16 flex max-w-3xl flex-wrap justify-center gap-8 rounded-2xl border border-white/[0.06] bg-[#111113] px-10 py-7"
        >
          {[
            { value: '8×', label: 'avg. revenue uplift' },
            { value: '40%', label: 'lower cost per acquisition' },
            { value: '23', label: 'AI-powered tools' },
            { value: '100%', label: 'data-driven decisions' },
          ].map((stat) => (
            <div key={stat.label} className="text-center">
              <div className="text-2xl md:text-3xl font-bold text-white">{stat.value}</div>
              <div className="mt-0.5 text-xs text-[#A1A1AA]">{stat.label}</div>
            </div>
          ))}
        </motion.div>

        {/* Team cards */}
        <motion.div
          className="grid grid-cols-1 gap-6 md:grid-cols-2"
          variants={containerVariants}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true }}
        >
          {teams.map((team) => (
            <motion.div
              key={team.title}
              variants={itemVariants}
              className="group rounded-xl border border-white/[0.06] bg-[#111113] p-8 transition-all duration-200 hover:border-[#3B82F6]/30 hover:-translate-y-0.5"
            >
              <div className="mb-5 flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#3B82F6]/10">
                  <team.icon className="h-5 w-5 text-[#3B82F6]" />
                </div>
                <span className="rounded-full border border-[#3B82F6]/20 bg-[#3B82F6]/10 px-3 py-0.5 text-xs font-semibold text-[#3B82F6]">
                  {team.label}
                </span>
              </div>
              <h3 className="mb-3 text-base font-semibold text-white">{team.title}</h3>
              <p className="mb-5 text-sm leading-relaxed text-[#A1A1AA]">{team.desc}</p>
              <ul className="flex flex-col gap-2">
                {team.points.map((point) => (
                  <li key={point} className="flex items-center gap-2.5 text-xs text-white/60">
                    <CheckCircle2 className="h-3.5 w-3.5 flex-shrink-0 text-[#3B82F6]/70" />
                    {point}
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </motion.div>

        {/* CTA strip */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mt-12 flex flex-col items-center gap-4 text-center"
        >
          <p className="text-sm text-[#A1A1AA]">
            Ready to work with a team that builds tools like this for fun?
          </p>
          <a
            href="https://google-ads-mcp.hellenicai.com/mcp"
            className="inline-flex items-center gap-2 rounded-lg bg-[#3B82F6] px-7 py-3 text-sm font-semibold text-white transition-colors hover:bg-[#2563EB]"
          >
            Talk to Hellenic Technologies
            <ArrowRight className="h-4 w-4" />
          </a>
        </motion.div>

      </div>
    </section>
  );
}
