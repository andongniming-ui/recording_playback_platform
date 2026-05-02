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
        { path: 'applications', component: () => import('@/views/applications/index.vue'), meta: { menuKey: 'applications' } },
        { path: 'applications/:id', component: () => import('@/views/applications/detail.vue'), meta: { menuKey: 'applications' } },
        { path: 'recording', component: () => import('@/views/recording/index.vue'), meta: { menuKey: 'recording' } },
        { path: 'recording/sessions/:id', component: () => import('@/views/recording/session-detail.vue'), meta: { menuKey: 'recording' } },
        { path: 'recording/recordings/:id', component: () => import('@/views/recording/recording-detail.vue'), meta: { menuKey: 'recording' } },
        { path: 'testcases', component: () => import('@/views/testcases/index.vue'), meta: { menuKey: 'testcases' } },
        { path: 'testcases/:id', component: () => import('@/views/testcases/detail.vue'), meta: { menuKey: 'testcases' } },
        { path: 'replay', component: () => import('@/views/replay/index.vue'), meta: { menuKey: 'replay' } },
        { path: 'replay/history', component: () => import('@/views/replay/history.vue'), meta: { menuKey: 'replay-history' } },
        { path: 'results', component: () => import('@/views/results/index.vue'), meta: { menuKey: 'results' } },
        { path: 'results/:jobId', component: () => import('@/views/results/job-detail.vue'), meta: { menuKey: 'results' } },
        { path: 'dashboard', component: () => import('@/views/dashboard/index.vue'), meta: { menuKey: 'dashboard' } },
        { path: 'suites', component: () => import('@/views/suites/index.vue'), meta: { menuKey: 'suites' } },
        { path: 'suites/:id', component: () => import('@/views/suites/detail.vue'), meta: { menuKey: 'suites' } },
        { path: 'schedule', component: () => import('@/views/schedule/index.vue'), meta: { menuKey: 'schedule' } },
        { path: 'compare', component: () => import('@/views/compare/index.vue'), meta: { menuKey: 'compare' } },
        { path: 'settings', component: () => import('@/views/settings/index.vue'), meta: { menuKey: 'settings' } },
        { path: 'ci', component: () => import('@/views/ci/index.vue'), meta: { roles: ['admin'], menuKey: 'ci' } },
        { path: 'users', component: () => import('@/views/users/index.vue'), meta: { roles: ['admin'], menuKey: 'users' } },
      ],
    },
    {
      path: '/login',
      component: () => import('@/views/auth/Login.vue'),
    },
    {
      path: '/:pathMatch(.*)*',
      component: () => import('@/views/errors/NotFound.vue'),
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
    return '/applications'
  }

  return true
})

export default router
