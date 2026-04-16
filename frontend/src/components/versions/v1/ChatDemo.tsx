'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { Send } from 'lucide-react';
import { motion } from 'framer-motion';

interface Conversation {
  user: string;
  ai: string;
}

const conversations: Conversation[] = [
  {
    user: 'Pause all campaigns with ROAS below 2x',
    ai: `Done. Found 3 campaigns with ROAS below 2.0x:\n• Brand Search — ROAS 1.4x ($2,180 spend)\n• Competitor Terms — ROAS 1.7x ($1,540 spend)\n• Broad Match — ROAS 1.9x ($980 spend)\n\nAll 3 paused. Want me to send a summary to Slack?`,
  },
  {
    user: "What's my best performing campaign this month?",
    ai: `Your top campaign is 'Branded Keywords' with:\n• ROAS: 4.2x ($12,400 revenue on $2,950 spend)\n• CTR: 8.7% (3x industry average)\n• 847 conversions at $3.48 CPA\n\nShould I increase its budget by 20%?`,
  },
  {
    user: 'Show me keywords wasting budget',
    ai: `Found 12 underperforming keywords burning $1,840/month:\n• 'free google ads' — $340 spend, 0 conversions\n• 'google ads tutorial' — $280 spend, 0 conversions\n• 8 more broad match terms...\n\nAdd all 12 as negatives?`,
  },
  {
    user: 'Optimize my Shopping campaigns for Q2',
    ai: `Analyzing your 6 Shopping campaigns...\n• Increase bids on 23 top products (+15% ROAS lift expected)\n• Pause 41 products with <0.5% CTR\n• Shift $2,100 budget from underperformers\n\nEstimated impact: +$8,400 revenue/month. Apply changes?`,
  },
];

type Phase = 'typing-input' | 'input-pause' | 'thinking' | 'typing-ai' | 'showing-full';

interface ChatMessage {
  type: 'user' | 'ai';
  text: string;
  isTyping?: boolean;
}

