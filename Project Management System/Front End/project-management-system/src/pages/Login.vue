<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="login-title">{{ $t('auth.loginTitle') }}</h1>
      <p class="login-subtitle">{{ $t('auth.login') }}</p>

      <form @submit.prevent="handleLogin" class="login-form">
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
          <label for="password">{{ $t('auth.password') }}</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            :placeholder="$t('auth.password')"
            required
          />
        </div>

        <button type="submit" class="btn-primary btn-full" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>{{ $t('auth.login') }}</span>
        </button>
      </form>

      <div class="login-footer">
        <p>{{ $t('auth.noAccount') }}</p>
        <router-link to="/signup" class="link">{{ $t('auth.signup') }}</router-link>
      </div>

      <div v-if="error" class="alert alert-error">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup>
  import { ref, nextTick } from 'vue';
  import { useRouter } from 'vue-router';
  import { useAuthStore } from '../store';

  const router = useRouter();
  const authStore = useAuthStore();

  const form = ref({
    username: '',
    password: '',
  });

  const loading = ref(false);
  const error = ref('');

  const handleLogin = async () => {
    loading.value = true;
    error.value = '';
    try {
      await authStore.login(form.value.username, form.value.password);

      // الانتظار حتى يتم تحديث reactive state
      await nextTick();

      // التحويل بعد تسجيل الدخول
      router.replace('/'); // replace أفضل من push هنا
    } catch (err) {
      error.value = err.response?.data?.detail || 'Login failed. Please try again.';
    } finally {
      loading.value = false;
    }
  };
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 400px;
}

.dark .login-card {
  background: #2d2d2d;
  color: #e0e0e0;
}

.login-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
  color: #333;
}

.dark .login-title {
  color: #e0e0e0;
}

.login-subtitle {
  font-size: 14px;
  color: #666;
  margin-bottom: 24px;
}

.dark .login-subtitle {
  color: #a0a0a0;
}

.login-form {
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

.login-footer {
  text-align: center;
  font-size: 14px;
  color: #666;
}

.dark .login-footer {
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
