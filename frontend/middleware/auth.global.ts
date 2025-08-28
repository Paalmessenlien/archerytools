
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

  // Define public routes that don't require authentication
  const publicRoutes = [
    '/',
    '/about',
    '/login',
    '/login/index'
  ];

  // Check if the current route is public
  const isPublicRoute = publicRoutes.includes(to.path);

  // If not a public route and user is not authenticated, redirect to login
  if (!isPublicRoute && !token.value) {
    return navigateTo('/login');
  }
});
