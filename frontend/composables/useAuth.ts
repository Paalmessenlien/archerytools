
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

  const loginWithGoogle = () => {
    console.log('loginWithGoogle called');
    return new Promise((resolve, reject) => {
      googleSdkLoaded((google) => {
        console.log('Google SDK loaded', google);
        google.accounts.oauth2.initCodeClient({
          client_id: config.public.googleClientId,
          scope: 'email profile openid',
          callback: (response) => {
            console.log('Google callback response:', response);
            if (response.code) {
              fetch('/api/auth/google', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({ token: response.code }),
              })
                .then((res) => res.json())
                .then((data) => {
                  if (data.token) {
                    setToken(data.token);
                    resolve(data.token);
                  } else {
                    reject(data.error || 'Failed to get token');
                  }
                })
                .catch((err) => reject(err));
            } else {
              reject('No code in response');
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
      const res = await fetch('/api/user', {
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
