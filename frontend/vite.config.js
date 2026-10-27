import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Where your FastAPI server runs, and the prefix your routes live under.
// Routes are /metrics/overview ... => API_PREFIX = ''
// Routes are /observability/metrics/overview ... => API_PREFIX = '/observability'
const API_TARGET = 'http://localhost:8000'
const API_PREFIX = ''

// The browser calls /api/metrics/overview; Vite forwards it to
// http://localhost:8000{API_PREFIX}/metrics/overview (so no CORS is needed in dev).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: API_TARGET,
        changeOrigin: true,
        rewrite: path => path.replace(/^\/api/, API_PREFIX),
      },
    },
  },
})