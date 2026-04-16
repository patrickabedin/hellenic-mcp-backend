'use client';

import { motion } from 'framer-motion';
import { Megaphone, BarChart3, Zap, Search, PenLine, FileText } from 'lucide-react';

const capabilities = [
  {
    category: 'Campaign Management',
    icon: Megaphone,
    items: [
      'List all campaigns with status, budget, and performance metrics',
      'Pause or enable any campaign, ad group, or individual keyword',
      'Create new campaigns with targeting, budgets, and bidding strategies',
      'Duplicate campaigns across accounts or MCC hierarchies',
      'Change campaign budgets (daily, monthly, shared budgets)',
    ],
  },
  {
    category: 'Performance Analysis',
    icon: BarChart3,
    items: [
      'Pull real-time metrics: clicks, impressions, CTR, CPC, conversions, ROAS',
      'Compare performance across date ranges, campaigns, or segments',
      'Identify top and bottom performers by any metric',
      'Analyze search term reports to find wasted spend',
      'Track conversion paths and attribution across devices',
    ],
  },
  {
    category: 'Bid & Budget Optimization',
    icon: Zap,
    items: [
      'Adjust keyword-level and ad-group-level bids',
      'Apply bid modifiers by device, location, schedule, or audience',
      'Reallocate budget from underperformers to top performers',
      'Set up and manage shared budget portfolios',
      'Recommend bid strategies based on performance trends',
    ],
  },
  {
    category: 'Keyword Research',
    icon: Search,
    items: [
      'Search for new keyword ideas from seed terms',
      'Add or remove keywords from ad groups',
      'Identify negative keywords from search term reports',
      'Analyze keyword quality scores and expected CTR',
      'Find keyword cannibalization across campaigns',
    ],
  },
  {
    category: 'Ad Creative',
    icon: PenLine,
    items: [
      'List all responsive search ads with headlines and descriptions',
      'Create new ad copy variants for A/B testing',
      'Pause underperforming ad variations',
      'Generate ad copy suggestions based on landing page content',
      'Analyze ad strength and improvement recommendations',
    ],
  },
  {
    category: 'Reporting & Alerts',
    icon: FileText,
    items: [
      'Generate formatted performance reports for any date range',
      'Schedule weekly/monthly summaries via cron',
      'Set up alerts when ROAS drops below thresholds',
      'Monitor budget pacing — are you on track to hit monthly targets?',
      'Export data to CSV, JSON, or send directly to Slack',
    ],
  },
];

export default function Capabilities() {
  return (
    <section id="capabilities" className="py-24 px-6">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <motion.h2
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-3xl md:text-4xl font-bold tracking-tight text-white mb-3"
          >
            Everything you can do with Google Ads — in plain English
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-base text-white/40 max-w-xl mx-auto"
          >
            The MCP server exposes the full Google Ads API surface as AI tools.
            No dashboard, no spreadsheets — just ask your AI assistant.
          </motion.p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {capabilities.map((cap, i) => {
            const Icon = cap.icon;
            return (
              <motion.div
                key={cap.category}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: i * 0.06 }}
                className="bg-[#111113] hover:bg-[#18181B] transition-colors duration-200 rounded-xl p-6"
              >
                <div className="flex items-center gap-3 mb-4">
                  <Icon className="h-5 w-5 text-[#3B82F6]" />
                  <h3 className="text-sm font-bold text-white tracking-tight">
                    {cap.category}
                  </h3>
                </div>
                <ul className="space-y-2.5">
                  {cap.items.map((item) => (
                    <li key={item} className="flex items-start gap-2 text-[13px] text-white/40 leading-relaxed">
                      <span className="text-white/15 mt-1 flex-shrink-0">›</span>
                      {item}
                    </li>
                  ))}
                </ul>
              </motion.div>
            );
          })}
        </div>

        {/* Example prompts */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-16 max-w-3xl mx-auto bg-[#111113] rounded-xl p-6"
        >
          <p className="text-xs font-medium text-white/30 tracking-[0.12em] uppercase mb-4">
            Example prompts
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {[
              '"Pause all campaigns with ROAS below 2x"',
              '"Show me my top 10 keywords by conversions this month"',
              '"Increase budget on Brand campaigns by 20%"',
              '"Find negative keywords from search terms with 0 conversions"',
              '"Create a performance report for the last 30 days"',
              '"Which ad groups are spending without converting?"',
              '"Generate 3 new headline variations for my top ad"',
              '"Compare this month\'s ROAS to last month by campaign"',
            ].map((prompt) => (
              <div
                key={prompt}
                className="bg-[#111113] rounded-lg px-4 py-3 text-[13px] text-white/50 font-mono leading-relaxed"
              >
                {prompt}
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}
