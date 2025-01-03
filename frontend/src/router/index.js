import { createRouter, createWebHistory } from "vue-router";
import OwnSchedule from "../views/OwnSchedule.vue";
import TeamSchedule from "@/views/OrgTeamSchedule.vue";
import { useMainStore } from "@/store";

const router = createRouter({
  history: createWebHistory(import.meta.env.VITE_BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: OwnSchedule,
    },
    {
      path: "/requestslist",
      name: "requestslist",
      component: () => import("../views/OwnRequests.vue"),
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
  "/staffweeklyschedule": [2],
  "/viewstaffrequests": [1, 3],
  "/team_schedule/director": [1],
  "/team_schedule/organisation": [1],
  "/team_schedule/manager": [3],
};

router.beforeEach(async (to, from, next) => {
  const store = useMainStore();
  const userRole = store.user.role;
  const userPosition = store.user.position;

  // Check if the route is restricted and if the user has the required role
  if (allowedRoles[to.path]) {
    if (allowedRoles[to.path].includes(userRole)) {
      // Additional checks for role 1
      if (userRole === 1) {
        if (
          to.path === "/team_schedule/organisation" &&
          (userPosition === "HR Team" || userPosition === "MD")
        ) {
          next(); // User has access to /team_schedule/organisation
        } else if (
          to.path === "/team_schedule/director" &&
          userPosition !== "HR Team" &&
          userPosition !== "MD"
        ) {
          next(); // User has access to /team_schedule/director
        } else if (
          to.path !== "/team_schedule/organisation" &&
          to.path !== "/team_schedule/director"
        ) {
          next(); // User has access to other routes
        } else {
          next("/"); // User does not have access, redirect to homepage
        }
      } else {
        next(); // User has access, proceed to the route
      }
    } else {
      next("/"); // User does not have access, redirect to homepage
    }
  } else {
    next(); // Route is not restricted, proceed to the route
  }
});

export default router;
