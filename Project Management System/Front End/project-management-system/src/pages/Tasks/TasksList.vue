<template>
  <div class="tasks-container">
    <div class="page-header">
      <h2>{{ $t('tasks.title') }}</h2>
      <router-link to="/tasks/create" class="btn-primary">
        + {{ $t('tasks.createTask') }}
      </router-link>
    </div>

    <div v-if="error" class="alert alert-error">
      {{ error }}
    </div>

    <div v-if="loading" class="loading">
      <span class="spinner"></span>
      {{ $t('common.loading') }}
    </div>

    <div v-else-if="tasks.length === 0" class="no-data">
      {{ $t('tasks.noTasks') }}
    </div>

    <div v-else class="table-container">
      <table>
        <thead>
          <tr>
            <th>{{ $t('tasks.title_field') }}</th>
            <th>{{ $t('tasks.status') }}</th>
            <th>{{ $t('tasks.project') }}</th>
            <th>{{ $t('tasks.assignee') }}</th>
            <th>{{ $t('tasks.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="task in tasks" :key="task.id">
            <td>{{ task.title }}</td>
            <td>
              <span :class="getStatusClass(task.status)">
                {{ getStatusLabel(task.status) }}
              </span>
            </td>
            <td>{{ getProjectName(task.project_id) }}</td>
            <td>{{ getAssigneeName(task.assigned_to) }}</td>
            <td class="actions-cell">
              <router-link :to="`/tasks/${task.id}`" class="btn-small btn-info">
                {{ $t('common.view') }}
              </router-link>
              <router-link :to="`/tasks/${task.id}/edit`" class="btn-small btn-warning">
                {{ $t('common.edit') }}
              </router-link>
              <button @click="deleteTask(task.id)" class="btn-small btn-danger">
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
import { useTasksStore, useProjectsStore, useUsersStore } from '../../store';

const tasksStore = useTasksStore();
const projectsStore = useProjectsStore();
const usersStore = useUsersStore();

const tasks = ref([]);
const loading = ref(false);
const error = ref('');

onMounted(async () => {
  await fetchTasks();
});

const fetchTasks = async () => {
  loading.value = true;
  error.value = '';
  try {
    await tasksStore.fetchTasks();
    await projectsStore.fetchProjects();
    await usersStore.fetchUsers();
    tasks.value = tasksStore.tasks;
  } catch (err) {
    error.value = 'Failed to load tasks';
  } finally {
    loading.value = false;
  }
};

const getProjectName = (projectId) => {
  const project = projectsStore.projects.find(p => p.id === projectId);
  return project ? project.title : 'Unknown';
};

const getAssigneeName = (assigneeId) => {
  if (!assigneeId) return '-';
  const user = usersStore.users.find(u => u.id === assigneeId);
  return user ? user.name : 'Unknown';
};

const getStatusLabel = (status) => {
  const statusMap = {
    pending: 'Pending',
    in_progress: 'In Progress',
    completed: 'Completed',
  };
  return statusMap[status] || status;
};

const getStatusClass = (status) => {
  const classMap = {
    pending: 'badge-pending',
    in_progress: 'badge-in-progress',
    completed: 'badge-completed',
  };
  return classMap[status] || '';
};

const deleteTask = async (id) => {
  if (confirm('Are you sure?')) {
    try {
      await tasksStore.deleteTask(id);
      tasks.value = tasksStore.tasks;
    } catch (err) {
      error.value = 'Failed to delete task';
    }
  }
};
</script>

<style scoped>
.tasks-container {
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

.badge-pending {
  display: inline-block;
  padding: 4px 8px;
  background-color: #fef3c7;
  color: #92400e;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.badge-in-progress {
  display: inline-block;
  padding: 4px 8px;
  background-color: #bfdbfe;
  color: #1e40af;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.badge-completed {
  display: inline-block;
  padding: 4px 8px;
  background-color: #d1fae5;
  color: #065f46;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
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
