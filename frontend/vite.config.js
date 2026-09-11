import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Custom plugin to inject Tailwind CSS CDN into built HTML
function tailwindCDN() {
  return {
    name: 'inject-tailwind-cdn',
    transformIndexHtml(html) {
      return html.replace(
        '</head>',
        `    <script src="https://cdn.tailwindcss.com"></script>
    <script>
      tailwind.config = {
        theme: {
          extend: {
            fontFamily: {
              sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
              mono: ['Fira Code', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
            },
          },
        },
      }
    </script>
  </head>`
      );
    },
  };
}

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), tailwindCDN()],
  server: {
    port: 5173,
    host: '127.0.0.1',
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
});

