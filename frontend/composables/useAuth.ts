
import { ref } from 'vue';

// Global state - shared across all useAuth() calls
const token = ref(process.client ? localStorage.getItem('token') : null);
const user = ref(null);
let googleAuthClient = null; // Singleton for the Google Auth client

export const useAuth = () => {
  const config = useRuntimeConfig();

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
                  body: JSON.stringify({ token: response.code }),
                });

                if (!res.ok) {
                  const errorData = await res.json();
                  console.error('Google auth API call failed:', errorData.error || `API error: ${res.status}`);
                  return;
                }

                const data = await res.json();
                if (data.token) {
                  setToken(data.token);
                  await fetchUser();
                  // Handle redirection if needed
                  if (data.needs_profile_completion) {
                    const router = useRouter();
                    router.push('/register');
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
    if (process.client) {
      localStorage.setItem('token', newToken);
    }
  };

  const removeToken = () => {
    token.value = null;
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
      // Ask user to click again
      alert("Login service is initializing. Please click the login button again.");
    }
  };

  const logout = () => {
    removeToken();
    user.value = null;
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
      } else {
        logout();
      }
    } catch (err) {
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

  return {
    token,
    user,
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
    checkAdminStatus,
    getAllUsers,
    setUserAdminStatus,
  };
};
