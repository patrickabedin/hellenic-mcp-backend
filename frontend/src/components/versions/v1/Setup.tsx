'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';

const platforms = [
  'Claude Desktop',
  'Claude.ai',
  'ChatGPT',
  'Gemini',
  'Cursor',
  'Windsurf',
  'OpenClaw',
  'hellenicAI',
  'Direct API',
] as const;

type Platform = (typeof platforms)[number];

const configBlocks: Record<Platform, { steps: { num: string; title: string; desc: string }[]; code?: string; urls?: { label: string; value: string }[]; note?: string }> = {
  'Claude Desktop': {
    steps: [
      { num: '1', title: 'Connect your Google Ads account', desc: 'Click <em>Connect Google Ads</em> above and authorize via Google OAuth. You\'ll get a session ID on the success page.' },
      { num: '2', title: 'Edit your Claude Desktop config', desc: 'Open <code>~/Library/Application Support/Claude/claude_desktop_config.json</code> (Mac) or <code>%APPDATA%\\Claude\\claude_desktop_config.json</code> (Windows) and add the block below. Replace <code>YOUR_SESSION_ID</code> with the ID from step 1.' },
      { num: '3', title: 'Restart Claude Desktop', desc: 'The 🔧 tools icon will appear in the chat bar. Ask: <em>"List my Google Ads campaigns"</em> to verify.' },
    ],
    code: `{
  "mcpServers": {
    "hellenic-google-ads": {
      "url": "https://google-ads-mcp.hellenicai.com/mcp",
      "headers": {
        "X-Session-ID": "YOUR_SESSION_ID"
      }
    }
  }
}`,
    note: '💡 Uses MCP Streamable HTTP transport — no local server process needed.',
  },
  'Claude.ai': {
    steps: [
      { num: '1', title: 'Connect your Google Ads account', desc: 'Click <em>Connect Google Ads</em> above and complete the OAuth flow. Copy your session ID from the success page.' },
      { num: '2', title: 'Open Claude.ai → Settings → Integrations', desc: 'Click <em>Add Integration</em> and enter the MCP server URL below. Add your session ID as a custom header <code>X-Session-ID</code>.' },
      { num: '3', title: 'Start a new conversation', desc: 'Claude will automatically have access to your Google Ads tools. Try: <em>"What\'s my total ad spend this month?"</em>' },
    ],
    urls: [
      { label: 'MCP Endpoint (Streamable HTTP)', value: 'https://google-ads-mcp.hellenicai.com/mcp' },
      { label: 'Header', value: 'X-Session-ID: YOUR_SESSION_ID' },
    ],
    note: '💡 Claude.ai supports remote MCP servers natively — no desktop app required.',
  },
  ChatGPT: {
    steps: [
      { num: '1', title: 'Connect your Google Ads account', desc: 'Click <em>Connect Google Ads</em> above and complete the OAuth flow.' },
      { num: '2', title: 'ChatGPT → Settings → Connectors → Add', desc: 'Paste the MCP endpoint URL. ChatGPT will auto-discover all available tools.' },
      { num: '3', title: 'Use in any GPT-4o conversation', desc: 'Ask: <em>"Show me my top 5 campaigns by spend"</em> — ChatGPT calls the MCP server live.' },
    ],
    urls: [{ label: 'MCP Endpoint', value: 'https://google-ads-mcp.hellenicai.com/mcp' }],
    note: '⚠️ ChatGPT MCP support requires ChatGPT Plus or Team plan.',
  },
  Gemini: {
    steps: [
      { num: '1', title: 'Connect your Google Ads account', desc: 'Click <em>Connect Google Ads</em> above and authorize via OAuth.' },
      { num: '2', title: 'Open Google AI Studio → Extensions → MCP', desc: 'Add a new MCP server and paste the endpoint URL. Gemini will discover all tools automatically.' },
      { num: '3', title: 'Ask Gemini about your campaigns', desc: 'Try: <em>"Which of my ad groups has the worst CTR this week?"</em>' },
    ],
    urls: [{ label: 'MCP Endpoint', value: 'https://google-ads-mcp.hellenicai.com/mcp' }],
    note: '💡 Also works with Gemini Advanced via Google Workspace integrations.',
  },
  Cursor: {
    steps: [
      { num: '1', title: 'Connect your Google Ads account', desc: 'Click <em>Connect Google Ads</em> above and complete the OAuth flow. Copy your session ID.' },
      { num: '2', title: 'Open Cursor → Settings → MCP', desc: 'Add a new server entry with the URL and your session ID header.' },
      { num: '3', title: 'Use in Cursor Agent or Composer', desc: 'Ask your coding agent: <em>"Pull my Google Ads performance data and build a dashboard"</em> — it fetches live data and writes the code.' },
    ],
    code: `{
  "mcpServers": {
    "hellenic-google-ads": {
      "url": "https://google-ads-mcp.hellenicai.com/mcp",
      "headers": {
        "X-Session-ID": "YOUR_SESSION_ID"
      }
    }
  }
}`,
  },
  Windsurf: {
    steps: [
      { num: '1', title: 'Connect your Google Ads account', desc: 'Click <em>Connect Google Ads</em> above and complete the OAuth flow.' },
      { num: '2', title: 'Open Windsurf → Settings → MCP Servers', desc: 'Add the endpoint URL and session header. Windsurf Cascade will auto-discover all tools.' },
      { num: '3', title: 'Use in Cascade', desc: 'Ask: <em>"Analyze my Google Ads and suggest budget optimizations"</em> — Cascade fetches live data and reasons over it.' },
    ],
    urls: [
      { label: 'MCP Endpoint', value: 'https://google-ads-mcp.hellenicai.com/mcp' },
      { label: 'Header', value: 'X-Session-ID: YOUR_SESSION_ID' },
    ],
  },
  OpenClaw: {
    steps: [
      { num: '1', title: 'Connect your Google Ads account', desc: 'Click <em>Connect Google Ads</em> above and complete the OAuth flow. Copy your session ID.' },
      { num: '2', title: 'Add MCP server in OpenClaw config', desc: 'Edit your <code>openclaw.json</code> and add the MCP server entry below, or run: <code>openclaw mcp add https://google-ads-mcp.hellenicai.com/mcp</code>' },
      { num: '3', title: 'Your agent manages Google Ads autonomously', desc: 'Set up cron jobs, heartbeat checks, or just ask: <em>"Pause all campaigns with ROAS below 2x"</em> — OpenClaw executes it.' },
    ],
    code: `{
  "mcp": {
    "servers": [{
      "name": "hellenic-google-ads",
      "url": "https://google-ads-mcp.hellenicai.com/mcp",
      "headers": {
        "X-Session-ID": "YOUR_SESSION_ID"
      }
    }]
  }
}`,
    note: '💡 OpenClaw agents can run Google Ads tasks on a schedule — no human needed.',
  },
  hellenicAI: {
    steps: [
      { num: '1', title: 'Connect your Google Ads account', desc: 'Click <em>Connect Google Ads</em> above and authorize via Google OAuth. You\'ll get a session ID on the success page.' },
      { num: '2', title: 'Open hellenicAI → Settings → MCP Servers → Add Server', desc: 'Select <em>Streamable HTTP</em> as the transport type. Paste the MCP endpoint URL below and add your session ID as the <code>X-Session-ID</code> header.' },
      { num: '3', title: 'Your hellenicAI agent is now connected', desc: 'The tools icon will appear in your agent\'s toolbar. Ask: <em>"List my Google Ads campaigns"</em> to verify the connection.' },
    ],
    urls: [
      { label: 'MCP Endpoint (Streamable HTTP)', value: 'https://google-ads-mcp.hellenicai.com/mcp' },
      { label: 'Transport', value: 'Streamable HTTP' },
      { label: 'Header', value: 'X-Session-ID: YOUR_SESSION_ID' },
    ],
    note: '💡 Uses MCP Streamable HTTP transport — no local server process needed.',
  },
  'Direct API': {
    steps: [
      { num: '1', title: 'Connect your Google Ads account', desc: 'Visit <code>https://google-ads-mcp.hellenicai.com/oauth/start?session_id=MY_SESSION</code> — replace <code>MY_SESSION</code> with any unique string.' },
      { num: '2', title: 'Call the MCP endpoint directly', desc: 'Use any HTTP client. Pass your session ID in the <code>X-Session-ID</code> header. The server speaks MCP Streamable HTTP (JSON-RPC 2.0).' },
      { num: '3', title: 'Integrate into your own app or agent', desc: 'Build custom automations, dashboards, or AI workflows using the full Google Ads API surface.' },
    ],
    code: `# List all available tools
curl -X POST https://google-ads-mcp.hellenicai.com/mcp \\
  -H "Content-Type: application/json" \\
  -H "X-Session-ID: YOUR_SESSION_ID" \\
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'

# Get campaign performance
curl -X POST https://google-ads-mcp.hellenicai.com/mcp \\
  -H "Content-Type: application/json" \\
  -H "X-Session-ID: YOUR_SESSION_ID" \\
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"list_campaigns","arguments":{}},"id":2}'`,
    note: '💡 Full MCP spec: modelcontextprotocol.io',
  },
};

