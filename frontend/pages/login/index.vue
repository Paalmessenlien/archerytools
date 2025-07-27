
<template>
  <div class="flex items-center justify-center min-h-screen">
    <div class="p-8 bg-white rounded-lg shadow-md">
      <h1 class="mb-4 text-2xl font-bold text-center">Login</h1>
      <GoogleLogin :callback="handleGoogleLogin" />
    </div>
  </div>
</template>

<script setup>
import { useAuth } from '~/composables/useAuth';

const { loginWithGoogle } = useAuth();
const router = useRouter();

const handleGoogleLogin = async (response) => {
  try {
    await loginWithGoogle(response);
    router.push('/setups');
  } catch (error) {
    console.error('Login failed:', error);
  }
};
</script>
