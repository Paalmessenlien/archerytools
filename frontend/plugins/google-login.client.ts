
import { defineNuxtPlugin } from '#app';

export default defineNuxtPlugin((nuxtApp) => {
  console.log('🚀 Google Login Plugin is loading!');
  
  const config = useRuntimeConfig();
  
  console.log('🔍 Google Login Plugin - Runtime config:', config.public);
  console.log('🔍 Google Client ID from config:', config.public.googleClientId);
  
  // Load Google Identity Services script directly
  if (process.client) {
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    
    script.onload = () => {
      console.log('✅ Google Identity Services script loaded');
      
      const clientId = config.public.googleClientId || '1039369917961-dq95hj3ip0krmhjajgo0h9qjdchq5pca.apps.googleusercontent.com';
      console.log('✅ Using Client ID for GSI:', clientId);
      
      // Initialize Google Identity Services
      if (window.google && window.google.accounts) {
        console.log('✅ Google accounts API available');
        
        // Make google object globally available
        nuxtApp.provide('google', window.google);
      }
    };
    
    script.onerror = () => {
      console.error('❌ Failed to load Google Identity Services script');
    };
    
    if (!document.querySelector('script[src="https://accounts.google.com/gsi/client"]')) {
      document.head.appendChild(script);
    }
  }
});
