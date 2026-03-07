import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import i18n from './i18n';
import './style.css';
import axios from './axios';
import { useAuthStore } from './store';
import { useThemeStore } from './store';

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);
app.use(i18n);
app.config.globalProperties.$axios = axios;

// Initialize auth and theme
const authStore = useAuthStore();
const themeStore = useThemeStore();

authStore.loadUserFromStorage();
themeStore.initTheme();

app.mount('#app');
