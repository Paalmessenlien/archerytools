
import { defineNuxtPlugin } from '#app';
import vue3GoogleLogin from 'vue3-google-login';

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.use(vue3GoogleLogin, {
    clientId: process.env.NUXT_PUBLIC_GOOGLE_CLIENT_ID,
  });
});
