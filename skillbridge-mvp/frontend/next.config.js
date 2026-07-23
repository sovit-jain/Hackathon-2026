/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    // Use the public backend URL when available; default to the deployed backend URL instead of localhost.
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'https://skillbridge-backend-740224388005.europe-west1.run.app';

    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
