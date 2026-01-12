// Example of how to use Vue Router

import { createRouter, createWebHistory } from 'vue-router'

// 1. Define route components.
// These can be imported from other files
import MainPage from '../pages/MainPage.vue';
import PostNewItem from '../pages/PostNewItem.vue';
import ProfilePage from '../pages/ProfilePage.vue';
import itemPage from '../pages/itemPage.vue';

let base = (import.meta.env.MODE == 'development') ? import.meta.env.BASE_URL : ''

// 2. Define some routes
// Each route should map to a component.
// We'll talk about nested routes later.
const router = createRouter({
    history: createWebHistory(base),
    routes: [
        { path: '/', name: 'Main Page', component: MainPage },
        { path: "/profile/", name: "profile", component: ProfilePage, meta: { requiresAuth: true } },
        { path: "/newitem/", name: "postItem", component: PostNewItem, meta: { requiresAuth: true } },
        {path: '/item/:id', name: 'itemDetail', component: itemPage},
    ]
})

router.beforeEach(async (to) => {
  if (!to.meta.requiresAuth) return true;

  const res = await fetch("/api/session/", { credentials: "include" });
  const data = (await res.json()) as { isAuthenticated: boolean };

  if (!data.isAuthenticated) {
    window.location.href = `/accounts/login/?next=${encodeURIComponent(to.fullPath)}`;
    return false;
  }

  return true;
});


export default router
