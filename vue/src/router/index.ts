import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/login",
      name: "login",
      component: () => import("../pages/LoginView.vue"),
    },
    {
      path: "/register",
      name: "register",
      component: () => import("../pages/RegisterView.vue"),
    },
    // 添加主布局路由
    {
      path: "/",
      component: () => import("../layouts/home.vue"),
      meta: { requiresAuth: true },
      redirect: 'chat',
      children: [
        {
          path: "chat",
          name: "chat",
          component: () => import("../pages/ChatView.vue"),
        },
        {
          path: "contacts",
          name: "contacts",
          component: () => import("../pages/ContactsView.vue"),
        },
        {
          path: "settings",
          name: "settings",
          component: () => import("../pages/SettingsView.vue"),
        },
      ],
    },
  ],
});

// 路由守卫 - 检查认证状态
router.beforeEach((to, _from, next) => {
  const isAuthenticated = !!localStorage.getItem("accessToken");

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: "login" });
  } else {
    next();
  }
});

export default router;
