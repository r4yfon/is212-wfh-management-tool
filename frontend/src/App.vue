<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { VTextField, VDatePicker, VBtn, VDialog, VCard, VCardTitle, VCardText, VCardActions, VSpacer } from 'vuetify/components'; 
import { ref, reactive } from 'vue';

// State variables
const dialog = ref(false);
const newEvent = reactive({
  staffId: '',
  date: '',
  time: '',
  reason: '',
});
const events = ref([]);

const confirmApply = () => {
  if (newEvent.staffId && newEvent.date && newEvent.time && newEvent.reason) {
    const event = {
      staffId: newEvent.staffId,
      date: newEvent.date,
      time: newEvent.time,
      reason: newEvent.reason,
      color: 'blue',
    };

    events.value.push(event); // Add new event to the calendar

    // Clear the form fields
    Object.assign(newEvent, {
      staffId: '',
      date: '',
      time: '',
      reason: '',
    });

    dialog.value = false
  }
};
</script>

<template>
  <header>
    <!-- <div class="wrapper"> -->
    <v-col cols="12">
      <v-row align="center" justify="end" class="header-buttons">
      <h1 class="title">WFH Management System</h1>
      <v-spacer></v-spacer>

      <v-dialog v-model="dialog" max-width="400px">
        <template v-slot:activator="{ props: activatorProps }">
          <v-btn
            v-bind="activatorProps"
            color="primary"
            text="Apply"
            variant="flat"
          ></v-btn>
        </template>

        <v-card title="Apply for Work From Home">
          <v-card-text>
            <v-form>
              <!-- Event Title -->
              <VTextField v-model="newEvent.staffId" label="Staff ID" required></VTextField>

              <!-- Event Date -->
              <VTextField v-model="newEvent.date" label="Date of Request" type="date" required></VTextField>

              <v-radio-group
                v-model="newEvent.time"
                label="Timing for Work From Home"
                row
                required
              >
                <v-radio label="AM (09:00-13:00)" value="AM"></v-radio>
                <v-radio label="PM (14:00-18:00)" value="PM"></v-radio>
                <v-radio label="FULL (09:00-18:00)" value="Full"></v-radio>
              </v-radio-group>

              <v-text-field v-model="newEvent.reason" label="Reason for Request" required></v-text-field>

            </v-form>
          </v-card-text>

          <v-card-actions>
            <v-spacer></v-spacer>

            <v-btn color="green darken-1" text @click="confirmApply">
              Apply
            </v-btn>
            <v-btn color="red darken-1" text @click="dialog = false">
              Cancel
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <v-menu>
        <template v-slot:activator="{ props }">
          <v-btn icon="mdi-dots-vertical" variant="text" v-bind="props"></v-btn>
        </template>
        <v-list>
          <v-list-item>
            <RouterLink to= "/weeklycalendar">Own Weekly Schedule</RouterLink>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-row>
    </v-col>
    
  </header>

  <div class = "content">
    <RouterView />
  </div>

</template>

<style scoped>
header {
  max-height: 100vh;
  position: fixed; 
  top: 0; 
  left: 0;
  right: 0;
  height: 50px;
  background-color: rgb(102, 136, 247); 
  z-index: 1000; /* Ensures the header is always on top of other elements */
  width: 100%;
  display: flex;
  justify-content: space-between; /* Space between title and nav */
  align-items: center;
  padding-left: 10px;
}

.header-buttons {
  width: 100%;
  justify-content: flex-end; /* Align buttons to the far right */
}

.content {
  padding-top: 30px; 
  padding-bottom: 30px;
  height: calc(100vh - 50px); 
  width: 100%; /* Ensure content spans full width */
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

nav {
  width: 100%;
  font-size: 12px;
  text-align: center;
  margin-top: 2rem;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
  border: 0;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }

  nav {
    text-align: left;
    margin-left: -1rem;
    font-size: 1rem;

    padding: 1rem 0;
    margin-top: 1rem;
  }
}
</style>
