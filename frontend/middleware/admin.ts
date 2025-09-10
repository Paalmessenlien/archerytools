export default defineNuxtRouteMiddleware(async (to, from) => {
  // Skip server-side execution - let client handle authentication
  if (process.server) {
    console.log('Admin middleware skipping server-side execution')
    return
  }

  const { user, isAdmin, isInitialized, initializeClientAuth } = useAuth()

  console.log('Admin middleware running for route:', to.path)
  
  // Wait for auth initialization if not already done
  if (!isInitialized.value) {
    console.log('Auth not initialized, initializing...')
    await initializeClientAuth()
  }

  console.log('Current user in admin middleware:', user.value?.email)
  console.log('Current admin status in admin middleware:', isAdmin.value)

  // Wait for authentication to be checked
  if (!user.value) {
    console.log('No user, redirecting to login')
    return navigateTo('/login')
  }

  // Check if user is admin (messenlien@gmail.com has automatic admin privileges)
  if (!isAdmin.value) {
    console.log('User is not admin, throwing 403 error')
    throw createError({
      statusCode: 403,
      statusMessage: 'Admin access required - Only messenlien@gmail.com has admin access'
    })
  }

  console.log('Admin middleware passed, allowing access to:', to.path)
})