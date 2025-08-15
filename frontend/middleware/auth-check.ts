export default defineNuxtRouteMiddleware(async (to, from) => {
  console.log('Auth middleware running for route:', to.path);
  const { user, token, fetchUser } = useAuth();

  console.log('Current user in middleware:', user.value);
  console.log('Current token in middleware:', !!token.value);

  if (!user.value) {
    console.log('No user found, attempting to fetch...');
    await fetchUser(); // Attempt to fetch user if not already loaded
    console.log('After fetchUser, user:', user.value);
    if (!user.value) {
      console.log('Still no user, redirecting to home');
      return navigateTo('/'); // Redirect to home for login if not authenticated
    }
  }
  console.log('Auth middleware passed, allowing access to:', to.path);
});