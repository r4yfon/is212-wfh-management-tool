import { createRouter, createWebHistory } from "vue-router";
import WeeklyCalendar from "../views/FullCalendar.vue";
import HRViewSchedule from "@/components/OrgSchedule.vue";
import { useMainStore } from "@/store";

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
    {
      path: "/staffweeklyschedule",
      name: "staffweeklyschedule",
      component: () => import("../views/StaffViewTeamSchedule.vue"),
    },
  ],
});

const allowedRoles = {
  "/weeklycalendar": [1, 2], // Example: Roles 1 and 2 can access /weeklycalendar
  "/staffweeklyschedule": [1, 2], // Example: Roles 1 and 2 can access /staffweeklyschedule
  "/requestslist": [1, 2], // Example: Only role 1 can access /requestslist
  "/viewstaffrequests": [1], // Example: Roles 1, 2, and 3 can access /viewstaffrequests
  "/org_schedule": [1], // Example: Only role 1 can access /org_schedule
};

router.beforeEach((to, from, next) => {
  const store = useMainStore();
  const userRole = store.user.role;

  // Check if the route is restricted and if the user has the required role
  if (allowedRoles[to.path]) {
    if (allowedRoles[to.path].includes(userRole)) {
      next(); // User has access, proceed to the route
    } else {
      next("/"); // User does not have access, redirect to homepage
    }
  } else {
    next(); // Route is not restricted, proceed to the route
  }
});

export default router;
