import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    port: 5173,
    host: true,
  },
  build: {
    chunkSizeWarningLimit: 600,
    modulePreload: {
      resolveDependencies: (_url, deps) => {
        return deps.filter(dep => !dep.includes('charts'));
      },
    },
    rollupOptions: {
      output: {
        manualChunks(id: string) {
          if (
            id.includes('node_modules/react/') ||
            id.includes('node_modules/react-dom/') ||
            id.includes('node_modules/react-router-dom/')
          ) {
            return 'vendor';
          }
          if (id.includes('node_modules/recharts/')) {
            return 'charts';
          }
          if (id.includes('node_modules/framer-motion/')) {
            return 'motion';
          }
          if (id.includes('node_modules/lucide-react/')) {
            return 'icons';
          }
        },
      },
    },
  },
})
