'use client';

import { motion } from 'framer-motion';

const capabilities = [
  { icon: '🔍', title: 'Web Analytics & Server-Side Tracking', desc: 'Senior Web Analytics teams specializing in server-side tracking and sophisticated attribution logic — connecting every touchpoint to revenue impact.' },
  { icon: '📊', title: 'Business Intelligence', desc: 'Dedicated BI team with deep expertise in BigQuery, Clickhouse, and Metabase — turning raw data into actionable business insights.' },
  { icon: '🤖', title: 'AI & Marketing Technology', desc: 'AI teams focused on the business and marketing perspective — like the Google Ads MCP Server — bridging cutting-edge AI with real marketing outcomes.' },
  { icon: '🎯', title: 'Google Ads & Meta Ads Performance', desc: 'Senior performance marketers who leverage the full power of analytics, BI, and AI to deliver outstanding results.' },
];

export default function About() {
  return (
    <section id="about" className="border-t border-white/6 bg-brand-surface py-20">
      <div className="mx-auto max-w-[1400px] px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="mb-14 text-center"
        >
          <h2 className="font-heading text-3xl font-bold md:text-4xl">About Hellenic Technologies</h2>
          <p className="mt-3 text-brand-text-secondary">The team behind hellenicAI</p>
          <div className="mx-auto mt-4 h-[3px] w-12 rounded-full bg-brand-blue" />
        </motion.div>

        <div className="mx-auto mb-12 grid max-w-[1100px] grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-4">
          {capabilities.map((cap, i) => (
            <motion.div
              key={cap.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.08 }}
              className="rounded-xl border border-white/6 bg-white/[0.03] p-7 transition-colors hover:border-brand-blue/40"
            >
              <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-lg bg-brand-blue/12 text-xl">
                {cap.icon}
              </div>
              <h3 className="mb-2 font-heading text-sm font-bold text-white">{cap.title}</h3>
              <p className="text-xs leading-relaxed text-white/55">{cap.desc}</p>
            </motion.div>
          ))}
        </div>

        {/* Results callout */}
        <div className="mx-auto mb-10 max-w-[860px] rounded-xl border border-brand-blue/20 bg-brand-blue/5 px-9 py-7 text-center">
          <p className="text-base leading-relaxed text-white/90">
            Businesses switching to Hellenic Technologies to manage their Google Ads and Meta Ads typically see{' '}
            <strong className="font-bold text-brand-blue">up to 8x more revenue</strong> while decreasing ad costs and frustrations.
          </p>
        </div>

        <div className="text-center">
          <a
            href="https://hellenictechnologies.com"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block rounded-lg bg-brand-blue px-8 py-3.5 text-sm font-semibold text-white transition-colors hover:bg-brand-blue-dark"
          >
            Learn more at hellenictechnologies.com →
          </a>
        </div>
      </div>
    </section>
  );
}
