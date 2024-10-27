import { createRouter, createWebHistory } from "vue-router";
import WeeklyCalendar from "../views/FullCalendar.vue";
import TeamSchedule from "@/views/TeamSchedule.vue";
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
      path: "/staffweeklyschedule",
      name: "staffweeklyschedule",
      component: () => import("../views/StaffViewTeamSchedule.vue"),
    },
    {
      path: "/team_schedule/:role",
      name: "teamschedule",
      component: TeamSchedule,
      props: true,
    },
  ],
});

const allowedRoles = {
  "/weeklycalendar": [1, 2, 3],
  "/staffweeklyschedule": [1, 2, 3],
  "/requestslist": [1, 2, 3],
  "/viewstaffrequests": [1, 3],
  "/org_schedule": [1],
  "/team_schedule/director": [1],
  "/team_schedule/manager": [3],
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
