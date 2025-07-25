// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt'
  ],
  
  // CSS Configuration
  css: [
    '~/assets/css/main.css',
    '@fortawesome/fontawesome-free/css/all.css'
  ],
  
  // Runtime Config for API
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:5000/api'
    }
  },
  
  // SSR Configuration
  ssr: true,
  
  // App Configuration
  app: {
    head: {
      title: 'ArrowTune - Professional Arrow Selection',
      meta: [
        { name: 'description', content: 'Professional arrow tuning and selection platform' },
        { name: 'keywords', content: 'archery, arrows, tuning, spine calculator, bow setup' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
        // Material Symbols font for Material Web icons
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200' },
        // Roboto font for Material Design
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,500;1,700&display=swap' }
      ]
    }
  },

  // Build Configuration
  build: {
    transpile: ['@headlessui/vue']
  },
  
  // Vue Configuration for Material Web Components
  vue: {
    compilerOptions: {
      isCustomElement: (tag) => tag.includes('md-')
    }
  },

  // Tailwind CSS Configuration
  tailwindcss: {
    cssPath: '~/assets/css/main.css',
    configPath: 'tailwind.config.js',
    exposeConfig: false,
    viewer: true,
  }
})