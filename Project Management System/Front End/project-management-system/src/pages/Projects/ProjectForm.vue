<template>
  <div class="form-container">
    <div class="page-header">
      <router-link to="/projects" class="btn-back">← {{ $t('common.back') }}</router-link>
      <h2>{{ isEdit ? $t('projects.editProject') : $t('projects.createProject') }}</h2>
    </div>

    <div v-if="error" class="alert alert-error">
      {{ error }}
    </div>

    <form @submit.prevent="handleSubmit" class="form-card">
      <div class="form-group">
        <label for="title">{{ $t('projects.title_field') }}</label>
        <input
          id="title"
          v-model="form.title"
          type="text"
          :placeholder="$t('projects.title_field')"
          :readonly="isView"
          required
        />
      </div>

      <div class="form-group">
        <label for="description">{{ $t('projects.description') }}</label>
        <textarea
          id="description"
          v-model="form.description"
          :placeholder="$t('projects.description')"
          :readonly="isView"
          rows="4"
        ></textarea>
      </div>

      <div class="form-group">
        <label for="owner">{{ $t('projects.owner') }}</label>
        <select v-model="form.owner_id" :disabled="isView" required>
          <option value="">Select Owner</option>
          <option v-for="user in users" :key="user.id" :value="user.id">
            {{ user.name }}
          </option>
        </select>
      </div>

      <div v-if="isView" class="form-actions">
        <router-link :to="`/projects/${projectId}/edit`" class="btn-primary">
          {{ $t('common.edit') }}
        </router-link>
      </div>

      <div v-else class="form-actions">
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ isEdit ? $t('common.update') : $t('common.create') }}
        </button>
        <router-link to="/projects" class="btn-secondary">
          {{ $t('common.cancel') }}
        </router-link>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useProjectsStore, useUsersStore, useAuthStore } from '../../store';

const router = useRouter();
const route = useRoute();
const projectsStore = useProjectsStore();
const usersStore = useUsersStore();
const authStore = useAuthStore();

const projectId = route.params.id;
const isEdit = computed(() => !!projectId && route.name === 'EditProject');
const isView = computed(() => !!projectId && route.name === 'ViewProject');

const form = ref({
  title: '',
  description: '',
  owner_id: '',
});

const users = ref([]);
const loading = ref(false);
const error = ref('');

onMounted(async () => {
  try {
    await usersStore.fetchUsers();
    users.value = usersStore.users;

    if (projectId) {
      const project = await projectsStore.fetchProject(projectId);
      form.value = {
        title: project.title,
        description: project.description || '',
        owner_id: project.owner_id,
      };
    } else {
      form.value.owner_id = authStore.user?.id || '';
    }
  } catch (err) {
    error.value = 'Failed to load data';
  }
});

const handleSubmit = async () => {
  loading.value = true;
  error.value = '';

  try {
    const projectData = {
      title: form.value.title,
      description: form.value.description,
      owner_id: form.value.owner_id,
    };

    if (isEdit.value) {
      await projectsStore.updateProject(projectId, projectData);
    } else {
      await projectsStore.createProject(projectData);
    }

    router.push('/projects');
  } catch (err) {
    error.value = err.response?.data?.detail || 'Operation failed';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.form-container {
  padding: 20px;
  max-width: 600px;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.btn-back {
  background: none;
  border: none;
  color: #3b82f6;
  text-decoration: none;
  font-size: 14px;
  cursor: pointer;
  padding: 0;
}

.btn-back:hover {
  text-decoration: underline;
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

.form-card {
  background-color: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.dark .form-card {
  background-color: #2d2d2d;
}

.form-group {
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.dark .form-group label {
  color: #e0e0e0;
}

.form-group input,
.form-group textarea,
.form-group select {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
}

.dark .form-group input,
.dark .form-group textarea,
.dark .form-group select {
  background-color: #1a1a1a;
  border-color: #404040;
  color: #e0e0e0;
}

.form-group input:readonly,
.form-group textarea:readonly {
  background-color: #f9fafb;
  cursor: not-allowed;
}

.dark .form-group input:readonly,
.dark .form-group textarea:readonly {
  background-color: #1a1a1a;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.btn-primary, .btn-secondary {
  padding: 10px 16px;
  border-radius: 6px;
  border: none;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  transition: all 0.2s;
}

.btn-primary {
  background-color: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background-color: #1e40af;
}

.btn-secondary {
  background-color: #e5e7eb;
  color: #333;
}

.dark .btn-secondary {
  background-color: #404040;
  color: #e0e0e0;
}

.btn-secondary:hover {
  background-color: #d1d5db;
}

.dark .btn-secondary:hover {
  background-color: #505050;
}
</style>
