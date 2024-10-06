<template>
  <v-menu>
    <template v-slot:activator="{ props }">
      <v-btn flat variant="outlined" color="grey" text v-bind="props" density="comfortable" icon="mdi-account"></v-btn>
    </template>
    <v-list>
      <v-list-item v-for="user in users" :key="user.staff_id" @click="selectUser(user)">
        <v-list-item-title>
          {{ user.staff_fname }} {{ user.staff_lname }}
          <v-list-item-subtitle>{{ user.dept }}</v-list-item-subtitle>
        </v-list-item-title>
      </v-list-item>
    </v-list>
  </v-menu>
</template>

<script>
import { useMainStore } from '@/store.js';

export default {
  data() {
    return {
      selectedUser: null,
      users: [
        {
          staff_id: 150488,
          staff_fname: "Jacob",
          staff_lname: "Tan",
          dept: "Engineering",
          position: "Call Centre",
          country: "Singapore",
          email: "Jacob.Tan@allinone.com.sg",
          reporting_manager: 151408,
          role: 2,
        },
        {
          staff_id: 130002,
          staff_fname: "Jack",
          staff_lname: "Sim",
          dept: "CEO",
          position: "MD",
          country: "Singapore",
          email: "jack.sim@allinone.com.sg",
          reporting_manager: 130002,
          role: 1,
        },
        {
          "staff_id": 140008,
          "staff_fname": "Jaclyn",
          "staff_lname": "Lee",
          "dept": "Sales",
          "position": "Sales Manager",
          "country": "Singapore",
          "email": "Jaclyn.Lee@allinone.com.sg",
          "reporting_manager": 140001,
          "role": 3
        }
      ],
    }
  },
  methods: {
    selectUser(user) {
      const userStore = useMainStore();
      userStore.updateUser(user);
    }
  }
}
</script>