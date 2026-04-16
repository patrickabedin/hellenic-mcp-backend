'use client';

import { motion } from 'framer-motion';

const testimonials = [
  {
    quote:
      'We replaced our weekly reporting ritual with a single Claude conversation. Our team saves 6 hours a week on Google Ads analysis alone. The MCP is a game-changer for agencies.',
    name: 'Marcus Lindström',
    role: 'Head of Performance',
    company: 'Nordic Digital Agency',
    initials: 'ML',
    color: 'bg-[#3B82F6]/20 text-[#3B82F6]',
  },
  {
    quote:
      'I told my AI assistant to pause all campaigns with ROAS under 2x and it did it in 10 seconds. What used to take me 30 minutes of clicking through dashboards now takes one sentence.',
    name: 'Sarah Chen',
    role: 'Growth Marketing Lead',
    company: 'ScaleUp Commerce',
    initials: 'SC',
    color: 'bg-[#10B981]/20 text-[#10B981]',
  },
  {
    quote:
      'As a solo founder, I can\'t afford a full-time media buyer. This MCP lets me manage $40K/month in ad spend through ChatGPT. It\'s like having a junior analyst on call 24/7 — for free.',
    name: 'Dimitris Papadopoulos',
    role: 'Founder & CEO',
    company: 'Aegean Eats',
    initials: 'DP',
    color: 'bg-[#F59E0B]/20 text-[#F59E0B]',
  },
];

const containerVariants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.1 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5 } },
};

export default function SocialProof() {
  return (
    <section className="py-24 px-6">
      <div className="mx-auto max-w-5xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="mb-16 text-center"
        >
          <h2 className="text-3xl font-bold tracking-tight text-white mb-3">
            Trusted by agencies and marketers
          </h2>
          <p className="text-base text-[#A1A1AA]">
            Real results from real teams using the MCP every day.
          </p>
        </motion.div>

        <motion.div
          className="grid grid-cols-1 md:grid-cols-3 gap-6"
          variants={containerVariants}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true }}
        >
          {testimonials.map((t, i) => (
            <motion.div
              key={i}
              variants={itemVariants}
              className="rounded-xl border border-white/[0.06] bg-[#111113] p-6 transition-all hover:border-white/[0.12] hover:-translate-y-1"
            >
              {/* Quote */}
              <p className="text-sm leading-relaxed text-white/60 mb-6">
                &ldquo;{t.quote}&rdquo;
              </p>

              {/* Author */}
              <div className="flex items-center gap-3">
                <div
                  className={`flex h-9 w-9 items-center justify-center rounded-full text-xs font-semibold ${t.color}`}
                >
                  {t.initials}
                </div>
                <div>
                  <div className="text-sm font-medium text-white">{t.name}</div>
                  <div className="text-xs text-white/40">
                    {t.role}, {t.company}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
