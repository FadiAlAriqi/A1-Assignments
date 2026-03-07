<template>
  <div id="app" :class="{ dark: isDark }">
    <router-view />
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useThemeStore } from './store';

const themeStore = useThemeStore();
const isDark = computed(() => themeStore.isDark);
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  width: 100%;
  height: 100%;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #ffffff;
  color: #333333;
  transition: background-color 0.3s, color 0.3s;
}

body.dark {
  background-color: #1a1a1a;
  color: #e0e0e0;
}

.dark {
  background-color: #1a1a1a;
  color: #e0e0e0;
}
</style>
