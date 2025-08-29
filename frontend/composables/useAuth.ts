
import { ref, computed } from 'vue';

// Global state - shared across all useAuth() calls
// Initialize as null to avoid hydration mismatches, load from localStorage on client only
const token = ref(null);
const user = ref(null);
const isInitialized = ref(false);
const isLoggedIn = ref(false);
let googleAuthClient = null; // Singleton for the Google Auth client

export const useAuth = () => {
  const config = useRuntimeConfig();

  // Validate token format and expiration
  const isTokenValid = (tokenString: string): boolean => {
    if (!tokenString) return false;
    
    try {
      // Basic JWT format check (3 parts separated by dots)
      const parts = tokenString.split('.');
      if (parts.length !== 3) return false;
      
      // Decode payload to check expiration
      const payload = JSON.parse(atob(parts[1]));
      
      // Check if token has expired (with 5 minute buffer)
      if (payload.exp) {
        const now = Math.floor(Date.now() / 1000);
        const bufferTime = 5 * 60; // 5 minutes
        if (payload.exp < (now + bufferTime)) {
          console.warn('🔑 Token is expired or about to expire');
          return false;
        }
      }
      
      return true;
    } catch (e) {
      console.warn('🔑 Token validation failed:', e);
      return false;
    }
  };

  // Initialize token from localStorage only on client, avoid SSR hydration issues
  const initializeClientAuth = () => {
    if (process.client && !isInitialized.value) {
      const storedToken = localStorage.getItem('token');
      if (storedToken && isTokenValid(storedToken)) {
        token.value = storedToken;
        isLoggedIn.value = true;
        // Fetch user data on initialization if token exists
        fetchUser();
      } else if (storedToken) {
        // Token exists but is invalid, clear it
        console.warn('🔑 Stored token is invalid, clearing...');
        localStorage.removeItem('token');
      }
      isInitialized.value = true;
    }
  };

  const initializeGoogleAuth = () => {
    if (googleAuthClient || !process.client) {
      return;
    }

    const clientId = config.public.googleClientId || '1039369917961-dq95hj3ip0krmhjajgo0h9qjdchq5pca.apps.googleusercontent.com';
    
    const checkGoogle = () => {
      if (window.google && window.google.accounts && window.google.accounts.oauth2) {
        console.log('✅ Google Identity Services available, initializing client.');
        googleAuthClient = window.google.accounts.oauth2.initCodeClient({
          client_id: clientId,
          scope: 'email profile openid',
          callback: async (response) => {
            console.log('Google callback response:', response);
            if (response.code) {
              try {
                const res = await fetch(`${config.public.apiBase}/auth/google`, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ code: response.code }),
                });

                if (!res.ok) {
                  const errorData = await res.json();
                  console.error('Google auth API call failed:', errorData.error || `API error: ${res.status}`);
                  
                  // Show generic error (all users should be able to login now)
                  alert('Authentication failed: ' + (errorData.error || 'Unknown error'));
                  return;
                }

                const data = await res.json();
                if (data.token) {
                  setToken(data.token);
                  await fetchUser();
                  const router = useRouter();
                  
                  // Handle redirection based on profile completion status
                  if (data.needs_profile_completion) {
                    router.push('/register');
                  } else {
                    // Redirect to user's page after successful login
                    router.push('/my-setup');
                  }
                } else {
                  console.error('Failed to get token from backend:', data.error);
                }
              } catch (err) {
                console.error('Error during Google auth API call:', err);
              }
            } else {
              console.error('No code in Google auth response');
            }
          },
        });
        console.log('✅ Google OAuth client initialized.');
      } else {
        console.log('⏳ Waiting for Google Identity Services to load...');
        setTimeout(checkGoogle, 100);
      }
    };
    checkGoogle();
  };

  const setToken = (newToken) => {
    token.value = newToken;
    isLoggedIn.value = !!newToken;
    if (process.client) {
      localStorage.setItem('token', newToken);
    }
  };

  const removeToken = () => {
    token.value = null;
    isLoggedIn.value = false;
    if (process.client) {
      localStorage.removeItem('token');
    }
  };

  const loginWithGoogle = () => {
    if (googleAuthClient) {
      console.log('Requesting code from Google...');
      googleAuthClient.requestCode();
    } else {
      console.error('Google Auth client not initialized. Make sure to call initializeGoogleAuth().');
      // As a fallback, try to initialize now.
      initializeGoogleAuth();
      // Login will be handled by the initialization callback
      console.log('Login service is initializing. The login will proceed automatically.');
    }
  };

  const logout = () => {
    removeToken();
    user.value = null;
    isLoggedIn.value = false;
  };

  const fetchUser = async () => {
    if (!token.value) return;

    try {
      const res = await fetch(`${config.public.apiBase}/user`, {
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
      });
      if (res.ok) {
        user.value = await res.json();
        isLoggedIn.value = true;
      } else {
        // Token is invalid, clear everything
        console.warn('🔑 Token validation failed during user fetch, logging out...');
        logout();
      }
    } catch (err) {
      console.warn('🔑 Error fetching user, logging out:', err);
      logout();
    }
  };

  const updateUserProfile = async (profileData) => {
    if (!token.value) throw new Error('No authentication token found.');

    try {
      const res = await fetch(`${config.public.apiBase}/user/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token.value}`,
        },
        body: JSON.stringify(profileData),
      });

      if (res.ok) {
        await fetchUser(); // Refresh user data after update
        return true;
      } else {
        const errorData = await res.json();
        throw new Error(errorData.error || `API error: ${res.status}`);
      }
    } catch (err) {
      console.error('Error updating user profile:', err);
      throw err;
    }
  };

  const fetchBowSetups = async () => {
    if (!token.value) return [];

    try {
      const res = await fetch(`${config.public.apiBase}/bow-setups`, {
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
      });
      if (res.ok) {
        return await res.json();
      } else {
        console.error('Failed to fetch bow setups:', res.status, await res.text());
        return [];
      }
    } catch (err) {
      console.error('Error fetching bow setups:', err);
      return [];
    }
  };

  const addBowSetup = async (setupData) => {
    if (!token.value) throw new Error('No authentication token found.');

    try {
      const res = await fetch(`${config.public.apiBase}/bow-setups`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token.value}`,
        },
        body: JSON.stringify(setupData),
      });

      if (res.ok) {
        return await res.json();
      } else {
        const errorData = await res.json();
        throw new Error(errorData.error || `API error: ${res.status}`);
      }
    } catch (err) {
      console.error('Error adding bow setup:', err);
      throw err;
    }
  };

  const updateBowSetup = async (setupId, setupData) => {
    if (!token.value) throw new Error('No authentication token found.');

    try {
      const res = await fetch(`${config.public.apiBase}/bow-setups/${setupId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token.value}`,
        },
        body: JSON.stringify(setupData),
      });

      if (res.ok) {
        return await res.json();
      } else {
        const errorData = await res.json();
        throw new Error(errorData.error || `API error: ${res.status}`);
      }
    } catch (err) {
      console.error('Error updating bow setup:', err);
      throw err;
    }
  };

  const deleteBowSetup = async (setupId) => {
    if (!token.value) throw new Error('No authentication token found.');

    try {
      const res = await fetch(`${config.public.apiBase}/bow-setups/${setupId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
      });

      if (res.ok) {
        return true;
      } else {
        const errorData = await res.json();
        throw new Error(errorData.error || `API error: ${res.status}`);
      }
    } catch (err) {
      console.error('Error deleting bow setup:', err);
      throw err;
    }
  };

  // Arrow management for bow setups
  const addArrowToSetup = async (setupId, arrowData) => {
    if (!token.value) throw new Error('No authentication token found.');
    
    try {
      const res = await fetch(`${config.public.apiBase}/bow-setups/${setupId}/arrows`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token.value}`,
        },
        body: JSON.stringify(arrowData),
      });
      
      if (res.ok) {
        return await res.json();
      } else {
        const errorData = await res.json();
        throw new Error(errorData.error || `API error: ${res.status}`);
      }
    } catch (err) {
      console.error('Error adding arrow to setup:', err);
      throw err;
    }
  };

  const fetchSetupArrows = async (setupId) => {
    if (!token.value) throw new Error('No authentication token found.');
    
    try {
      const res = await fetch(`${config.public.apiBase}/bow-setups/${setupId}/arrows`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
      });
      
      if (res.ok) {
        const data = await res.json();
        return data.arrows;
      } else {
        const errorData = await res.json();
        throw new Error(errorData.error || `API error: ${res.status}`);
      }
    } catch (err) {
      console.error('Error fetching setup arrows:', err);
      throw err;
    }
  };

  const deleteArrowFromSetup = async (arrowSetupId) => {
    if (!token.value) throw new Error('No authentication token found.');

    try {
      const res = await fetch(`${config.public.apiBase}/setup-arrows/${arrowSetupId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
      });

      if (res.ok) {
        return await res.json();
      } else {
        const errorData = await res.json();
        throw new Error(errorData.error || 'Failed to remove arrow from setup.');
      }
    } catch (err) {
      console.error('Error removing arrow from setup:', err);
      throw err;
    }
  };

  const updateArrowInSetup = async (arrowSetupId, updateData) => {
    if (!token.value) throw new Error('No authentication token found.');

    try {
      const res = await fetch(`${config.public.apiBase}/setup-arrows/${arrowSetupId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token.value}`,
        },
        body: JSON.stringify(updateData),
      });

      if (res.ok) {
        return await res.json();
      } else {
        const errorData = await res.json();
        throw new Error(errorData.error || 'Failed to update arrow in setup.');
      }
    } catch (err) {
      console.error('Error updating arrow in setup:', err);
      throw err;
    }
  };

  // Admin functionality
  const checkAdminStatus = async () => {
    console.log('checkAdminStatus called, token exists:', !!token.value);
    if (!token.value) {
      console.log('No token available for admin check');
      return false;
    }

    try {
      console.log('Making admin check request to:', `${config.public.apiBase}/admin/check`);
      const res = await fetch(`${config.public.apiBase}/admin/check`, {
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
      });
      console.log('Admin check response status:', res.status);
      if (res.ok) {
        const data = await res.json();
        console.log('Admin check response data:', data);
        return data.is_admin;
      } else {
        const errorData = await res.text();
        console.log('Admin check failed:', res.status, errorData);
        return false;
      }
    } catch (err) {
      console.error('Error checking admin status:', err);
      return false;
    }
  };

  const getAllUsers = async () => {
    if (!token.value) throw new Error('No authentication token found.');

    try {
      const res = await fetch(`${config.public.apiBase}/admin/users`, {
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
      });
      if (res.ok) {
        const data = await res.json();
        return data.users;
      } else {
        const errorData = await res.json();
        throw new Error(errorData.error || `API error: ${res.status}`);
      }
    } catch (err) {
      console.error('Error fetching users:', err);
      throw err;
    }
  };

  const setUserAdminStatus = async (userId, isAdmin) => {
    if (!token.value) throw new Error('No authentication token found.');

    try {
      const res = await fetch(`${config.public.apiBase}/admin/users/${userId}/admin`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token.value}`,
        },
        body: JSON.stringify({ is_admin: isAdmin }),
      });

      if (res.ok) {
        return await res.json();
      } else {
        const errorData = await res.json();
        throw new Error(errorData.error || `API error: ${res.status}`);
      }
    } catch (err) {
      console.error('Error setting admin status:', err);
      throw err;
    }
  };

  const updateUserStatus = async (userId, status) => {
    if (!token.value) throw new Error('No authentication token found.');

    try {
      const res = await fetch(`${config.public.apiBase}/admin/users/${userId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token.value}`,
        },
        body: JSON.stringify({ status }),
      });

      if (res.ok) {
        return await res.json();
      } else {
        const errorData = await res.json();
        throw new Error(errorData.error || `API error: ${res.status}`);
      }
    } catch (err) {
      console.error('Error updating user status:', err);
      throw err;
    }
  };

  const deleteUser = async (userId) => {
    if (!token.value) throw new Error('No authentication token found.');

    try {
      const res = await fetch(`${config.public.apiBase}/admin/users/${userId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
      });

      if (res.ok) {
        return await res.json();
      } else {
        const errorData = await res.json();
        throw new Error(errorData.error || `API error: ${res.status}`);
      }
    } catch (err) {
      console.error('Error deleting user:', err);
      throw err;
    }
  };

  // Computed property for admin status
  const isAdmin = computed(() => {
    return user.value?.email === 'messenlien@gmail.com'
  })

  return {
    token,
    user,
    isLoggedIn,
    isInitialized,
    isAdmin,
    initializeClientAuth,
    initializeGoogleAuth,
    loginWithGoogle,
    logout,
    fetchUser,
    updateUserProfile,
    fetchBowSetups,
    addBowSetup,
    updateBowSetup,
    deleteBowSetup,
    addArrowToSetup,
    fetchSetupArrows,
    deleteArrowFromSetup,
    updateArrowInSetup,
    checkAdminStatus,
    getAllUsers,
    setUserAdminStatus,
    updateUserStatus,
    deleteUser,
  };
};
