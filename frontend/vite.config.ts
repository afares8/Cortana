import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: true, // Expose to all network interfaces
    proxy: {
      "/api": {
        target: "http://localhost:8000", // Asume que backend está corriendo en tu PC
        changeOrigin: true,
        secure: false,
      },
    },
    hmr: {
      overlay: false          // Evita errores molestos en pantalla
    },
  },
})
