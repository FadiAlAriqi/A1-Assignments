<template>
  <div class="dashboard-container">
    <Navbar />
    <div class="dashboard-content">
      <Sidebar />
      <main class="main-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import Navbar from '../components/Navbar.vue';
import Sidebar from '../components/Sidebar.vue';
import { useSessionTimeout } from '../composables/useSessionTimeout';

useSessionTimeout();
</script>

<style scoped>
.dashboard-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f9fafb;
}

.dark .dashboard-container {
  background-color: #1a1a1a;
}

.dashboard-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}
</style>
