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
    host: "0.0.0.0",          // 🔥 Esto permite que otros dispositivos accedan
    port: 5173,               // Puedes cambiar este puerto si quieres
    strictPort: true,         // Si el puerto está ocupado, lanza error en vez de cambiarlo
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
