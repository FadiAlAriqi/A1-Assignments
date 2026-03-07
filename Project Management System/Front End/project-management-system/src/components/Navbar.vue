<template>
  <nav class="navbar">
    <div class="navbar-container">
      <div class="navbar-brand">
        <h1>Admin Panel</h1>
      </div>

      <div class="navbar-actions">
        <!-- Language Selector -->
        <div class="language-selector">
          <select v-model="currentLocale" @change="changeLanguage" class="language-select">
            <option value="en">English</option>
            <option value="ar">العربية</option>
          </select>
        </div>

        <!-- Theme Toggle -->
        <button @click="toggleTheme" class="theme-toggle" :title="$t('navbar.theme')">
          <span v-if="isDark">☀️</span>
          <span v-else>🌙</span>
        </button>

        <!-- Profile Dropdown -->
        <div class="profile-dropdown">
          <button @click="toggleDropdown" class="profile-button">
            👤 {{ user?.name || 'User' }}
          </button>
          <div v-if="showDropdown" class="dropdown-menu">
            <div class="dropdown-item disabled">{{ user?.name }}</div>
            <router-link to="/profile" class="dropdown-item" @click="showDropdown = false">
              {{ $t('navbar.profile') }}
            </router-link>
            <button @click="handleLogout" class="dropdown-item logout-btn">
              {{ $t('navbar.logout') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore, useThemeStore, useLanguageStore } from '../store';
import { useI18n } from 'vue-i18n';

const router = useRouter();
const authStore = useAuthStore();
const themeStore = useThemeStore();
const languageStore = useLanguageStore();
const { locale } = useI18n();

const showDropdown = ref(false);
const user = computed(() => authStore.user);
const isDark = computed(() => themeStore.isDark);
const currentLocale = ref(locale.value);

const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value;
};

const toggleTheme = () => {
  themeStore.toggleTheme();
};

const changeLanguage = () => {
  languageStore.setLocale(currentLocale.value);
  locale.value = currentLocale.value;
  document.documentElement.lang = currentLocale.value;
  document.documentElement.dir = currentLocale.value === 'ar' ? 'rtl' : 'ltr';
};

const handleLogout = () => {
  authStore.logout();
  router.push('/login');
};
</script>

<style scoped>
.navbar {
  background-color: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 16px 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.dark .navbar {
  background-color: #2d2d2d;
  border-bottom-color: #404040;
}

.navbar-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
}

.navbar-brand h1 {
  font-size: 24px;
  font-weight: 700;
  color: #333;
  margin: 0;
}

.dark .navbar-brand h1 {
  color: #e0e0e0;
}

.navbar-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.language-selector {
  position: relative;
}

.language-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background-color: white;
  color: #333;
  cursor: pointer;
  font-size: 14px;
}

.dark .language-select {
  background-color: #1a1a1a;
  border-color: #404040;
  color: #e0e0e0;
}

.theme-toggle {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: background-color 0.2s;
}

.theme-toggle:hover {
  background-color: #f3f4f6;
}

.dark .theme-toggle:hover {
  background-color: #404040;
}

.profile-dropdown {
  position: relative;
}

.profile-button {
  background-color: #f3f4f6;
  border: 1px solid #ddd;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  transition: all 0.2s;
}

.dark .profile-button {
  background-color: #1a1a1a;
  border-color: #404040;
  color: #e0e0e0;
}

.profile-button:hover {
  background-color: #e5e7eb;
}

.dark .profile-button:hover {
  background-color: #404040;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 200px;
  margin-top: 8px;
  z-index: 1000;
}

.dark .dropdown-menu {
  background-color: #2d2d2d;
  border-color: #404040;
}

.dropdown-item {
  display: block;
  width: 100%;
  padding: 12px 16px;
  text-align: left;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 14px;
  color: #333;
  text-decoration: none;
  transition: background-color 0.2s;
}

.dark .dropdown-item {
  color: #e0e0e0;
}

.dropdown-item:hover:not(.disabled) {
  background-color: #f3f4f6;
}

.dark .dropdown-item:hover:not(.disabled) {
  background-color: #404040;
}

.dropdown-item.disabled {
  cursor: default;
  color: #999;
  font-weight: 600;
  border-bottom: 1px solid #e5e7eb;
}

.dark .dropdown-item.disabled {
  color: #666;
  border-bottom-color: #404040;
}

.logout-btn {
  color: #ef4444;
  border-top: 1px solid #e5e7eb;
}

.dark .logout-btn {
  border-top-color: #404040;
  color: #fca5a5;
}

.logout-btn:hover {
  background-color: #fee2e2 !important;
}

.dark .logout-btn:hover {
  background-color: #7f1d1d !important;
}
</style>
