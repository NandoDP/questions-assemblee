import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',  // Écoute sur toutes les interfaces (accès réseau local)
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://192.168.1.16:5001',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    // Optimisations mobile
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'charts': ['recharts']
        }
      }
    }
  }
})