export default function ChatDemo() {
  const [phase, setPhase] = useState<Phase>('typing-input');
  const [inputText, setInputText] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const mountedRef = useRef(true);
  const currentConvoRef = useRef(0);

  const clearTimeouts = useCallback(() => {
    if (timeoutRef.current) { clearTimeout(timeoutRef.current); timeoutRef.current = null; }
    if (intervalRef.current) { clearInterval(intervalRef.current); intervalRef.current = null; }
  }, []);

  const scrollToBottom = useCallback(() => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight;
    }
  }, []);

  useEffect(() => {
    mountedRef.current = true;
    // Start the chain on mount
    timeoutRef.current = setTimeout(() => {
      if (!mountedRef.current) return;
      startTypeInput();
    }, 800);
    return () => { mountedRef.current = false; clearTimeouts(); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function startTypeInput() {
    const idx = currentConvoRef.current;
    const text = conversations[idx].user;
    let i = 0;
    setPhase('typing-input');
    setInputText('');
    intervalRef.current = setInterval(() => {
      if (!mountedRef.current) return;
      if (i < text.length) {
        setInputText(text.slice(0, i + 1));
        i++;
      } else {
        clearInterval(intervalRef.current!);
        intervalRef.current = null;
        // Pause with text in input, then "send"
        timeoutRef.current = setTimeout(() => {
          if (!mountedRef.current) return;
          setMessages(prev => [...prev, { type: 'user', text }]);
          setInputText('');
          scrollToBottom();
          // After brief pause, show thinking
          timeoutRef.current = setTimeout(() => {
            if (!mountedRef.current) return;
            setPhase('thinking');
            scrollToBottom();
            // After thinking, type AI response
            timeoutRef.current = setTimeout(() => {
              if (!mountedRef.current) return;
              startTypeAI();
            }, 1200);
          }, 400);
        }, 600);
      }
    }, 40);
  }

  function startTypeAI() {
    const idx = currentConvoRef.current;
    const text = conversations[idx].ai;
    let i = 0;
    setPhase('typing-ai');
    setMessages(prev => [...prev, { type: 'ai', text: '', isTyping: true }]);
    intervalRef.current = setInterval(() => {
      if (!mountedRef.current) return;
      if (i < text.length) {
        setMessages(prev => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          if (last && last.type === 'ai') {
            updated[updated.length - 1] = { ...last, text: text.slice(0, i + 1), isTyping: true };
          }
          return updated;
        });
        i++;
        scrollToBottom();
      } else {
        clearInterval(intervalRef.current!);
        intervalRef.current = null;
        setMessages(prev => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          if (last && last.type === 'ai') {
            updated[updated.length - 1] = { ...last, text, isTyping: false };
          }
          return updated;
        });
        setPhase('showing-full');
        // After 3s pause, chain to next conversation
        timeoutRef.current = setTimeout(() => {
          if (!mountedRef.current) return;
          currentConvoRef.current = (currentConvoRef.current + 1) % conversations.length;
          startTypeInput();
        }, 3000);
      }
    }, 15);
  }

  const showThinking = phase === 'thinking';
  const showCursor = phase === 'typing-ai';

  return (
    <div className="w-full rounded-xl border border-[#27272A] bg-[#111113] overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-2 border-b border-white/[0.06] bg-[#0042BF]/8 px-5 py-3.5">
        <div className="h-2.5 w-2.5 rounded-full bg-[#0042BF]" />
        <span className="text-sm font-semibold text-white/70">Google Ads MCP — Connected</span>
      </div>

      {/* Messages area — no AnimatePresence wrapper, messages accumulate */}
      <div
        ref={scrollContainerRef}
        className="flex flex-col gap-5 px-5 py-6 overflow-y-auto"
        style={{ minHeight: 300, maxHeight: 420 }}
      >
        {messages.map((msg, i) => (
          <motion.div
            key={`${msg.type}-${i}`}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25 }}
            className="flex gap-3 items-start"
          >
            {msg.type === 'user' ? (
              <>
                <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-white/[0.06] text-xs font-medium text-white/50">
                  U
                </div>
                <div className="rounded-lg border border-white/[0.06] bg-white/[0.03] px-4 py-3 text-sm leading-relaxed text-white/80">
                  {msg.text}
                </div>
              </>
            ) : (
              <>
                <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-[#0042BF]/20 text-xs font-semibold text-[#0042BF]">
                  AI
                </div>
                <div
                  className={`rounded-lg border bg-white/[0.02] px-4 py-3 text-sm leading-relaxed text-white/80 ${
                    msg.isTyping && showCursor ? 'border-[#0042BF]/30 typewriter-cursor' : 'border-white/[0.06]'
                  }`}
                  style={{ whiteSpace: 'pre-wrap' }}
                >
                  {msg.text}
                </div>
              </>
            )}
          </motion.div>
        ))}

        {/* Thinking indicator */}
        {showThinking && (
          <motion.div
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
            className="flex gap-3 items-start"
          >
            <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-[#0042BF]/20 text-xs font-semibold text-[#0042BF]">
              AI
            </div>
            <div className="flex items-center gap-1.5 rounded-lg border border-white/[0.06] bg-white/[0.02] px-4 py-3">
              <span className="h-1.5 w-1.5 rounded-full bg-white/40 animate-bounce" style={{ animationDelay: '0ms' }} />
              <span className="h-1.5 w-1.5 rounded-full bg-white/40 animate-bounce" style={{ animationDelay: '150ms' }} />
              <span className="h-1.5 w-1.5 rounded-full bg-white/40 animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input bar — animated */}
      <div className="flex items-center gap-3 border-t border-white/[0.06] bg-[#0a0a0c] px-4 py-3.5">
        <input
          type="text"
          value={phase === 'typing-input' ? inputText : ''}
          placeholder={phase !== 'typing-input' ? 'Ask anything about your campaigns...' : ''}
          readOnly
          className="flex-1 rounded-lg border border-[#27272A] bg-[#18181b] px-4 py-2.5 text-sm text-white/80 placeholder-white/30 outline-none focus:border-[#0042BF]/50 transition-colors"
        />
        <button
          className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-[#0042BF] text-white transition-colors hover:bg-[#0035A0]"
          aria-label="Send"
        >
          <Send className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
