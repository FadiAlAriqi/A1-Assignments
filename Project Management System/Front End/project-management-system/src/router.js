import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from './store';

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('./pages/Login.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/signup',
    name: 'Signup',
    component: () => import('./pages/Signup.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('./pages/Dashboard.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: 'users',
        name: 'Users',
        component: () => import('./pages/Users/UsersList.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'users/create',
        name: 'CreateUser',
        component: () => import('./pages/Users/UserForm.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'users/:id',
        name: 'ViewUser',
        component: () => import('./pages/Users/UserView.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'users/:id/edit',
        name: 'EditUser',
        component: () => import('./pages/Users/UserForm.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'projects',
        name: 'Projects',
        component: () => import('./pages/Projects/ProjectsList.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'projects/create',
        name: 'CreateProject',
        component: () => import('./pages/Projects/ProjectForm.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'projects/:id',
        name: 'ViewProject',
        component: () => import('./pages/Projects/ProjectView.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'projects/:id/edit',
        name: 'EditProject',
        component: () => import('./pages/Projects/ProjectForm.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'tasks',
        name: 'Tasks',
        component: () => import('./pages/Tasks/TasksList.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'tasks/create',
        name: 'CreateTask',
        component: () => import('./pages/Tasks/TaskForm.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'tasks/:id',
        name: 'ViewTask',
        component: () => import('./pages/Tasks/TaskView.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'tasks/:id/edit',
        name: 'EditTask',
        component: () => import('./pages/Tasks/TaskForm.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('./pages/Profile.vue'),
        meta: { requiresAuth: true },
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();

  if (!authStore.isAuthenticated) {
    const storedToken = localStorage.getItem('token');
    if (storedToken) authStore.token = storedToken;
  }

  const requiresAuth = to.meta.requiresAuth;

  if (requiresAuth && !authStore.isAuthenticated) {
    next('/login');
  } else if (!requiresAuth && authStore.isAuthenticated && (to.path === '/login' || to.path === '/signup')) {
    next('/');
  } else {
    next();
  }
});

export default router;
