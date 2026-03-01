import { execSync } from "child_process";

/**
 * Detect the WSL2 IP address so we can proxy API calls from the
 * Windows‐side Next.js server into the WSL‐side FastAPI backend.
 *
 * Priority:
 *   1. BACKEND_URL env var (explicit override)
 *   2. WSL2 IP auto‐detection (wsl hostname -I)
 *   3. localhost:8000 fallback (works when running fully inside WSL
 *      or when WSL2 localhost forwarding is enabled)
 */
function resolveBackendUrl() {
  if (process.env.BACKEND_URL) {
    return process.env.BACKEND_URL;
  }

  // Try to detect WSL2 IP (works when Next.js runs on Windows)
  try {
    const out = execSync("wsl -e hostname -I", {
      timeout: 3000,
      encoding: "utf-8",
      stdio: ["pipe", "pipe", "pipe"],
    }).trim().split(/\s+/)[0];
    if (out && /^\d+\.\d+\.\d+\.\d+$/.test(out)) {
      return `http://${out}:${process.env.DASHBOARD_API_PORT ?? "8000"}`;
    }
  } catch {
    // wsl command not available or failed — not on Windows / no WSL
  }

  return `http://localhost:${process.env.DASHBOARD_API_PORT ?? "8000"}`;
}

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  /**
   * Proxy /api/* and /reports/* through the Next.js server so the browser
   * never directly contacts the FastAPI backend port (avoids WSL2 port-
   * forwarding issues).
   */
  async rewrites() {
    const backendUrl = resolveBackendUrl();
    console.log(`[next.config] Proxying API → ${backendUrl}`);
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

