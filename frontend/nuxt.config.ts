// https://nuxt.com/docs/api/configuration/nuxt-config

// Debug: Log environment variables during build
console.log('🔍 Nuxt Config Debug:');
console.log('  NUXT_PUBLIC_GOOGLE_CLIENT_ID:', process.env.NUXT_PUBLIC_GOOGLE_CLIENT_ID);
console.log('  NUXT_PUBLIC_API_BASE:', process.env.NUXT_PUBLIC_API_BASE);
console.log('  NODE_ENV:', process.env.NODE_ENV);

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
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:5000/api',
      googleClientId: process.env.NUXT_PUBLIC_GOOGLE_CLIENT_ID
    }
  },

  // Route Rules for API proxy in development
  routeRules: {
    '/api/**': { 
      proxy: 'http://localhost:5000/api/**',
      cors: true 
    }
  },
  
  // SSR Configuration
  ssr: true,
  
  // App Configuration
  app: {
    head: {
      title: 'ArcheryTool - Professional Archery Tools',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1, maximum-scale=5' },
        { name: 'description', content: 'Professional archery tools for arrow selection and tuning' },
        { name: 'keywords', content: 'archery, arrows, tuning, spine calculator, bow setup' },
        { name: 'format-detection', content: 'telephone=no' },
        { name: 'apple-mobile-web-app-capable', content: 'yes' },
        { name: 'apple-mobile-web-app-status-bar-style', content: 'default' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
        // Material Symbols font for Material Web icons
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200' },
        // Roboto font for Material Design
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,500;1,700&display=swap' }
      ],
      // Set default dark mode class on HTML element for SSR
      htmlAttrs: {
        class: 'dark'
      }
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
  },

  // Nitro (server) configuration for headers
  nitro: {
    headers: {
      'Cross-Origin-Opener-Policy': 'unsafe-none',
      'Content-Security-Policy': "default-src 'self'; connect-src 'self' http://localhost http://localhost:5000 https://archerytool.online https://accounts.google.com https://apis.google.com; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://accounts.google.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:;"
    },
    // Fix for internal paths resolution
    experimental: {
      wasm: true
    }
  },

  // Compatibility configuration
  experimental: {
    payloadExtraction: false
  },

  // TypeScript configuration
  typescript: {
    strict: false,
    typeCheck: false
  }
})