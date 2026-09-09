import { createRouter, createWebHistory } from 'vue-router';
import InboxView from './views/InboxView.vue';

export default createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/unread' },
    { path: '/unread', component: InboxView, props: { mode: 'unread' } },
    { path: '/starred', component: InboxView, props: { mode: 'starred' } },
    { path: '/all', component: InboxView, props: { mode: 'all' } },
    { path: '/archive', component: () => import('./views/ArchiveView.vue') },
    { path: '/paper/:id', component: () => import('./views/ReaderView.vue'), props: true },
    { path: '/:pathMatch(.*)*', redirect: '/unread' },
  ],
});
