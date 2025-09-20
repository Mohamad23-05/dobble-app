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
    v({
      svgoConfig: {
        plugins: [
          {
            name: 'removeViewBox',
            active: false
          },
          {
            name: 'removeDimensions',
            active: true
          }
        ]
      }
    })
    ,
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})

