
import { useAuth } from '~/composables/useAuth';

export default defineNuxtRouteMiddleware(async (to, from) => {
  const { token, fetchUser } = useAuth();

  if (token.value) {
    await fetchUser();
  }

  if (to.path.startsWith('/setups') && !token.value) {
    return navigateTo('/login');
  }
});
