
import { useAuth } from '~/composables/useAuth';

export default defineNuxtRouteMiddleware(async (to, from) => {
  // Skip on server-side to avoid hydration issues
  if (process.server) {
    return;
  }

  const { token, fetchUser, initializeClientAuth } = useAuth();

  // Initialize client auth first
  await initializeClientAuth();

  // Define public routes that don't require authentication
  const publicRoutes = [
    '/',
    '/about',
    '/login',
    '/login/index'
  ];

  // Check if the current route is public
  const isPublicRoute = publicRoutes.includes(to.path);

  // For public routes, just initialize auth but don't redirect
  if (isPublicRoute) {
    if (token.value) {
      await fetchUser();
    }
    return;
  }

  // For protected routes, try to fetch user if we have a token
  if (token.value) {
    await fetchUser();
  } else {
    // Only redirect to login if we're sure there's no valid auth
    // Let the specific route middleware (like auth-check) handle this
    console.log('Global middleware: No token found for protected route, letting route middleware handle it');
  }
});
