import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: HomeView,
    },
    {
      path: "/weeklycalendar",
      name: "weeklycalendar",
      component: () => import("../views/FullCalendar.vue"),
    },
    {
      path: "/requestslist",
      name: "requestslist",
      component: () => import("../views/RequestsList.vue"),
    },
  ],
});

export default router;
