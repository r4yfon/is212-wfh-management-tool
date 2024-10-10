import { defineStore } from "pinia";

export const useMainStore = defineStore("main", {
  state: () => ({
    user: {
      staff_id: 150488,
      staff_fname: "Jacob",
      staff_lname: "Tan",
      dept: "Engineering",
      position: "Call Centre",
      country: "Singapore",
      email: "Jacob.Tan@allinone.com.sg",
      reporting_manager: "151408",
      role: 2,
    },
  }),
  actions: {
    updateUser(user) {
      this.user = user;
    },
  }
});