import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: () => import('@/layouts/MainLayout.vue'),
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
        { path: 'ci', component: () => import('@/views/ci/index.vue') },
        { path: 'users', component: () => import('@/views/users/index.vue') },
        { path: 'settings', component: () => import('@/views/settings/index.vue') },
      ],
    },
    {
      path: '/login',
      component: () => import('@/views/auth/Login.vue'),
    },
  ],
})

export default router
