<script setup>
import { RouterLink } from "vue-router";
import {
  VTextField,
  VBtn,
  VDialog,
  VCard,
  VCardText,
  VCardActions,
  VSpacer,
  VProgressCircular,
} from "vuetify/components";
</script>

<template>
  <header class="container-fluid position-sticky bg-info-subtle py-1 py-md-3 z-3">
    <!-- <div class="wrapper"> -->
    <v-col cols="12" class="container">
      <v-row align="center" justify="end" class="header-buttons">
        <!-- hambuger menu for mobile -->
        <v-btn class="d-md-none" icon="mdi-menu" variant="plain" @click="toggleMenu"></v-btn>

        <RouterLink to="/">
          <img src="@/assets/logo.svg" alt="Vue Logo" height="32" />
        </RouterLink>

        <!-- buttons for desktop -->
        <div class="d-none d-md-flex">
          <v-btn variant="plain" href="/weeklycalendar" class="d-none d-md-block align-content-center">View
            Schedule</v-btn>
          <v-btn variant="plain" href="/requestslist" class="d-none d-md-block align-content-center">View
            Requests</v-btn>
          <v-btn @click="dialog = true" variant="plain">Apply to WFH</v-btn>
        </div>

        <v-dialog v-model="dialog" max-width="500px">
          <v-card>
            <v-card-title>Apply to WFH</v-card-title>
            <v-card-text>
              <v-form>
                <!-- Event Title -->
                <VTextField v-model="newEvent.staffId" label="Staff ID" required></VTextField>

                <!-- Toggle Buttons for One Day and Recurring -->
                <v-btn-toggle v-model="requestType" mandatory class="mb-4">
                  <v-btn value="one-time" color="primary">One Day</v-btn>
                  <v-btn value="recurring" color="primary">Recurring</v-btn>
                </v-btn-toggle>

                <!-- One Day Request -->
                <v-text-field v-if="requestType === 'one-time'" v-model="newEvent.date" label="Date of Request"
                  type="date" required></v-text-field>

                <!-- Recurring Request Fields -->
                <div v-if="requestType === 'recurring'">
                  <v-text-field v-model="newEvent.date" label="Start Date" type="date" @change="updateRecurrenceDay"
                    required></v-text-field>
                  <v-text-field v-model="newEvent.endDate" label="End Date" type="date" required></v-text-field>

                  <p v-if="newEvent.date != '' && newEvent.endDate != ''">
                    This event will repeat every {{ newEvent.dayOfWeek }} from
                    {{ newEvent.date }} to
                    {{ newEvent.endDate }}
                  </p>
                </div>

                <v-radio-group v-model="newEvent.shift" label="Timing for Work From Home" row required>
                  <v-radio label="AM (09:00-13:00)" value="AM"></v-radio>
                  <v-radio label="PM (14:00-18:00)" value="PM"></v-radio>
                  <v-radio label="FULL (09:00-18:00)" value="Full"></v-radio>
                </v-radio-group>

                <v-text-field v-model="newEvent.reason" label="Reason for Request" required></v-text-field>
              </v-form>
            </v-card-text>
            <v-card-actions>
              <v-btn color="green-darken-1" @click="confirmApply">
                <span v-if="loading">
                  <v-progress-circular indeterminate :size="15" :width="2" color="primary"
                    class="me-1"></v-progress-circular>
                </span>
                Apply
              </v-btn>
              <v-btn color="red-darken-1" @click="dialog = false">Cancel</v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

        <v-spacer></v-spacer>


        <!--  for switching users -->
        <v-menu>
          <template v-slot:activator="{ props }">
            <v-btn flat variant="outlined" color="grey" text v-bind="props" density="comfortable"
              icon="mdi-account"></v-btn>
          </template>
          <v-list>
            <v-list-item v-for="user in users" :key="user" @click="selectUser(user)">
              <v-list-item-title>{{ user }}</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>

        <!-- dropdown menu for mobile -->
        <div class="d-md-none w-100" id="mobile-menu" v-show="isMenuOpen">
          <div class="d-flex flex-column">
            <v-btn class="justify-content-start" href="/requestslist" @click="toggleMenu" variant="plain">View
              Requests</v-btn>
            <v-btn class="justify-content-start" href="/weeklycalendar" @click="toggleMenu" variant="plain">View
              Schedule</v-btn>
            <v-btn class="justify-content-start" @click="dialog = true" variant="plain">Apply to WFH</v-btn>
          </div>
        </div>
      </v-row>
    </v-col>
  </header>
</template>

<script>
export default {
  data() {
    return {
      users: ["HR", "Manager", "Employee"],
      dialog: false,
      loading: false,
      requestType: "one-time",
      isMenuOpen: false,
      newEvent: {
        staffId: "",
        date: "",
        endDate: "",
        dayOfWeek: "",
        shift: "",
        reason: "",
      },
    }
  },
  methods: {
    toggleMenu() {
      this.isMenuOpen = !this.isMenuOpen;
    },
    updateRecurrenceDay() {
      const date = new Date(this.newEvent.date);
      this.newEvent.dayOfWeek = date.toLocaleString("en-US", { weekday: "long" });
    },
    convertRecurringToObject(startDate, endDate, shift) {
      const dates = {};
      const startDateObj = new Date(startDate);
      const endDateObj = new Date(endDate);
      let currentDate = new Date(startDateObj);
      while (currentDate <= endDateObj) {
        dates[currentDate.toISOString().split("T")[0]] = shift;
        currentDate.setDate(currentDate.getDate() + 7);
      }
      return dates;
    },
    confirmApply() {
      this.loading = true;
      console.log("newEvent", this.newEvent);
      if (
        this.requestType === "one-time" &&
        this.newEvent.staffId &&
        this.newEvent.date &&
        this.newEvent.shift &&
        this.newEvent.reason
      ) {
        fetch("http://localhost:5001/request/create", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            staff_id: this.newEvent.staffId,
            request_date: new Date().toISOString().split("T")[0],
            request_dates: {
              [this.newEvent.date]: this.newEvent.shift,
            },
            apply_reason: this.newEvent.reason,
          }),
        })
          .then((response) => response.json())
          .then((data) => {
            console.log("Success:", data);
          })
          .catch((error) => {
            console.error("Error:", error);
          })
          .finally(() => {
            this.loading = false;
            setTimeout(200);
            this.dialog = false;
          });
      } else if (
        this.requestType === "recurring" &&
        this.newEvent.staffId &&
        this.newEvent.date &&
        this.newEvent.endDate &&
        this.newEvent.shift &&
        this.newEvent.reason
      ) {
        const recurringDates = this.convertRecurringToObject(
          this.newEvent.date,
          this.newEvent.endDate,
          this.newEvent.shift,
        );
        fetch("http://localhost:5001/request/create", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            staff_id: this.newEvent.staffId,
            request_date: new Date().toISOString().split("T")[0],
            request_dates: recurringDates,
            apply_reason: this.newEvent.reason,
          }),
        })
          .then((response) => response.json())
          .then((data) => {
            console.log("Success:", data);
          })
          .catch((error) => {
            console.error("Error:", error);
          })
          .finally(() => {
            this.loading = false;
            setTimeout(200);
            this.dialog = false;
          });
      } else {
        alert("Please fill in all required fields and try again.");
        this.loading = false;
      }
      this.newEvent.staffId = "";
      this.newEvent.date = "";
      this.newEvent.endDate = "";
      this.newEvent.shift = "";
      this.newEvent.reason = "";
      this.newEvent.requestType = "one-time";
      this.newEvent.recurrence = "";
    }
  }
}
</script>