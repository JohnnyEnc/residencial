import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/login' },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { guest: true },
    },
    {
      path: '/admin',
      component: () => import('../layouts/AdminLayout.vue'),
      meta: { roles: ['admin'] },
      children: [
        { path: '', name: 'admin-dashboard', component: () => import('../views/admin/DashboardView.vue') },
        { path: 'units', name: 'admin-units', component: () => import('../views/admin/UnitsView.vue') },
        { path: 'users', name: 'admin-users', component: () => import('../views/admin/UsersView.vue') },
        { path: 'directory', name: 'admin-directory', component: () => import('../views/admin/DirectoryView.vue') },
        { path: 'payments', name: 'admin-payments', component: () => import('../views/admin/PaymentsView.vue') },
        { path: 'reports', name: 'admin-reports', component: () => import('../views/admin/ReportsView.vue') },
        { path: 'announcements', name: 'admin-announcements', component: () => import('../views/admin/AnnouncementsView.vue') },
      ],
    },
    {
      path: '/app',
      component: () => import('../layouts/MobileLayout.vue'),
      meta: { roles: ['resident'] },
      children: [
        { path: '', name: 'resident-home', component: () => import('../views/resident/HomeView.vue') },
        { path: 'directory', name: 'resident-directory', component: () => import('../views/resident/DirectoryView.vue') },
        { path: 'payments', name: 'resident-payments', component: () => import('../views/resident/PaymentsView.vue') },
        { path: 'reports', name: 'resident-reports', component: () => import('../views/resident/ReportsView.vue') },
        { path: 'reports/new', name: 'resident-report-new', component: () => import('../views/resident/NewReportView.vue') },
        { path: 'profile', name: 'resident-profile', component: () => import('../views/shared/ProfileView.vue') },
      ],
    },
    {
      path: '/staff',
      component: () => import('../layouts/MobileLayout.vue'),
      meta: { roles: ['staff'] },
      children: [
        { path: '', name: 'staff-home', component: () => import('../views/staff/ReportsView.vue') },
        { path: 'reports/:id', name: 'staff-report', component: () => import('../views/staff/ReportDetailView.vue') },
        { path: 'profile', name: 'staff-profile', component: () => import('../views/shared/ProfileView.vue') },
      ],
    },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (auth.token && !auth.user) {
    try {
      await auth.fetchMe()
    } catch {
      auth.logout()
    }
  }

  if (to.meta.guest && auth.isAuthenticated) {
    return auth.homePath()
  }

  const roles = to.meta.roles as string[] | undefined
  if (roles) {
    if (!auth.isAuthenticated) return '/login'
    if (!roles.includes(auth.role!)) return auth.homePath()
  }
})

export default router
