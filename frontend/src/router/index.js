import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/dashboard',
    component: () => import('../views/Layout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
      { path: 'clusters', name: 'Clusters', component: () => import('../views/cluster/ClusterList.vue') },
      { path: 'clusters/:id', name: 'ClusterDetail', component: () => import('../views/cluster/ClusterDetail.vue') },
      { path: 'workloads', name: 'Workloads', component: () => import('../views/workload/WorkloadList.vue') },
      { path: 'services', name: 'Services', component: () => import('../views/network/ServiceList.vue') },
      { path: 'nodes', name: 'Nodes', component: () => import('../views/node/NodeList.vue') },
      { path: 'audit', name: 'AuditLogs', component: () => import('../views/audit/AuditLog.vue') },
      { path: 'users', name: 'Users', component: () => import('../views/user/UserList.vue') },
    ],
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.matched.some((r) => r.meta.requiresAuth) && !token) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router