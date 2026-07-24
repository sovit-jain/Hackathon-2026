/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    // API rewrites for Next.js - requires NEXT_PUBLIC_API_URL environment variable
    // DO NOT add localhost fallback - use env vars in all environments
    const backendUrl = process.env.NEXT_PUBLIC_API_URL;

    if (!backendUrl) {
      console.warn('NEXT_PUBLIC_API_URL is not set. API rewrites will use relative paths.');
    }

    return backendUrl ? [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ] : [];
  },
};

module.exports = nextConfig;
