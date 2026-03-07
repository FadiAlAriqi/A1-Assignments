<template>
  <div class="signup-container">
    <div class="signup-card">
      <h1 class="signup-title">{{ $t('auth.signupTitle') }}</h1>
      <p class="signup-subtitle">{{ $t('auth.signup') }}</p>

      <form @submit.prevent="handleSignup" class="signup-form">
        <div class="form-group">
          <label for="name">{{ $t('auth.name') }}</label>
          <input
            id="name"
            v-model="form.name"
            type="text"
            :placeholder="$t('auth.name')"
            required
          />
        </div>

        <div class="form-group">
          <label for="username">{{ $t('auth.username') }}</label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            :placeholder="$t('auth.username')"
            required
          />
        </div>

        <div class="form-group">
          <label for="email">{{ $t('auth.email') }}</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            :placeholder="$t('auth.email')"
            required
          />
        </div>

        <div class="form-group">
          <label for="password">{{ $t('auth.password') }}</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            :placeholder="$t('auth.password')"
            required
          />
        </div>

        <div class="form-group">
          <label for="confirmPassword">{{ $t('auth.confirmPassword') }}</label>
          <input
            id="confirmPassword"
            v-model="form.confirmPassword"
            type="password"
            :placeholder="$t('auth.confirmPassword')"
            required
          />
          <span v-if="passwordMismatch" class="error-text">
            {{ $t('auth.passwordMismatch') }}
          </span>
        </div>

        <button type="submit" class="btn-primary btn-full" :disabled="loading || passwordMismatch">
          <span v-if="loading" class="spinner"></span>
          <span v-else>{{ $t('auth.signup') }}</span>
        </button>
      </form>

      <div class="signup-footer">
        <p>{{ $t('auth.haveAccount') }}</p>
        <router-link to="/login" class="link">{{ $t('auth.login') }}</router-link>
      </div>

      <div v-if="error" class="alert alert-error">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../store';

const router = useRouter();
const authStore = useAuthStore();

const form = ref({
  name: '',
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
});

const loading = ref(false);
const error = ref('');

const passwordMismatch = computed(() => {
  return form.value.password && form.value.confirmPassword && form.value.password !== form.value.confirmPassword;
});

const handleSignup = async () => {
  if (passwordMismatch.value) return;

  loading.value = true;
  error.value = '';

  try {
    await authStore.signup(form.value.name, form.value.username, form.value.email, form.value.password);
    router.push('/');
  } catch (err) {
    error.value = err.response?.data?.detail || 'Signup failed. Please try again.';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.signup-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.signup-card {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 450px;
}

.dark .signup-card {
  background: #2d2d2d;
  color: #e0e0e0;
}

.signup-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
  color: #333;
}

.dark .signup-title {
  color: #e0e0e0;
}

.signup-subtitle {
  font-size: 14px;
  color: #666;
  margin-bottom: 24px;
}

.dark .signup-subtitle {
  color: #a0a0a0;
}

.signup-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.dark .form-group label {
  color: #e0e0e0;
}

.form-group input {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.dark .form-group input {
  background-color: #1a1a1a;
  border-color: #404040;
  color: #e0e0e0;
}

.error-text {
  font-size: 12px;
  color: #ef4444;
}

.dark .error-text {
  color: #fca5a5;
}

.btn-full {
  width: 100%;
  padding: 12px;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.signup-footer {
  text-align: center;
  font-size: 14px;
  color: #666;
}

.dark .signup-footer {
  color: #a0a0a0;
}

.link {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
  margin-left: 4px;
}

.link:hover {
  text-decoration: underline;
}

.alert {
  margin-top: 16px;
}
</style>
