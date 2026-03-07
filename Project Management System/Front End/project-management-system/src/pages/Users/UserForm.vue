<template>
  <div class="form-container">
    <div class="page-header">
      <router-link to="/users" class="btn-back">← {{ $t('common.back') }}</router-link>
      <h2>{{ isEdit ? $t('users.editUser') : $t('users.createUser') }}</h2>
    </div>

    <div v-if="error" class="alert alert-error">
      {{ error }}
    </div>

    <form @submit.prevent="handleSubmit" class="form-card">
      <div class="form-group">
        <label for="name">{{ $t('users.name') }}</label>
        <input
          id="name"
          v-model="form.name"
          type="text"
          :placeholder="$t('users.name')"
          :readonly="isView"
        />
        <span v-if="submitted && !form.name" class="error-text">
          Name is required
        </span>
      </div>

      <div class="form-group">
        <label for="username">{{ $t('users.username') }}</label>
        <input
          id="username"
          v-model="form.username"
          type="text"
          :placeholder="$t('users.username')"
          :readonly="isView"
        />
        <span v-if="submitted && !form.username" class="error-text">
          Username is required
        </span>
      </div>

      <div class="form-group">
        <label for="email">{{ $t('users.email') }}</label>
        <input
          id="email"
          v-model="form.email"
          type="email"
          :placeholder="$t('users.email')"
          :readonly="isView"
        />
        <span v-if="submitted && !form.email" class="error-text">
          Email is required
        </span>
      </div>

      <div v-if="!isView" class="form-group">
        <label for="password">{{ $t('users.password') }}</label>
        <input
          id="password"
          v-model="form.password"
          type="password"
          :placeholder="$t('users.password')"
        />
        <span v-if="submitted && isEdit === false && !form.password" class="error-text">
          Password is required
        </span>
      </div>

      <div v-if="!isView" class="form-group">
        <label for="confirmPassword">{{ $t('users.confirmPassword') }}</label>
        <input
          id="confirmPassword"
          v-model="form.confirmPassword"
          type="password"
          :placeholder="$t('users.confirmPassword')"
        />
        <span v-if="passwordMismatch" class="error-text">
          {{ $t('auth.passwordMismatch') }}
        </span>
        <span v-if="submitted && isEdit === false && !form.confirmPassword" class="error-text">
          Confirm Password is required
        </span>
      </div>

      <div v-if="isView" class="form-actions">
        <router-link :to="`/users/${userId}/edit`" class="btn-primary">
          {{ $t('common.edit') }}
        </router-link>
      </div>

      <div v-else class="form-actions">
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ isEdit ? $t('common.update') : $t('common.create') }}
        </button>
        <router-link to="/users" class="btn-secondary">
          {{ $t('common.cancel') }}
        </router-link>
      </div>
    </form>
  </div>
</template>

<script setup>
  import { ref, computed, onMounted } from 'vue';
  import { useRouter, useRoute } from 'vue-router';
  import { useUsersStore } from '../../store';

  const router = useRouter();
  const route = useRoute();
  const usersStore = useUsersStore();

  const userId = route.params.id;
  const isEdit = computed(() => !!userId && route.name === 'EditUser');
  const isView = computed(() => !!userId && route.name === 'ViewUser');

  const form = ref({
    name: '',
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  const loading = ref(false);
  const error = ref('');
  const submitted = ref(false);

  const passwordMismatch = computed(() => {
    return form.value.password || form.value.confirmPassword 
      ? form.value.password !== form.value.confirmPassword 
      : false;
  });

  onMounted(async () => {
    if (userId) {
      try {
        const user = await usersStore.fetchUser(userId);
        form.value = {
          name: user.name,
          username: user.username,
          email: user.email,
          password: '',
          confirmPassword: '',
        };
      } catch (err) {
        error.value = 'Failed to load user';
      }
    }
  });

  const validateForm = () => {
    if (!form.value.name || !form.value.username || !form.value.email) {
      return false;
    }

    if (!isEdit.value) {
      if (!form.value.password || !form.value.confirmPassword) {
        return false;
      }
      if (form.value.password !== form.value.confirmPassword) {
        return false;
      }
    }

    if (isEdit.value) {
      if (form.value.password || form.value.confirmPassword) {
        if (!form.value.password || !form.value.confirmPassword) {
          return false;
        }
        if (form.value.password !== form.value.confirmPassword) {
          return false;
        }
      }
    }

    return true;
  };

  const handleSubmit = async () => {
    submitted.value = true;
    
    if (!validateForm()) {
      error.value = 'Please fill in all required fields and ensure passwords match.';
      return;
    }

    loading.value = true;
    error.value = '';

    try {
      const userData = {
        name: form.value.name,
        username: form.value.username,
        email: form.value.email,
      };

      if (form.value.password) {
        userData.password = form.value.password;
      }

      if (isEdit.value) {
        await usersStore.updateUser(userId, userData);
      } else {
        await usersStore.createUser(userData);
      }

      router.push('/users');
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

  .form-group input {
    padding: 10px 12px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 14px;
  }

  .dark .form-group input {
    background-color: #1a1a1a;
    border-color: #404040;
    color: #e0e0e0;
  }

  .form-group input:readonly {
    background-color: #f9fafb;
    cursor: not-allowed;
  }

  .dark .form-group input:readonly {
    background-color: #1a1a1a;
  }

  .error-text {
    font-size: 12px;
    color: #ef4444;
  }

  .dark .error-text {
    color: #fca5a5;
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
