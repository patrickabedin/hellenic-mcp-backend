'use client';

import { motion } from 'framer-motion';
import { Building2, Store } from 'lucide-react';

const agencyItems = [
  'Alert me every Monday with last week\'s spend vs budget for all client accounts',
  'Flag any campaign whose CPC jumped more than 20% week-over-week',
  'Pause any ad group with CTR below 0.5% and spend above €50 this month',
  'Show me the top 5 search terms driving conversions for Acme Corp this month',
  'Which client campaigns are overspending their monthly budget right now?',
  'Increase the budget for all campaigns tagged \'Black Friday\' by 30%',
];

const businessItems = [
  'Notify me if my main campaign drops below a 3x ROAS',
  'Every Friday, send me a summary: spend, clicks, conversions, ROAS',
  'Pause my brand campaign if daily spend exceeds €200',
  'What keywords are wasting my budget with zero conversions this month?',
  'How does this week\'s performance compare to last week?',
  'Lower the bid on all keywords with Quality Score below 5',
];

const containerVariants = {
  hidden: {},
  show: {
    transition: {
      staggerChildren: 0.15,
    },
  },
};

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5 } },
};

function Column({
  icon: Icon,
  title,
  items,
}: {
  icon: typeof Building2;
  title: string;
  items: string[];
}) {
  return (
    <motion.div
      variants={cardVariants}
      className="bg-[#111113] rounded-2xl p-8 ring-1 ring-white/[0.04]"
    >
      <div className="mb-5 flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#3B82F6]/10">
          <Icon className="h-5 w-5 text-[#3B82F6]" />
        </div>
        <h3 className="text-base font-semibold text-white">{title}</h3>
      </div>
      <ul className="flex flex-col gap-3">
        {items.map((item, i) => (
          <li
            key={i}
            className="flex items-start gap-3 text-sm leading-relaxed text-white/60"
          >
            <span className="mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-[#3B82F6]" />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </motion.div>
  );
}

export default function UseCases() {
  return (
    <section id="features" className="pt-4 pb-24 px-6">
      <div className="mx-auto max-w-5xl">
        <h2 className="mb-3 text-center text-3xl font-bold tracking-tight text-white">
          Built for agencies and businesses
        </h2>
        <p className="mb-16 text-center text-base text-white/40">
          Plain English commands. Real Google Ads actions.
        </p>

        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 gap-6"
          variants={containerVariants}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true }}
        >
          <Column icon={Building2} title="For Agencies" items={agencyItems} />
          <Column icon={Store} title="For Businesses" items={businessItems} />
        </motion.div>
      </div>
    </section>
  );
}
