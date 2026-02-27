/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  /**
   * Proxy /api/* and /reports/* through the Next.js server so the browser
   * never directly contacts the FastAPI backend port (avoids WSL2 port-
   * forwarding issues when Next.js and uvicorn both run inside WSL).
   */
  async rewrites() {
    const backendUrl = process.env.BACKEND_URL ?? "http://localhost:8000";
    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/api/:path*`,
      },
      {
        source: "/reports/:path*",
        destination: `${backendUrl}/reports/:path*`,
      },
    ];
  },
};

export default nextConfig;

