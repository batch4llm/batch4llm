import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from 'path'

export default defineConfig({
    plugins: [react()],
    server: {
        port: 5173,
        strictPort: true,
        proxy: {
            '/api': {
                target: process.env.VITE_API_TARGET ?? 'http://127.0.0.1:80',
                changeOrigin: true,
                secure: false,
            },
        },
    },
    build: {
        outDir: "dist",
        emptyOutDir: true,
    },
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src')
        }
    }
});
