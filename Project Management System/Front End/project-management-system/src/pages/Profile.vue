<template>
  <div class="profile-container">
    <div class="page-header">
      <h2>{{ $t('profile.title') }}</h2>
    </div>

    <div v-if="error" class="alert alert-error">
      {{ error }}
    </div>

    <div v-if="success" class="alert alert-success">
      {{ $t('profile.updateSuccess') }}
    </div>

    <form @submit.prevent="handleSubmit" class="form-card">
      <div class="form-group">
        <label for="name">{{ $t('profile.name') }}</label>
        <input
          id="name"
          v-model="form.name"
          type="text"
          :placeholder="$t('profile.name')"
          required
        />
      </div>

      <div class="form-group">
        <label for="username">{{ $t('profile.username') }}</label>
        <input
          id="username"
          v-model="form.username"
          type="text"
          :placeholder="$t('profile.username')"
          required
        />
      </div>

      <div class="form-group">
        <label for="email">{{ $t('profile.email') }}</label>
        <input
          id="email"
          v-model="form.email"
          type="email"
          :placeholder="$t('profile.email')"
          required
        />
      </div>

      <hr class="divider" />

      <div class="form-group">
        <label for="password">{{ $t('profile.newPassword') }}</label>
        <input
          id="password"
          v-model="form.password"
          type="password"
          :placeholder="$t('profile.newPassword')"
        />
        <small>{{ $t('common.loading') }}</small>
      </div>

      <div class="form-group">
        <label for="confirmPassword">{{ $t('profile.confirmNewPassword') }}</label>
        <input
          id="confirmPassword"
          v-model="form.confirmPassword"
          type="password"
          :placeholder="$t('profile.confirmNewPassword')"
        />
        <span v-if="passwordMismatch" class="error-text">
          {{ $t('auth.passwordMismatch') }}
        </span>
      </div>

      <div class="form-actions">
        <button type="submit" class="btn-primary" :disabled="loading || passwordMismatch">
          {{ $t('common.save') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useAuthStore, useUsersStore } from '../store';

const authStore = useAuthStore();
const usersStore = useUsersStore();

const form = ref({
  name: '',
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
});

const loading = ref(false);
const error = ref('');
const success = ref(false);

const passwordMismatch = computed(() => {
  return form.value.password && form.value.confirmPassword && form.value.password !== form.value.confirmPassword;
});

onMounted(() => {
  if (authStore.user) {
    form.value = {
      name: authStore.user.name,
      username: authStore.user.username,
      email: authStore.user.email,
      password: '',
      confirmPassword: '',
    };
  }
});

const handleSubmit = async () => {
  if (passwordMismatch.value) return;

  loading.value = true;
  error.value = '';
  success.value = false;

  try {
    const userData = {
      name: form.value.name,
      username: form.value.username,
      email: form.value.email,
    };

    if (form.value.password) {
      userData.password = form.value.password;
    }

    await usersStore.updateUser(authStore.user.id, userData);
    
    // Update local user data
    authStore.user = {
      ...authStore.user,
      ...userData,
    };
    localStorage.setItem('user', JSON.stringify(authStore.user));

    form.value.password = '';
    form.value.confirmPassword = '';
    success.value = true;

    setTimeout(() => {
      success.value = false;
    }, 3000);
  } catch (err) {
    error.value = err.response?.data?.detail || 'Update failed';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.profile-container {
  padding: 20px;
  max-width: 600px;
}

.page-header {
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

.alert-success {
  background-color: #d1fae5;
  color: #065f46;
  border: 1px solid #6ee7b7;
}

.dark .alert-error {
  background-color: #7f1d1d;
  color: #fee2e2;
  border-color: #dc2626;
}

.dark .alert-success {
  background-color: #064e3b;
  color: #d1fae5;
  border-color: #047857;
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

.form-group small {
  font-size: 12px;
  color: #666;
}

.dark .form-group small {
  color: #a0a0a0;
}

.error-text {
  font-size: 12px;
  color: #ef4444;
}

.dark .error-text {
  color: #fca5a5;
}

.divider {
  border: none;
  border-top: 1px solid #e5e7eb;
  margin: 24px 0;
}

.dark .divider {
  border-top-color: #404040;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.btn-primary {
  padding: 10px 16px;
  border-radius: 6px;
  border: none;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  background-color: #3b82f6;
  color: white;
  transition: all 0.2s;
}

.btn-primary:hover {
  background-color: #1e40af;
}

.btn-primary:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}
</style>
