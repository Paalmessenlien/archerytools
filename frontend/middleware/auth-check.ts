import { useAuth } from '~/composables/useAuth';

export default defineNuxtRouteMiddleware(async (to, from) => {
  const { user, fetchUser } = useAuth();

  if (!user.value) {
    await fetchUser(); // Attempt to fetch user if not already loaded
    if (!user.value) {
      return navigateTo('/'); // Redirect to home if still not logged in
    }
  }
});