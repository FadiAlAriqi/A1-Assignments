<template>
  <div class="projects-container">
    <div class="page-header">
      <h2>{{ $t('projects.title') }}</h2>
      <router-link to="/projects/create" class="btn-primary">
        + {{ $t('projects.createProject') }}
      </router-link>
    </div>

    <div v-if="error" class="alert alert-error">
      {{ error }}
    </div>

    <div v-if="loading" class="loading">
      <span class="spinner"></span>
      {{ $t('common.loading') }}
    </div>

    <div v-else-if="projects.length === 0" class="no-data">
      {{ $t('projects.noProjects') }}
    </div>

    <div v-else class="table-container">
      <table>
        <thead>
          <tr>
            <th>{{ $t('projects.title_field') }}</th>
            <th>{{ $t('projects.description') }}</th>
            <th>{{ $t('projects.owner') }}</th>
            <th>{{ $t('projects.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="project in projects" :key="project.id">
            <td>{{ project.title }}</td>
            <td>{{ project.description || '-' }}</td>
            <td>{{ getOwnerName(project.owner_id) }}</td>
            <td class="actions-cell">
              <router-link :to="`/projects/${project.id}`" class="btn-small btn-info">
                {{ $t('common.view') }}
              </router-link>
              <router-link :to="`/projects/${project.id}/edit`" class="btn-small btn-warning">
                {{ $t('common.edit') }}
              </router-link>
              <button @click="deleteProject(project.id)" class="btn-small btn-danger">
                {{ $t('common.delete') }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useProjectsStore, useUsersStore } from '../../store';

const projectsStore = useProjectsStore();
const usersStore = useUsersStore();
const projects = ref([]);
const loading = ref(false);
const error = ref('');

onMounted(async () => {
  await fetchProjects();
});

const fetchProjects = async () => {
  loading.value = true;
  error.value = '';
  try {
    await projectsStore.fetchProjects();
    await usersStore.fetchUsers();
    projects.value = projectsStore.projects;
  } catch (err) {
    error.value = 'Failed to load projects';
  } finally {
    loading.value = false;
  }
};

const getOwnerName = (ownerId) => {
  const user = usersStore.users.find(u => u.id === ownerId);
  return user ? user.name : 'Unknown';
};

const deleteProject = async (id) => {
  if (confirm('Are you sure?')) {
    try {
      await projectsStore.deleteProject(id);
      projects.value = projectsStore.projects;
    } catch (err) {
      error.value = 'Failed to delete project';
    }
  }
};
</script>

<style scoped>
.projects-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  font-size: 24px;
  font-weight: 700;
  color: #333;
  margin: 0;
}

.dark .page-header h2 {
  color: #e0e0e0;
}

.btn-primary {
  background-color: #3b82f6;
  color: white;
  padding: 10px 16px;
  border-radius: 6px;
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  transition: background-color 0.2s;
  display: inline-block;
}

.btn-primary:hover {
  background-color: #1e40af;
}

.alert {
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 16px;
}

.alert-error {
  background-color: #fee2e2;
  color: #991b1b;
  border: 1px solid #fca5a5;
}

.dark .alert-error {
  background-color: #7f1d1d;
  color: #fee2e2;
  border-color: #dc2626;
}

.loading {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 20px;
  font-size: 14px;
  color: #666;
}

.dark .loading {
  color: #a0a0a0;
}

.no-data {
  text-align: center;
  padding: 40px 20px;
  color: #666;
  font-size: 14px;
}

.dark .no-data {
  color: #a0a0a0;
}

.table-container {
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.dark .table-container {
  background-color: #2d2d2d;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background-color: #f3f4f6;
}

.dark thead {
  background-color: #1a1a1a;
}

th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #e5e7eb;
  font-size: 14px;
}

.dark th {
  color: #e0e0e0;
  border-bottom-color: #404040;
}

td {
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
  font-size: 14px;
  color: #333;
}

.dark td {
  border-bottom-color: #404040;
  color: #e0e0e0;
}

tbody tr:hover {
  background-color: #f9fafb;
}

.dark tbody tr:hover {
  background-color: #404040;
}

.actions-cell {
  display: flex;
  gap: 8px;
}

.btn-small {
  padding: 6px 12px;
  border-radius: 4px;
  border: none;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  transition: all 0.2s;
}

.btn-info {
  background-color: #3b82f6;
  color: white;
}

.btn-info:hover {
  background-color: #1e40af;
}

.btn-warning {
  background-color: #f59e0b;
  color: white;
}

.btn-warning:hover {
  background-color: #d97706;
}

.btn-danger {
  background-color: #ef4444;
  color: white;
}

.btn-danger:hover {
  background-color: #dc2626;
}
</style>
