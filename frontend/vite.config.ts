import {fileURLToPath, URL} from 'node:url'
import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwind from '@tailwindcss/vite'
import svgLoader from 'vite-svg-loader'
// Optional in local dev only; keep but don’t enable in prod
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig(({mode}) => {
  const isDev = mode === 'development'

  return {
    plugins: [
      vue(),
      tailwind(),
      svgLoader({
        svgo: true,
        svgoConfig: {
          plugins: [
            {name: 'removeViewBox'},   // keep viewBox for proper scaling
            {name: 'removeDimensions'}, // allow sizing via CSS (width/height)
          ],
        },
      }),
      ...(isDev ? [vueDevTools()] : []),
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
  }
})
