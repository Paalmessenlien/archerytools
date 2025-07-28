import { useAuth } from '~/composables/useAuth';

export default defineNuxtRouteMiddleware(async (to, from) => {
  // Only apply this middleware to the root route
  if (to.path !== '/') return;
  
  const { user, fetchUser } = useAuth();

  if (!user.value) {
    await fetchUser(); // Attempt to fetch user if not already loaded
    if (!user.value) {
      return navigateTo('/login'); // Redirect to login if not authenticated
    }
  }
});