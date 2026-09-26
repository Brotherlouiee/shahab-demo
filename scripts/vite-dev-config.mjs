import react from "@vitejs/plugin-react";

export function createViteConfig({
  apiProxyTarget = process.env.VITE_DEV_API_PROXY_TARGET || "http://127.0.0.1:8000",
} = {}) {
  return {
    plugins: [react()],
    server: {
      proxy: {
        "/api/v1": {
          target: apiProxyTarget,
          changeOrigin: false,
        },
      },
    },
  };
}
