export default defineNuxtRouteMiddleware(async (to, from) => {
  const { user, checkAdminStatus } = useAuth()

  // Wait for authentication to be checked
  if (!user.value) {
    return navigateTo('/login')
  }

  // Check if user is admin (messenlien@gmail.com has automatic admin privileges)
  try {
    const isAdmin = await checkAdminStatus()
    if (!isAdmin) {
      throw createError({
        statusCode: 403,
        statusMessage: 'Admin access required'
      })
    }
  } catch (error) {
    console.error('Admin check failed:', error)
    throw createError({
      statusCode: 403,
      statusMessage: 'Admin access required'
    })
  }
})