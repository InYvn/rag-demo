import Vue from 'vue'
import VueRouter from 'vue-router'
import HomeView from '../views/HomeView.vue'
const KBList = () => import('../views/KBList.vue')
const KBDetail = () => import('../views/KBDetail.vue')
const Chat = () => import('../views/Chat.vue')

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  { path: '/kb', name: 'KBList', component: KBList },
  { path: '/kb/:id', name: 'KBDetail', component: KBDetail }, 
  { path: '/chat', name: 'Chat', component: Chat },
  {
    path: '/about',
    name: 'about',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/AboutView.vue')
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
