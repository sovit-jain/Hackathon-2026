/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',  // ← ADD THIS LINE
  reactStrictMode: true,
  async rewrites() {
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
