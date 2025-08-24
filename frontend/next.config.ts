import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  // Configuração para Docker
  experimental: {
    outputFileTracingRoot: undefined, // Usar o padrão
  },
};

export default nextConfig;
