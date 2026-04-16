/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    unoptimized: true,
  },
  async rewrites() {
    return [
      {
        source: '/mcp',
        destination: 'https://web-production-a7930.up.railway.app/mcp',
      },
      {
        source: '/mcp/:path*',
        destination: 'https://web-production-a7930.up.railway.app/mcp/:path*',
      },
      {
        source: '/oauth/:path*',
        destination: 'https://web-production-a7930.up.railway.app/oauth/:path*',
      },
      {
        source: '/health',
        destination: 'https://web-production-a7930.up.railway.app/health',
      },
    ];
  },
};

export default nextConfig;
