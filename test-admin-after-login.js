// Test script to verify admin access after login
// Copy the JWT token from browser localStorage and test

console.log('🔧 Admin Access Test');
console.log('===================');

// Instructions for user:
console.log('1. Open browser dev tools (F12)');
console.log('2. Go to Console tab');
console.log('3. Type: localStorage.getItem("token")');
console.log('4. Copy the token value');
console.log('5. Replace YOUR_TOKEN_HERE below and run this script');

const token = 'YOUR_TOKEN_HERE';

if (token === 'YOUR_TOKEN_HERE') {
  console.log('❌ Please replace YOUR_TOKEN_HERE with actual token from browser');
  process.exit(1);
}

const testAdminEndpoints = async () => {
  const endpoints = [
    '/api/admin/check',
    '/api/admin/migrations/status', 
    '/api/admin/database/health'
  ];
  
  for (const endpoint of endpoints) {
    try {
      const response = await fetch(`http://localhost:3000${endpoint}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log(`✅ ${endpoint}: SUCCESS`);
        console.log(`   Response:`, data);
      } else {
        console.log(`❌ ${endpoint}: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      console.log(`❌ ${endpoint}: Error - ${error.message}`);
    }
  }
};

// Uncomment to test with actual token:
// testAdminEndpoints();