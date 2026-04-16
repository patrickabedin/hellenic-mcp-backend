// Components used (21):
// 1. Header — nav with logo, links, CTA button
// 2. Hero — headline, subheadline, CTA buttons, ChatDemo, Works marquee
// 3. ChatDemo — animated typewriter chat conversation demo
// 4. Works — scrolling marquee of AI assistants
// 5. UseCases — two-column For Agencies / For Businesses cards
// 6. Tools — 22-tool numbered grid
// 7. HowItWorks — 3-step numbered process
// 8. CTA — blue gradient call-to-action band
// 9. FAQ — accordion FAQ section
// 10. Footer — links, copyright
// 11. motion.div (framer-motion) — scroll animations
// 12. AnimatePresence (framer-motion) — exit animations
// 13. Send (lucide-react) — send icon in chat
// 14. ChevronDown (lucide-react) — FAQ accordion arrow
// 15. Check (lucide-react) — checkmark icons
// 16. Zap (lucide-react) — lightning bolt icons
// 17. Shield (lucide-react) — shield icons
// 18. BarChart3 (lucide-react) — chart icons
// 19. Globe (lucide-react) — globe icons
// 20. Settings (lucide-react) — settings icons
// 21. Sparkles (lucide-react) — sparkle icons

import Header from "@/components/Header";
import Hero from "@/components/Hero";
import UseCases from "@/components/UseCases";
import Tools from "@/components/Tools";
import HowItWorks from "@/components/HowItWorks";
import ManagedService from "@/components/ManagedService";
import CTA from "@/components/CTA";
import FAQ from "@/components/FAQ";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <>
      <Header />
      <Hero />
      <UseCases />
      <Tools />
      <HowItWorks />
      <ManagedService />
      <CTA />
      <FAQ />
      <Footer />
    </>
  );
}
