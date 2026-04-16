'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';

const MCP_URL = 'https://google-ads-mcp.hellenicai.com/mcp';

const clients = [
  {
    name: 'Claude Desktop',
    icon: '🔮',
    config: `{
  "mcpServers": {
    "hellenic-google-ads": {
      "url": "https://google-ads-mcp.hellenicai.com/mcp",
      "transport": "http",
      "headers": {
        "X-Session-ID": "YOUR_SESSION_ID"
      }
    }
  }
}`,
    configFile: '~/.claude/claude_desktop_config.json',
    note: 'Uses MCP Streamable HTTP transport — no local server process needed.',
  },
  {
    name: 'Cursor',
    icon: '⌨️',
    config: `{
  "mcpServers": {
    "hellenic-google-ads": {
      "url": "https://google-ads-mcp.hellenicai.com/mcp",
      "transport": "http",
      "headers": {
        "X-Session-ID": "YOUR_SESSION_ID"
      }
    }
  }
}`,
    configFile: '.cursor/mcp.json',
    note: 'Open Cursor → Settings → MCP to add the server. Use in Agent or Composer mode.',
  },
  {
    name: 'Windsurf',
    icon: '🌊',
    config: `{
  "mcpServers": {
    "hellenic-google-ads": {
      "url": "https://google-ads-mcp.hellenicai.com/mcp",
      "transport": "http",
      "headers": {
        "X-Session-ID": "YOUR_SESSION_ID"
      }
    }
  }
}`,
    configFile: '~/.codeium/windsurf/mcp_config.json',
    note: 'Windsurf Cascade auto-discovers all tools. Ask it to manage your campaigns directly.',
  },
  {
    name: 'Any MCP Client',
    icon: '🔌',
    config: `# Any MCP-compatible client can connect using streamable HTTP transport:
# Transport: Streamable HTTP (SSE)
# URL: https://google-ads-mcp.hellenicai.com/mcp
# Header: X-Session-ID: YOUR_SESSION_ID

# The server speaks JSON-RPC 2.0 over HTTP.
# No local installation required — it's a hosted remote MCP server.`,
    configFile: 'Your MCP config file',
    note: 'This server uses streamable HTTP transport (SSE). Just paste the URL and your session ID.',
  },
];

export default function MCPConnection() {
  const [activeClient, setActiveClient] = useState(0);
  const [copied, setCopied] = useState(false);
  const [copiedConfig, setCopiedConfig] = useState(false);

  const copyUrl = () => {
    navigator.clipboard.writeText(MCP_URL);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const copyConfig = () => {
    navigator.clipboard.writeText(clients[activeClient].config);
    setCopiedConfig(true);
    setTimeout(() => setCopiedConfig(false), 2000);
  };

  return (
    <section id="mcp-connection" className="py-12 md:py-16 px-6 border-t border-white/[0.06]">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-12">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-[#5E6AD2]/20 bg-[#5E6AD2]/5 text-xs font-medium text-[#5E6AD2] tracking-wide mb-6">
              MCP Streamable HTTP
            </span>
          </motion.div>
          <motion.h2
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-[32px] md:text-[40px] font-extrabold tracking-tighter leading-[1.05] mb-4"
          >
            Connect to your AI assistant
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.15 }}
            className="text-[16px] text-white/55 max-w-lg mx-auto mb-8"
          >
            One URL. No local server to install. The MCP server runs in the cloud and speaks
            streamable HTTP — works with Claude, Cursor, Windsurf, and any MCP-compatible client.
          </motion.p>

          {/* MCP URL with copy button */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="inline-flex items-center gap-2 rounded-lg border border-white/[0.08] bg-white/[0.03] px-4 py-3"
          >
            <code className="text-[14px] font-mono text-white/80 tracking-tight">
              {MCP_URL}
            </code>
            <button
              onClick={copyUrl}
              className="ml-1 px-3 py-1.5 rounded-md bg-[#5E6AD2]/20 hover:bg-[#5E6AD2]/30 text-[#5E6AD2] text-xs font-medium transition-colors"
            >
              {copied ? '✓ Copied' : 'Copy'}
            </button>
          </motion.div>
        </div>

        {/* Step 1: Get session ID */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.25 }}
          className="mb-10 max-w-3xl mx-auto rounded-xl border border-white/[0.06] bg-white/[0.02] p-6"
        >
          <div className="flex items-start gap-4">
            <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-[#5E6AD2] text-sm font-bold text-white">
              1
            </div>
            <div>
              <h3 className="text-[16px] font-bold text-white mb-1">Get your session ID</h3>
              <p className="text-[14px] text-white/55 leading-relaxed mb-3">
                Connect your Google Ads account via Google OAuth. You&apos;ll receive a session ID on the
                success page — this is what authenticates your AI assistant to your Google Ads data.
              </p>
              <a
                href="https://google-ads-mcp.hellenicai.com/oauth/start?session_id=new"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-[#5E6AD2] hover:bg-[#6B77D8] text-white text-[13px] font-medium transition-colors"
              >
                Connect Google Ads →
              </a>
            </div>
          </div>
        </motion.div>

        {/* Step 2: Choose your client */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="max-w-3xl mx-auto"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-[#5E6AD2] text-sm font-bold text-white">
              2
            </div>
            <h3 className="text-[16px] font-bold text-white">Add the config to your AI client</h3>
          </div>

          {/* Client tabs */}
          <div className="flex flex-wrap gap-2 mb-6">
            {clients.map((client, i) => (
              <button
                key={client.name}
                onClick={() => setActiveClient(i)}
                className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg text-[13px] font-medium transition-all ${
                  activeClient === i
                    ? 'bg-[#5E6AD2] text-white'
                    : 'bg-white/[0.04] text-white/50 hover:text-white/70 hover:bg-white/[0.06] border border-white/[0.06]'
                }`}
              >
                <span>{client.icon}</span>
                {client.name}
              </button>
            ))}
          </div>

          {/* Config block */}
          <div className="rounded-xl border border-white/[0.06] overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2.5 border-b border-white/[0.06] bg-white/[0.02]">
              <span className="text-[12px] font-mono text-white/40">
                {clients[activeClient].configFile}
              </span>
              <button
                onClick={copyConfig}
                className="px-3 py-1 rounded-md bg-white/[0.06] hover:bg-white/[0.1] text-white/50 hover:text-white/70 text-[11px] font-medium transition-colors"
              >
                {copiedConfig ? '✓ Copied' : 'Copy config'}
              </button>
            </div>
            <pre className="p-5 bg-[#0a0a0a] text-[13px] font-mono leading-relaxed overflow-x-auto">
              <code className="text-white/70">{clients[activeClient].config}</code>
            </pre>
          </div>

          {/* Note */}
          {clients[activeClient].note && (
            <p className="mt-3 text-[13px] text-white/40">
              💡 {clients[activeClient].note}
            </p>
          )}
        </motion.div>
      </div>
    </section>
  );
}
