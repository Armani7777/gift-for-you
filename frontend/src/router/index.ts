import { createRouter, createWebHistory } from 'vue-router'
import AnswersView from '@/views/AnswersView.vue'
import CreateInvitationView from '@/views/CreateInvitationView.vue'
import DemoView from '@/views/DemoView.vue'
import HomeView from '@/views/HomeView.vue'
import InvitationView from '@/views/InvitationView.vue'
import ManageInvitationView from '@/views/ManageInvitationView.vue'
import NotFoundView from '@/views/NotFoundView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView, meta: { title: "Create a Date Invitation They'll Remember" } },
    { path: '/create', name: 'create', component: CreateInvitationView, meta: { title: 'Create invitation', robots: 'noindex' } },
    { path: '/demo', name: 'demo', component: DemoView, meta: { title: 'Demo invitation' } },
    { path: '/answers', name: 'answers', component: AnswersView, meta: { title: 'Her answers', robots: 'noindex' } },
    { path: '/i/:token', name: 'invite', component: InvitationView, meta: { title: 'A date invitation', robots: 'noindex' } },
    {
      path: '/manage/:token/:managementToken',
      name: 'manage',
      component: ManageInvitationView,
      meta: { title: 'Invitation status', robots: 'noindex' },
    },
    { path: '/:pathMatch(.*)*', name: 'not-found', component: NotFoundView, meta: { title: 'Not found', robots: 'noindex' } },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

router.afterEach((to) => {
  const title = String(to.meta.title || "Create a Date Invitation They'll Remember")
  document.title = title
  let robots = document.querySelector('meta[name="robots"]')
  if (!robots) {
    robots = document.createElement('meta')
    robots.setAttribute('name', 'robots')
    document.head.appendChild(robots)
  }
  robots.setAttribute('content', String(to.meta.robots || 'index,follow'))
})

export default router
