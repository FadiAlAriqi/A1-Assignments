import { defineStore } from 'pinia';
import { ref, computed, nextTick } from 'vue';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:9900';

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('user')) || null);
  const token = ref(localStorage.getItem('token') || null);
  const isAuthenticated = computed(() => !!token.value);


  const login = async (username, password) => {
    try {
      const response = await axios.post(`${API_URL}/login/`, {
        username,
        password,
      });

      token.value = response.data.access_token;
      localStorage.setItem('token', response.data.access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`;

      const userResponse = await axios.get(`${API_URL}/users/`, {
        headers: { Authorization: `Bearer ${token.value}` },
      });

      user.value = userResponse.data.find(u => u.username === username);

      if (!user.value) {
        throw new Error('User not found after login');
      }

      localStorage.setItem('user', JSON.stringify(user.value));

      return response.data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const signup = async (name, username, email, password) => {
    try {
      const response = await axios.post(`${API_URL}/signup/`, {
        name,
        username,
        email,
        password,
      });
      token.value = response.data.access_token;
      localStorage.setItem('token', response.data.access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`;
      
      user.value = response.data.user;
      localStorage.setItem('user', JSON.stringify(user.value));
      
      return response.data;
    } catch (error) {
      console.error('Signup error:', error);
      throw error;
    }
  };

  const logout = () => {
    user.value = null;
    token.value = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    delete axios.defaults.headers.common['Authorization'];
  };

  const loadUserFromStorage = () => {
    const storedUser = localStorage.getItem('user');
    const storedToken = localStorage.getItem('token');
    
    if (storedUser && storedToken) {
      user.value = JSON.parse(storedUser);
      token.value = storedToken;
      axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
    }
  };

  return {
    user,
    token,
    isAuthenticated,
    login,
    signup,
    logout,
    loadUserFromStorage,
  };
});

export const useUsersStore = defineStore('users', () => {
  const users = ref([]);
  const loading = ref(false);
  const error = ref(null);

  const fetchUsers = async () => {
    loading.value = true;
    try {
      const response = await axios.get(`${API_URL}/users/`);
      users.value = response.data;
      error.value = null;
    } catch (err) {
      error.value = err.message;
      console.error('Fetch users error:', err);
    } finally {
      loading.value = false;
    }
  };

  const fetchUser = async (id) => {
    try {
      const response = await axios.get(`${API_URL}/users/${id}`);
      return response.data;
    } catch (err) {
      console.error('Fetch user error:', err);
      throw err;
    }
  };

  const createUser = async (userData) => {
    try {
      const response = await axios.post(`${API_URL}/users/`, userData);
      users.value.push(response.data);
      return response.data;
    } catch (err) {
      console.error('Create user error:', err);
      throw err;
    }
  };

  const updateUser = async (id, userData) => {
    try {
      const response = await axios.put(`${API_URL}/users/${id}`, userData);
      const index = users.value.findIndex(u => u.id === id);
      if (index !== -1) {
        users.value[index] = response.data;
      }
      return response.data;
    } catch (err) {
      console.error('Update user error:', err);
      throw err;
    }
  };

  const deleteUser = async (id) => {
    try {
      await axios.delete(`${API_URL}/users/${id}`);
      users.value = users.value.filter(u => u.id !== id);
    } catch (err) {
      console.error('Delete user error:', err);
      throw err;
    }
  };

  return {
    users,
    loading,
    error,
    fetchUsers,
    fetchUser,
    createUser,
    updateUser,
    deleteUser,
  };
});

export const useProjectsStore = defineStore('projects', () => {
  const projects = ref([]);
  const loading = ref(false);
  const error = ref(null);

  const fetchProjects = async () => {
    loading.value = true;
    try {
      const response = await axios.get(`${API_URL}/projects/`);
      projects.value = response.data;
      error.value = null;
    } catch (err) {
      error.value = err.message;
      console.error('Fetch projects error:', err);
    } finally {
      loading.value = false;
    }
  };

  const fetchProject = async (id) => {
    try {
      const response = await axios.get(`${API_URL}/projects/${id}`);
      return response.data;
    } catch (err) {
      console.error('Fetch project error:', err);
      throw err;
    }
  };

  const createProject = async (projectData) => {
    try {
      const response = await axios.post(`${API_URL}/projects/`, projectData);
      projects.value.push(response.data);
      return response.data;
    } catch (err) {
      console.error('Create project error:', err);
      throw err;
    }
  };

  const updateProject = async (id, projectData) => {
    try {
      const response = await axios.put(`${API_URL}/projects/${id}`, projectData);
      const index = projects.value.findIndex(p => p.id === id);
      if (index !== -1) {
        projects.value[index] = response.data;
      }
      return response.data;
    } catch (err) {
      console.error('Update project error:', err);
      throw err;
    }
  };

  const deleteProject = async (id) => {
    try {
      await axios.delete(`${API_URL}/projects/${id}`);
      projects.value = projects.value.filter(p => p.id !== id);
    } catch (err) {
      console.error('Delete project error:', err);
      throw err;
    }
  };

  return {
    projects,
    loading,
    error,
    fetchProjects,
    fetchProject,
    createProject,
    updateProject,
    deleteProject,
  };
});

export const useTasksStore = defineStore('tasks', () => {
  const tasks = ref([]);
  const loading = ref(false);
  const error = ref(null);

  const fetchTasks = async () => {
    loading.value = true;
    try {
      const response = await axios.get(`${API_URL}/tasks/`);
      tasks.value = response.data;
      error.value = null;
    } catch (err) {
      error.value = err.message;
      console.error('Fetch tasks error:', err);
    } finally {
      loading.value = false;
    }
  };

  const fetchTask = async (id) => {
    try {
      const response = await axios.get(`${API_URL}/tasks/${id}`);
      return response.data;
    } catch (err) {
      console.error('Fetch task error:', err);
      throw err;
    }
  };

  const createTask = async (taskData) => {
    try {
      const response = await axios.post(`${API_URL}/tasks/`, taskData);
      tasks.value.push(response.data);
      return response.data;
    } catch (err) {
      console.error('Create task error:', err);
      throw err;
    }
  };

  const updateTask = async (id, taskData) => {
    try {
      const response = await axios.put(`${API_URL}/tasks/${id}`, taskData);
      const index = tasks.value.findIndex(t => t.id === id);
      if (index !== -1) {
        tasks.value[index] = response.data;
      }
      return response.data;
    } catch (err) {
      console.error('Update task error:', err);
      throw err;
    }
  };

  const deleteTask = async (id) => {
    try {
      await axios.delete(`${API_URL}/tasks/${id}`);
      tasks.value = tasks.value.filter(t => t.id !== id);
    } catch (err) {
      console.error('Delete task error:', err);
      throw err;
    }
  };

  return {
    tasks,
    loading,
    error,
    fetchTasks,
    fetchTask,
    createTask,
    updateTask,
    deleteTask,
  };
});

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref(localStorage.getItem('theme') === 'dark');

  const toggleTheme = () => {
    isDark.value = !isDark.value;
    localStorage.setItem('theme', isDark.value ? 'dark' : 'light');
    if (isDark.value) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  const initTheme = () => {
    if (isDark.value) {
      document.documentElement.classList.add('dark');
    }
  };

  return {
    isDark,
    toggleTheme,
    initTheme,
  };
});

export const useLanguageStore = defineStore('language', () => {
  const locale = ref(localStorage.getItem('locale') || 'en');

  const setLocale = (lang) => {
    locale.value = lang;
    localStorage.setItem('locale', lang);
  };

  return {
    locale,
    setLocale,
  };
});
