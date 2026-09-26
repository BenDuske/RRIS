import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/ws': {
        target: 'http://localhost:8000',
        ws: true,
      },
      '/ingest': 'http://localhost:8000',
      '/incidents': 'http://localhost:8000',
      '/reset': 'http://localhost:8000',
    },
  },
})
