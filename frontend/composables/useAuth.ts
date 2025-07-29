
import { ref } from 'vue';
import { googleSdkLoaded } from 'vue3-google-login';

// Global state - shared across all useAuth() calls
const token = ref(process.client ? localStorage.getItem('token') : null);
const user = ref(null);

export const useAuth = () => {
  const config = useRuntimeConfig();

  const setToken = (newToken) => {
    token.value = newToken;
    if (process.client) { // Add check here
      localStorage.setItem('token', newToken);
    }
  };

  const removeToken = () => {
    token.value = null;
    if (process.client) { // Add check here
      localStorage.removeItem('token');
    }
  };

  const loginWithGoogle = async () => {
    console.log('loginWithGoogle called');
    return new Promise((resolve, reject) => {
      googleSdkLoaded((google) => {
        console.log('Google SDK loaded', google);
        google.accounts.oauth2.initCodeClient({
          client_id: config.public.googleClientId,
          scope: 'email profile openid',
          callback: async (response) => {
            console.log('Google callback response:', response);
            if (response.code) {
              console.log('API Base URL:', config.public.apiBase);
              fetch(`${config.public.apiBase}/auth/google`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({ token: response.code }),
              })
                .then(async (res) => {
                  if (!res.ok) {
                    const errorData = await res.json();
                    throw new Error(errorData.error || `API error: ${res.status}`);
                  }
                  return res.json();
                })
                .then(async (data) => {
                  if (data.token) {
                    setToken(data.token);
                    resolve({ token: data.token, needsProfileCompletion: data.needs_profile_completion });
                  } else {
                    // Ensure rejection is always with an Error object
                    reject(new Error(data.error || 'Failed to get token'));
                  }
                })
                .catch((err) => {
                  console.error('Error during Google auth API call:', err);
                  reject(err); // Propagate the error
                });
            } else {
              reject(new Error('No code in response')); // Ensure rejection is always with an Error object
            }
          },
        }).requestCode();
      });
    });
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

  const updateUserProfile = async (profileData: any) => {
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
    loginWithGoogle,
    logout,
    fetchUser,
    updateUserProfile,
    fetchBowSetups,
    addBowSetup,
    deleteBowSetup,
    checkAdminStatus,
    getAllUsers,
    setUserAdminStatus,
  };
};