export default function Setup() {
  const [active, setActive] = useState<Platform>('Claude Desktop');
  const data = configBlocks[active];

  return (
    <section id="setup" className="py-20">
      <div className="mx-auto max-w-[1400px] px-8">
        <div className="mb-10 text-center">
          <div className="mb-3 text-xs font-semibold uppercase tracking-wider text-brand-text-secondary">
            SETUP
          </div>
          <h2 className="font-heading text-3xl font-bold md:text-4xl">Connect in 3 steps</h2>
          <p className="mt-3 text-brand-text-secondary">Works with every major AI platform</p>
        </div>

        {/* Platform tabs */}
        <div className="mb-8 flex flex-wrap justify-center gap-2">
          {platforms.map((p) => (
            <button
              key={p}
              onClick={() => setActive(p)}
              className={`rounded-lg px-4 py-2 text-sm font-medium transition-all ${
                active === p
                  ? 'bg-brand-blue text-white'
                  : 'bg-white/5 text-brand-text-secondary hover:text-white'
              }`}
            >
              {p}
            </button>
          ))}
        </div>

        {/* Content */}
        <motion.div
          key={active}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.25 }}
          className="mx-auto max-w-2xl rounded-xl border border-white/6 bg-brand-surface p-8"
        >
          {/* Steps */}
          <div className="mb-6 flex flex-col gap-4">
            {data.steps.map((step) => (
              <div key={step.num} className="flex gap-4">
                <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-brand-blue text-xs font-bold text-white">
                  {step.num}
                </div>
                <div className="text-sm leading-relaxed text-white/80">
                  <strong className="text-white">{step.title}</strong>
                  <br />
                  <span dangerouslySetInnerHTML={{ __html: step.desc }} />
                </div>
              </div>
            ))}
          </div>

          {/* Config code */}
          {data.code && (
            <pre className="overflow-x-auto rounded-lg bg-black/40 p-4 text-xs leading-relaxed text-white/80">
              <code>{data.code}</code>
            </pre>
          )}

          {/* URL boxes */}
          {data.urls && (
            <div className="mt-4 flex flex-col gap-2">
              {data.urls.map((url) => (
                <div key={url.label} className="rounded-lg bg-black/30 px-4 py-3">
                  <div className="mb-1 text-xs text-brand-text-secondary">{url.label}</div>
                  <div className="font-mono text-sm text-white/90">{url.value}</div>
                </div>
              ))}
            </div>
          )}

          {/* Note */}
          {data.note && (
            <p className="mt-4 text-xs text-brand-text-secondary">{data.note}</p>
          )}
        </motion.div>
      </div>
    </section>
  );
}
