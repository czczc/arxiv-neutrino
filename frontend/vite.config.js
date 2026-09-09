import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

// Backend target for the dev proxy (uvicorn arxivnu.api:app on :8000).
const target = process.env.ARXIV_PROXY_TARGET || 'http://127.0.0.1:8000';

// Public URL prefix. '/' for local dev and root mounts; set
// VITE_BASE=/<prefix>/ (trailing slash) when served under a sub-path.
// Must match --root-path on uvicorn and the Apache ProxyPass prefix.
const base = process.env.VITE_BASE || '/';

export default defineConfig({
  base,
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: { '/api': target, '/health': target },
  },
});
