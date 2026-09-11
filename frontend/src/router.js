import { createRouter, createWebHistory } from 'vue-router';
import InboxView from './views/InboxView.vue';

export default createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/all' },
    { path: '/unread', component: InboxView, props: { mode: 'unread' } },
    { path: '/starred', component: InboxView, props: { mode: 'starred' } },
    { path: '/deleted', component: InboxView, props: { mode: 'deleted' } },
    { path: '/folder/:id', component: InboxView, props: (r) => ({ mode: 'folder', folderId: r.params.id }) },
    { path: '/all', component: InboxView, props: { mode: 'all' } },
    { path: '/archive', component: () => import('./views/ArchiveView.vue') },
    { path: '/about', component: () => import('./views/AboutView.vue') },
    { path: '/paper/:id', component: () => import('./views/ReaderView.vue'), props: true },
    { path: '/:pathMatch(.*)*', redirect: '/all' },
  ],
});
