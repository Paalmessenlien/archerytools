/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./components/**/*.{js,vue,ts}",
    "./layouts/**/*.vue",
    "./pages/**/*.vue",
    "./plugins/**/*.{js,ts}",
    "./nuxt.config.{js,ts}",
    "./app.vue"
  ],
  theme: {
    screens: {
      // Mobile-first responsive breakpoints for enhanced mobile experience
      'xs': '320px',         // Small phones (iPhone SE)
      'sm-mobile': '375px',  // Standard phones (iPhone 6-8)  
      'md-mobile': '414px',  // Large phones (iPhone 11 Pro Max)
      'lg-mobile': '428px',  // Extra large phones (iPhone 12 Pro Max)
      'sm': '640px',         // Tablet portrait
      'md': '768px',         // Tablet landscape  
      'lg': '1024px',        // Desktop
      'xl': '1280px',        // Large desktop
      '2xl': '1536px',       // Extra large desktop
    },
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        }
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      borderRadius: {
        'xl': '1rem',
        '2xl': '1.5rem',
      },
      boxShadow: {
        'soft': '0 1px 3px rgba(0, 0, 0, 0.1)',
        'medium': '0 4px 6px rgba(0, 0, 0, 0.1)',
      }
    },
  },
  plugins: [],
}