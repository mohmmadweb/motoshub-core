/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  eslint: { ignoreDuringBuilds: true },
  async rewrites() {
    // Proxy /api/v1/* to the backend to avoid CORS in the browser.
    const base = process.env.BACKEND_ORIGIN || "http://localhost:8000";
    return [{ source: "/api/v1/:path*", destination: `${base}/api/v1/:path*` }];
  },
};
export default nextConfig;
