import { createRouter, createWebHistory, createWebHashHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

// Usar hash history para GitHub Pages (evita 404 em refresh)
const isGitHubPages = import.meta.env.VITE_GITHUB_PAGES === 'true'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/generate/:sessionId',
    name: 'Generate',
    component: () => import('../views/Generate.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/review/:sessionId',
    name: 'Review',
    component: () => import('../views/Review.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: isGitHubPages ? createWebHashHistory() : createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router
