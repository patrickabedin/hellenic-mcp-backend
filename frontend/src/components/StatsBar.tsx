'use client';

import { motion } from 'framer-motion';
import { useEffect, useRef, useState } from 'react';

interface StatItemProps {
  value: number;
  suffix: string;
  label: string;
}

function StatItem({ value, suffix, label }: StatItemProps) {
  const [count, setCount] = useState(0);
  const ref = useRef<HTMLDivElement>(null);
  const hasAnimated = useRef(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !hasAnimated.current) {
          hasAnimated.current = true;
          const duration = 1500;
          const steps = 40;
          const increment = value / steps;
          let current = 0;
          const timer = setInterval(() => {
            current += increment;
            if (current >= value) {
              setCount(value);
              clearInterval(timer);
            } else {
              setCount(Math.floor(current));
            }
          }, duration / steps);
        }
      },
      { threshold: 0.5 }
    );
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [value]);

  return (
    <div ref={ref} className="text-center">
      <div className="text-2xl md:text-3xl font-bold text-white">
        {count}
        {suffix}
      </div>
      <div className="mt-1 text-xs text-[#A1A1AA]">{label}</div>
    </div>
  );
}

export default function StatsBar() {
  const stats = [
    { value: 25, suffix: ' Tools', label: 'Full Google Ads control' },
    { value: 500, suffix: '+', label: 'Agencies trust us' },
    { value: 0, suffix: '', label: 'Free forever' },
    { value: 100, suffix: '%', label: 'Open source' },
  ];

  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6 }}
      className="py-12 px-6"
    >
      <div className="mx-auto max-w-4xl">
        <div className="flex flex-wrap items-center justify-center gap-8 md:gap-0 md:divide-x md:divide-white/[0.06]">
          {stats.map((stat, i) => (
            <div key={i} className="md:flex-1 md:px-8 first:md:pl-0 last:md:pr-0">
              <StatItem value={stat.value} suffix={stat.suffix} label={stat.label} />
            </div>
          ))}
        </div>
      </div>
    </motion.section>
  );
}
