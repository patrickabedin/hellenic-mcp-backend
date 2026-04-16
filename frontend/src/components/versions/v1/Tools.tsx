'use client';

import { motion } from 'framer-motion';

const tools = [
  { name: 'list_accessible_customers', desc: 'List all accessible Google Ads customer accounts' },
  { name: 'get_campaign_performance', desc: 'Deep metrics: CTR, CPC, ROAS, conversions — everything that matters' },
  { name: 'create_campaign', desc: 'Create new campaigns with budget, channel type, and bidding strategy' },
  { name: 'update_campaign', desc: 'Modify campaign settings, budgets, and targeting parameters' },
  { name: 'pause_campaign', desc: 'Pause any campaign instantly when you need immediate control' },
  { name: 'enable_campaign', desc: 'Re-enable a paused campaign and get back in the game' },
  { name: 'get_ad_group_performance', desc: 'Ad group-level metrics for granular performance analysis' },
  { name: 'create_ad_group', desc: 'Create ad groups within campaigns with custom bids and targeting' },
  { name: 'update_ad_group', desc: 'Modify ad group settings, bids, and status' },
  { name: 'get_keyword_performance', desc: 'Keyword performance with quality scores — optimize what works' },
  { name: 'add_keywords', desc: 'Add new keywords to ad groups with match types and bids' },
  { name: 'update_keyword_bid', desc: 'Adjust keyword-level bids for optimal cost-per-click' },
  { name: 'get_ad_performance', desc: 'Ad creative performance metrics and engagement data' },
  { name: 'create_responsive_search_ad', desc: 'Build responsive search ads with multiple headlines and descriptions' },
  { name: 'update_ad', desc: 'Modify existing ad copy, headlines, and descriptions' },
  { name: 'get_account_budget', desc: 'View account-level budget allocation and spend pacing' },
  { name: 'get_billing_summary', desc: 'Payment method health, account status, and spend summary' },
  { name: 'get_conversion_actions', desc: 'View all conversion actions and tracking configuration' },
  { name: 'create_conversion_action', desc: 'Set up new conversion tracking for key business events' },
  { name: 'get_audience_insights', desc: 'Audience demographics, interests, and behavior data' },
  { name: 'apply_recommendation', desc: 'One-click apply any optimization recommendation from Google' },
  { name: 'dismiss_recommendation', desc: 'Dismiss irrelevant recommendations to keep your list clean' },
  { name: 'get_recommendations', desc: "Surface Google's AI optimization suggestions for your campaigns" },
  { name: 'generate_keyword_ideas', desc: 'Discover new keyword opportunities based on seed terms' },
  { name: 'get_search_terms_report', desc: 'Actual search queries triggering your ads — real user intent revealed' },
];

const containerVariants = {
  hidden: {},
  show: {
    transition: {
      staggerChildren: 0.05,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4 } },
};

export default function Tools() {
  return (
    <section id="tools" className="py-24 px-6">
      <div className="mx-auto max-w-5xl">
        <h2 className="mb-3 text-center text-3xl font-bold tracking-tight text-white">
          Twenty-five tools. Infinite possibilities.
        </h2>
        <p className="mb-16 text-center text-base text-white/40 max-w-xl mx-auto">
          Complete control over your Google Ads campaigns through simple conversation
        </p>

        <motion.div
          className="grid grid-cols-1 sm:grid-cols-3 gap-3"
          variants={containerVariants}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true }}
        >
          {tools.map((tool, i) => (
            <motion.div
              key={i}
              variants={itemVariants}
              className="bg-[#111113] hover:bg-[#18181B] transition-colors duration-200 rounded-xl p-5"
            >
              <div className="mb-2 text-[#3B82F6] text-xs font-mono">
                {String(i + 1).padStart(2, '0')}
              </div>
              <div className="mb-1.5 text-sm font-semibold text-white">{tool.name}</div>
              <div className="text-xs text-white/40 leading-relaxed">{tool.desc}</div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
