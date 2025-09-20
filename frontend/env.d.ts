/// <reference types="vite/client" />

// Vue components
declare module '*.vue' {
  import type {DefineComponent} from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

// Images
declare module '*.svg' {
  const content: string
  export default content
}
declare module '*.svg?component' {
  import type {DefineComponent} from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}
declare module '*.png' {
  const content: string
  export default content
}
declare module '*.jpg' {
  const content: string
  export default content
}
declare module '*.jpeg' {
  const content: string
  export default content
}
declare module '*.webp' {
  const content: string
  export default content
}

// Vite's import.meta
interface ImportMetaEnv {
  readonly VITE_API_BASE?: string

  // add other env vars as needed
  [key: string]: any
}

interface ImportMeta {
  readonly env: ImportMetaEnv

  glob<T = unknown>(
    pattern: string,
    options?: {
      eager?: boolean
      import?: string | string[]
      as?: string
    }
  ): Record<string, T>
}

declare module '*.vue' {
  import type {DefineComponent} from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

