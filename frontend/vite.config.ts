import {fileURLToPath, URL} from 'node:url'

import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import tailwind from '@tailwindcss/vite'
import svgLoader from 'vite-svg-loader'


// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    tailwind(),
    svgLoader({
      svgo: true,
      svgoConfig: {
        plugins: [
          {name: 'removeViewBox', active: false},   // keep viewBox for proper scaling
          {name: 'removeDimensions', active: true}, // allow sizing via CSS (width/height)
        ],
      },
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})

