/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  async rewrites() {
    const backend = process.env.HOOK_API_URL || 'http://127.0.0.1:8000';
    return [{ source: '/api/backend/:path*', destination: `${backend}/:path*` }];
  },
};
module.exports = nextConfig;
