const nextConfig = {
  reactStrictMode: false,
  distDir: ".next-build",

  // Rewrites for development - proxy requests to FastAPI backend
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: "http://localhost:8000/api/v1/:path*",
      },
    ];
  },
};

export default nextConfig;

