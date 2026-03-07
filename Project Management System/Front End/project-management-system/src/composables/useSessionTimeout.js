import { onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../store';

const SESSION_TIMEOUT = 30 * 60 * 1000; // 30 minutes
let timeoutId = null;
let activityTimeoutId = null;

export function useSessionTimeout() {
  const router = useRouter();
  const authStore = useAuthStore();

  const resetTimeout = () => {
    // Clear existing timeouts
    if (timeoutId) clearTimeout(timeoutId);
    if (activityTimeoutId) clearTimeout(activityTimeoutId);

    // Set new timeout
    timeoutId = setTimeout(() => {
      authStore.logout();
      router.push('/login');
    }, SESSION_TIMEOUT);
  };

  const handleActivity = () => {
    resetTimeout();
  };

  onMounted(() => {
    if (authStore.isAuthenticated) {
      resetTimeout();

      // Add event listeners for user activity
      document.addEventListener('mousemove', handleActivity);
      document.addEventListener('keydown', handleActivity);
      document.addEventListener('click', handleActivity);
      document.addEventListener('scroll', handleActivity);
    }
  });

  onUnmounted(() => {
    // Remove event listeners
    document.removeEventListener('mousemove', handleActivity);
    document.removeEventListener('keydown', handleActivity);
    document.removeEventListener('click', handleActivity);
    document.removeEventListener('scroll', handleActivity);

    // Clear timeouts
    if (timeoutId) clearTimeout(timeoutId);
    if (activityTimeoutId) clearTimeout(activityTimeoutId);
  });

  return {
    resetTimeout,
  };
}
