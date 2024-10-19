import { defineStore } from "pinia";

export const useMainStore = defineStore("main", {
  state: () => ({
    user: {
      staff_id: 151408,
      staff_fname: "Philip",
      staff_lname: "Lee",
      department: "Engineering",
      position: "Director",
      country: "Singapore",
      email: "Philip.Lee@allinone.com.sg",
      reporting_manager: 130002,
      role: 1
    },
    paths: {
      employee: "http://localhost:5000/employee",
      request: "http://localhost:5001/request",
      request_dates: "http://localhost:5002/request_dates",
      status_log: "http://localhost:5003/status_log",
      view_schedule: "http://localhost:5100",
      view_requests: "http://localhost:5101",
      reject_requests: "http://localhost:5102/reject_request",
    },
  }),
  persist: {
    storage: sessionStorage,
    pick: ["user"],
  },
  actions: {
    updateUser(user) {
      this.user = user;
      location.reload();
    },
  },
});
