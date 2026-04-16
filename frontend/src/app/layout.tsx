import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Google Ads MCP — Control Google Ads with AI",
  description:
    "The MCP server that connects Google Ads to any AI assistant. 25 tools. Free forever. Open source.",
  openGraph: {
    title: "Google Ads MCP — Control Google Ads with AI",
    description:
      "Manage campaigns, optimize bids, and analyze performance through natural language. Works with Claude, ChatGPT, Gemini, and more.",
    siteName: "hellenicAI",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={inter.variable}>
      <body style={{ fontFamily: "var(--font-inter), Inter, -apple-system, sans-serif" }}>
        {children}
      </body>
    </html>
  );
}
