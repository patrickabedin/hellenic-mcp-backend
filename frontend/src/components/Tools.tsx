'use client';

import { motion } from 'framer-motion';
import {
  Users,
  BarChart3,
  Megaphone,
  Pencil,
  Pause,
  Play,
  LayoutList,
  PlusCircle,
  PenLine,
  Search,
  DollarSign,
  BadgePercent,
  FileText,
  PenTool,
  Wallet,
  CreditCard,
  Target,
  PlusSquare,
  UsersRound,
  Lightbulb,
  XCircle,
  Sparkles,
  KeyRound,
  Filter,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

const tools: { name: string; desc: string; icon: LucideIcon }[] = [
  { name: 'list_accessible_customers', desc: 'Browse all Google Ads accounts you have access to', icon: Users },
  { name: 'get_campaign_performance', desc: 'Deep metrics: CTR, CPC, ROAS, conversions — everything that matters', icon: BarChart3 },
  { name: 'create_campaign', desc: 'Launch campaigns with budget, channel type, and bidding strategy', icon: Megaphone },
  { name: 'update_campaign', desc: 'Modify campaign settings, budgets, and targeting parameters', icon: Pencil },
  { name: 'pause_campaign', desc: 'Pause any campaign instantly when you need immediate control', icon: Pause },
  { name: 'enable_campaign', desc: 'Re-enable a paused campaign and get back in the game', icon: Play },
  { name: 'get_ad_group_performance', desc: 'Ad group-level metrics for granular performance analysis', icon: LayoutList },
  { name: 'create_ad_group', desc: 'Build ad groups within campaigns with custom bids and targeting', icon: PlusCircle },
  { name: 'update_ad_group', desc: 'Modify ad group settings, bids, and status', icon: PenLine },
  { name: 'get_keyword_performance', desc: 'Keyword performance with quality scores — optimize what works', icon: Search },
  { name: 'add_keywords', desc: 'Add new keywords to ad groups with match types and bids', icon: KeyRound },
  { name: 'update_keyword_bid', desc: 'Adjust keyword-level bids for optimal cost-per-click', icon: DollarSign },
  { name: 'get_ad_performance', desc: 'Ad creative performance metrics and engagement data', icon: BadgePercent },
  { name: 'create_responsive_search_ad', desc: 'Build responsive search ads with multiple headlines and descriptions', icon: FileText },
  { name: 'update_ad', desc: 'Modify existing ad copy, headlines, and descriptions', icon: PenTool },
  { name: 'get_account_budget', desc: 'View account-level budget allocation and spend pacing', icon: Wallet },
  { name: 'get_billing_summary', desc: 'Payment method health, account status, and spend summary', icon: CreditCard },
  { name: 'get_conversion_actions', desc: 'View all conversion actions and tracking configuration', icon: Target },
  { name: 'create_conversion_action', desc: 'Set up new conversion tracking for key business events', icon: PlusSquare },
  { name: 'get_audience_insights', desc: 'Audience demographics, interests, and behavior data', icon: UsersRound },
  { name: 'apply_recommendation', desc: 'One-click apply any optimization recommendation from Google', icon: Lightbulb },
  { name: 'dismiss_recommendation', desc: 'Dismiss irrelevant recommendations to keep your list clean', icon: XCircle },
  { name: 'get_recommendations', desc: "Surface Google's AI optimization suggestions for your campaigns", icon: Sparkles },
  { name: 'generate_keyword_ideas', desc: 'Discover new keyword opportunities based on seed terms', icon: KeyRound },
  { name: 'get_search_terms_report', desc: 'Actual search queries triggering your ads — real user intent revealed', icon: Filter },
];

const containerVariants = {
  hidden: {},
  show: {
    transition: {
      staggerChildren: 0.04,
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
        <p className="mb-16 text-center text-base text-[#A1A1AA] max-w-xl mx-auto">
          Complete control over your Google Ads campaigns through simple conversation
        </p>

        <motion.div
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
          variants={containerVariants}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true }}
        >
          {tools.map((tool, i) => (
            <motion.div
              key={i}
              variants={itemVariants}
              className="group rounded-xl border border-white/[0.06] bg-[#111111] p-5 transition-all duration-200 hover:border-white/[0.12] hover:-translate-y-0.5"
            >
              <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-lg bg-[#3B82F6]/10">
                <tool.icon className="h-4 w-4 text-[#3B82F6]" />
              </div>
              <div className="mb-1.5 font-mono text-xs text-white/70">{tool.name}</div>
              <div className="text-xs text-[#A1A1AA] leading-relaxed">{tool.desc}</div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
