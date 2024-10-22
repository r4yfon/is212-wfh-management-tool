import { createRouter, createWebHistory } from "vue-router";
import WeeklyCalendar from "../views/FullCalendar.vue";
import HRViewSchedule from "@/components/OrgSchedule.vue";

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
      component: WeeklyCalendar,
    },
    {
      path: "/requestslist",
      name: "requestslist",
      component: () => import("../views/RequestsList.vue"),
    },
    {
      path: "/viewstaffrequests",
      name: "viewstaffrequests",
      component: () => import("../views/ViewStaffRequests.vue"),
    },
    {
      path: "/org_schedule",
      component: HRViewSchedule,
    },
  ],
});

export default router;
