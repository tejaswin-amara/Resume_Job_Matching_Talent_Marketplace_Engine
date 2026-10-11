/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    if (process.env.BACKEND_URL) {
      return [
        {
          source: '/api/:path*',
          destination: `${process.env.BACKEND_URL}/api/:path*`,
        },
      ];
    }
    return [];
  },
};

export default nextConfig;
