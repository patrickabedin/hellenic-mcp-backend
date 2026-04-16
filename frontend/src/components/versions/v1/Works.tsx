'use client';

const row1 = [
  'Claude', 'GPT-4o', 'Gemini', 'Mistral', 'Llama', 'Perplexity',
  'Cursor', 'Windsurf', 'Zed', 'VS Code', 'Neovim',
];

const row2 = [
  'Continue', 'Codeium', 'Copilot', 'Replit', 'Bolt', 'v0',
  'Lovable', 'Devin', 'SWE-agent', 'OpenHands',
];

function PillRow({ items, direction = 'left', speed = 30 }: { items: string[]; direction?: 'left' | 'right'; speed?: number }) {
  const repeated = [...items, ...items, ...items, ...items];
  const animStyle = {
    animation: `marquee ${speed}s linear infinite`,
    animationDirection: direction === 'right' ? 'reverse' as const : 'normal' as const,
  };

  return (
    <div className="overflow-hidden py-1.5">
      <div className="flex gap-3 w-max" style={animStyle}>
        {repeated.map((name, i) => (
          <span
            key={i}
            className="inline-flex items-center rounded-full border border-white/[0.08] bg-white/[0.04] px-4 py-1.5 text-sm text-zinc-100"
          >
            {name}
          </span>
        ))}
      </div>
    </div>
  );
}

export default function Works() {
  return (
    <div>
      <p className="relative z-10 mb-6 text-center text-sm font-medium text-zinc-100">
        Works with every AI assistant
      </p>
      <div className="relative flex flex-col gap-2">
        <PillRow items={row1} direction="left" speed={45} />
        <PillRow items={row2} direction="right" speed={50} />
      </div>
    </div>
  );
}
