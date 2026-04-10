import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: () => import('@/layouts/MainLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: '/dashboard' },
        { path: 'dashboard', component: () => import('@/views/dashboard/index.vue') },
        { path: 'applications', component: () => import('@/views/applications/index.vue') },
        { path: 'recording', component: () => import('@/views/recording/index.vue') },
        { path: 'testcases', component: () => import('@/views/testcases/index.vue') },
        { path: 'replay', component: () => import('@/views/replay/index.vue') },
        { path: 'compare', component: () => import('@/views/compare/index.vue') },
        { path: 'results', component: () => import('@/views/results/index.vue') },
        { path: 'schedule', component: () => import('@/views/schedule/index.vue') },
        { path: 'suites', component: () => import('@/views/suites/index.vue') },
        { path: 'ci', component: () => import('@/views/ci/index.vue'), meta: { roles: ['admin'] } },
        { path: 'users', component: () => import('@/views/users/index.vue'), meta: { roles: ['admin'] } },
        { path: 'settings', component: () => import('@/views/settings/index.vue') },
      ],
    },
    {
      path: '/login',
      component: () => import('@/views/auth/Login.vue'),
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/dashboard',
    },
  ],
})

router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role') || 'viewer'
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)
  const allowedRoles = to.matched.flatMap((record) => {
    const roles = record.meta.roles
    return Array.isArray(roles) ? roles : []
  })

  if (requiresAuth && !token) {
    return { path: '/login', query: to.fullPath !== '/' ? { redirect: to.fullPath } : undefined }
  }

  if (to.path === '/login' && token) {
    return '/dashboard'
  }

  if (allowedRoles.length > 0 && !allowedRoles.includes(role)) {
    return '/dashboard'
  }

  return true
})

export default router
