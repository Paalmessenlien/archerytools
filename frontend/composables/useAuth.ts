
import { ref } from 'vue';
import { googleSdkLoaded } from 'vue3-google-login';

export const useAuth = () => {
  const config = useRuntimeConfig();
  // Initialize token only on the client side
  const token = ref(process.client ? localStorage.getItem('token') : null);
  const user = ref(null);

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
                    await fetchUser(); // Fetch user data immediately after setting token
                    resolve(data.token);
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

  return {
    token,
    user,
    loginWithGoogle,
    logout,
    fetchUser,
  };
};
