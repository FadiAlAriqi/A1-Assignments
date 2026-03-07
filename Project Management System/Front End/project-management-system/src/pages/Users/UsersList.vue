<template>
  <div class="users-container">
    <div class="page-header">
      <h2>{{ $t('users.title') }}</h2>
      <router-link to="/users/create" class="btn-primary">
        + {{ $t('users.createUser') }}
      </router-link>
    </div>

    <div v-if="error" class="alert alert-error">
      {{ error }}
    </div>

    <div v-if="loading" class="loading">
      <span class="spinner"></span>
      {{ $t('common.loading') }}
    </div>

    <div v-else-if="users.length === 0" class="no-data">
      {{ $t('users.noUsers') }}
    </div>

    <div v-else class="table-container">
      <table>
        <thead>
          <tr>
            <th>{{ $t('users.name') }}</th>
            <th>{{ $t('users.username') }}</th>
            <th>{{ $t('users.email') }}</th>
            <th>{{ $t('users.isActive') }}</th>
            <th>{{ $t('users.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.name }}</td>
            <td>{{ user.username }}</td>
            <td>{{ user.email }}</td>
            <td>
              <span :class="{ 'badge-active': user.is_active, 'badge-inactive': !user.is_active }">
                {{ user.is_active ? 'Yes' : 'No' }}
              </span>
            </td>
            <td class="actions-cell">
              <router-link :to="`/users/${user.id}`" class="btn-small btn-info">
                {{ $t('common.view') }}
              </router-link>
              <router-link :to="`/users/${user.id}/edit`" class="btn-small btn-warning">
                {{ $t('common.edit') }}
              </router-link>
              <button @click="deleteUser(user.id)" class="btn-small btn-danger">
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
import { useUsersStore } from '../../store';

const usersStore = useUsersStore();
const users = ref([]);
const loading = ref(false);
const error = ref('');

onMounted(async () => {
  await fetchUsers();
});

const fetchUsers = async () => {
  loading.value = true;
  error.value = '';
  try {
    await usersStore.fetchUsers();
    users.value = usersStore.users;
  } catch (err) {
    error.value = 'Failed to load users';
  } finally {
    loading.value = false;
  }
};

const deleteUser = async (id) => {
  if (confirm('Are you sure?')) {
    try {
      await usersStore.deleteUser(id);
      users.value = usersStore.users;
    } catch (err) {
      error.value = 'Failed to delete user';
    }
  }
};
</script>

<style scoped>
.users-container {
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

.badge-active {
  display: inline-block;
  padding: 4px 8px;
  background-color: #d1fae5;
  color: #065f46;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.badge-inactive {
  display: inline-block;
  padding: 4px 8px;
  background-color: #fee2e2;
  color: #991b1b;
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
