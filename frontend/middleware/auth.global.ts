
import { useAuth } from '~/composables/useAuth';

export default defineNuxtRouteMiddleware(async (to, from) => {
  // Skip on server-side to avoid hydration issues
  if (process.server) {
    return;
  }

  const { token, fetchUser, initializeClientAuth } = useAuth();

  // Initialize client auth first
  initializeClientAuth();

  if (token.value) {
    await fetchUser();
  }

  if (to.path.startsWith('/setups') && !token.value) {
    return navigateTo('/login');
  }
});
