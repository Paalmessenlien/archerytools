// Simple test to check API configuration
console.log('Environment variables:');
console.log('NUXT_PUBLIC_API_BASE:', process.env.NUXT_PUBLIC_API_BASE);
console.log('NODE_ENV:', process.env.NODE_ENV);

// Test the same default logic as nuxt.config.ts
const apiBase = process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:5000/api';
console.log('Resolved API Base:', apiBase);