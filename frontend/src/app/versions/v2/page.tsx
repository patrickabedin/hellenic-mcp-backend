// Components used:
// 1. Header — nav with hellenicAI logo, links, CTA button
// 2. Hero — headline, subheadline, CTA buttons, product mockup, Works marquee
// 3. StatsBar — animated stat counters
// 4. Works — scrolling marquee of AI assistants
// 5. UseCases — two-column For Agencies / For Businesses cards
// 6. SeeItInAction — ChatDemo in its own section with prompt chips
// 7. Tools — 25-tool card grid with icons
// 8. SocialProof — testimonial cards
// 9. HowItWorks — 3-step numbered process
// 10. ManagedService — HT agency section
// 11. CTA — blue gradient call-to-action band
// 12. FAQ — accordion FAQ section
// 13. Footer — expanded links

import Header from "@/components/Header";
import Hero from "@/components/Hero";
import StatsBar from "@/components/StatsBar";
import UseCases from "@/components/UseCases";
import SeeItInAction from "@/components/SeeItInAction";
import Tools from "@/components/Tools";
import SocialProof from "@/components/SocialProof";
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
      <StatsBar />
      <UseCases />
      <SeeItInAction />
      <Tools />
      <SocialProof />
      <HowItWorks />
      <ManagedService />
      <CTA />
      <FAQ />
      <Footer />
    </>
  );
}
