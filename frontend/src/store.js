import { defineStore } from "pinia";

export const useMainStore = defineStore("main", {
  state: () => ({
    user: {
      staff_id: 140937,
      staff_fname: "Sirirat",
      staff_lname: "Chaiyaporn",
      department: "Sales",
      position: "Account Manager",
      country: "Hong Kong",
      email: "Sirirat.Chaiyaporn@allinone.com.hk",
      reporting_manager: 140879,
      role: 2,
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
