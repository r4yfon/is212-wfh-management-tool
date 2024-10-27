<script setup>
import { useMainStore } from '@/store.js';
const userStore = useMainStore();
</script>

<template>
  <v-menu>
    <template v-slot:activator="{ props }">
      <v-btn flat variant="outlined" color="black" text v-bind="props" prepend-icon="mdi-account">
        {{ userStore.user.staff_fname }} {{ userStore.user.staff_lname }}
      </v-btn>
    </template>
    <v-list>
      <v-list-item v-for="user in users" :key="user.staff_id" @click="selectUser(user)">
        <v-list-item-title>{{ user.staff_fname }} {{ user.staff_lname }}</v-list-item-title>
        <v-list-item-subtitle>Department: {{ user.department }}</v-list-item-subtitle>
        <v-list-item-subtitle>Position: {{ user.position }}</v-list-item-subtitle>
      </v-list-item>
    </v-list>
  </v-menu>
</template>

<script>
export default {
  data() {
    return {
      users: [
        // {
        //   staff_id: 150488,
        //   staff_fname: "Jacob",
        //   staff_lname: "Tan",
        //   department: "Engineering",
        //   position: "Call Centre",
        //   country: "Singapore",
        //   email: "Jacob.Tan@allinone.com.sg",
        //   reporting_manager: 151408,
        //   role: 2,
        // },
        {
          staff_id: 140937,
          staff_fname: "Sirirat",
          staff_lname: "Chaiyaporn",
          department: "Sales",
          position: "Account Manager",
          country: "Hong Kong",
          email: "Sirirat.Chaiyaporn@allinone.com.hk",
          reporting_manager: 140879,
          role: 2
        },
        {
          staff_id: 130002,
          staff_fname: "Jack",
          staff_lname: "Sim",
          department: "CEO",
          position: "MD",
          country: "Singapore",
          email: "jack.sim@allinone.com.sg",
          reporting_manager: 130002,
          role: 1,
        },
        // {
        //   staff_id: 151408,
        //   staff_fname: "Philip",
        //   staff_lname: "Lee",
        //   department: "Engineering",
        //   position: "Director",
        //   country: "Singapore",
        //   email: "Philip.Lee@allinone.com.sg",
        //   reporting_manager: 130002,
        //   role: 1
        // },
        {
          staff_id: 140879,
          staff_fname: "Siti",
          staff_lname: "Abdullah",
          department: "Sales",
          position: "Sales Manager",
          country: "Singapore",
          email: "Siti.Abdullah@allinone.com.sg",
          reporting_manager: 140001,
          role: 3
        },

      ],
    }
  },
  mounted() {
    // this.selected_user = userStore.user;
  },
  methods: {
    selectUser(user) {
      const userStore = useMainStore();
      userStore.updateUser(user);
    }
  }
}
</script>