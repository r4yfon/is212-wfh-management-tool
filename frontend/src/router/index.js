import { createRouter, createWebHistory } from "vue-router";
import WeeklyCalendar from "../views/FullCalendar.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: WeeklyCalendar,
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
