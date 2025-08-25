import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import GeneratorView from "@/views/GeneratorView.vue";
import NotFoundView from "@/views/NotFoundView.vue";
import AboutView from "@/views/AboutView.vue";


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { title: 'Home'}
    },
    {
      path: '/generator',
      component: GeneratorView,
      meta: {title: 'Generator'}
    },
    {
      path: '/about',
      component : AboutView,
      meta: {title: 'About'}
    },
     // Catch-all (MUSS am Ende stehen)
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFoundView',
      component: NotFoundView,
      meta: { title: '404' } },
  ],
})

export default router
