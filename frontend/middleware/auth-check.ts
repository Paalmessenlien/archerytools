export default defineNuxtRouteMiddleware(async (to, from) => {
  console.log('Auth middleware running for route:', to.path);
  
  // Skip on server-side to avoid issues
  if (process.server) {
    return;
  }

  const { user, token, fetchUser, initializeClientAuth } = useAuth();

  // Always reinitialize auth from localStorage on route changes
  await initializeClientAuth();
  
  console.log('Current user in middleware:', user.value);
  console.log('Current token in middleware:', !!token.value);

  // Check authentication state
  if (!token.value || !user.value) {
    console.log('Missing token or user - redirecting to login');
    return navigateTo('/login');
  }

  console.log('Auth middleware passed, allowing access to:', to.path);
});