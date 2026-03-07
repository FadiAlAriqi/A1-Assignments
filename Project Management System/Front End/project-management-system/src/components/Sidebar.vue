<template>
  <aside class="sidebar">
    <nav class="sidebar-nav">
      <router-link
        to="/tasks"
        class="sidebar-item"
        :class="{ active: isActive('/tasks') }"
      >
        📋 {{ $t('sidebar.tasks') }}
      </router-link>
      <router-link
        to="/users"
        class="sidebar-item"
        :class="{ active: isActive('/users') }"
      >
        👥 {{ $t('sidebar.users') }}
      </router-link>
      <router-link
        to="/projects"
        class="sidebar-item"
        :class="{ active: isActive('/projects') }"
      >
        📁 {{ $t('sidebar.projects') }}
      </router-link>
    </nav>
  </aside>
</template>

<script setup>
import { useRoute } from 'vue-router';

const route = useRoute();

const isActive = (path) => {
  return route.path.startsWith(path);
};
</script>

<style scoped>
.sidebar {
  width: 250px;
  background-color: white;
  border-right: 1px solid #e5e7eb;
  padding: 20px 0;
  overflow-y: auto;
  flex-shrink: 0;
}

.dark .sidebar {
  background-color: #2d2d2d;
  border-right-color: #404040;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 0 12px;
}

.sidebar-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 6px;
  color: #666;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  cursor: pointer;
}

.dark .sidebar-item {
  color: #a0a0a0;
}

.sidebar-item:hover {
  background-color: #f3f4f6;
  color: #333;
}

.dark .sidebar-item:hover {
  background-color: #404040;
  color: #e0e0e0;
}

.sidebar-item.active {
  background-color: #dbeafe;
  color: #1e40af;
  font-weight: 600;
}

.dark .sidebar-item.active {
  background-color: #1e3a8a;
  color: #93c5fd;
}
</style>
