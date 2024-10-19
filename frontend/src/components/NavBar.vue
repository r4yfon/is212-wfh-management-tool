<script setup>
import { RouterLink } from "vue-router";
import UserSelection from "./UserSelection.vue";
import { is_within_word_count, two_months_before, three_months_after } from "@/inputValidation";
import { useMainStore } from "@/store";
const userStore = useMainStore();
</script>

<template>
  <header class="container-fluid position-sticky bg-info-subtle py-1 py-md-3 z-3">
    <!-- <div class="wrapper"> -->
    <v-col cols="12">
      <v-row align="center" justify="end" class="header-buttons">
        <!-- hambuger menu for mobile -->
        <v-btn class="d-md-none" icon="mdi-menu" variant="plain" @click="toggleMenu"></v-btn>

        <RouterLink to="/">
          <img src="@/assets/logo.svg" alt="Vue Logo" height="32" />
        </RouterLink>

        <!-- buttons for desktop -->
        <div class="d-none d-md-flex ms-md-3">
          <RouterLink to="/weeklycalendar" class="btn d-none d-md-block align-content-center">View
            Schedule</RouterLink>
          <RouterLink to="/requestslist" class="btn d-none d-md-block align-content-center">View
            My Requests</RouterLink>
          <RouterLink v-if="userStore.user.role!=2" to="/viewstaffrequests" class="btn d-none d-md-block align-content-center">
            View Staff Requests
          </RouterLink>
          <v-btn @click="dialog = true" variant="outlined" text="Apply to WFH" class="btn"></v-btn>
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

                <!-- Request -->
                <v-text-field v-model="newEvent.date" label="Date of Request" type="date" :min="twoWeeksBefore"
                  :max="threeMonthsAfter" :error-messages="errors.date" required></v-text-field>
                <v-text-field v-if="requestType == 'recurring'" v-model="newEvent.endDate" label="End Date" type="date"
                  :min="newEvent.date" :max="threeMonthsAfter" :error-messages="errors.endDate" required></v-text-field>
                <p v-if="newEvent.date != '' && newEvent.endDate != ''" :error-messages="errors.endDate">
                  This event will repeat every {{ dayOfWeek }} from
                  {{ newEvent.date }} to
                  {{ newEvent.endDate }}
                </p>

                <v-radio-group v-model="newEvent.shift" label="Timing for Work From Home" row required
                  :error-messages="errors.shift">
                  <v-radio label="AM (09:00-13:00)" value="AM"></v-radio>
                  <v-radio label="PM (14:00-18:00)" value="PM"></v-radio>
                  <v-radio label="FULL (09:00-18:00)" value="Full"></v-radio>
                </v-radio-group>

                <v-text-field v-model="newEvent.reason" label="Reason for Request" :counter="100"
                  :rules="[is_within_word_count]" :error-messages="errors.reason" required></v-text-field>
              </v-form>
            </v-card-text>
            <v-card-actions>
              <v-btn color="green-darken-1" @click="validateAndConfirmApply">
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
        <UserSelection />

        <!-- dropdown menu for mobile -->
        <div class="d-md-none w-100" id="mobile-menu" v-show="isMenuOpen">
          <div class="d-flex flex-column">
            <v-btn class="justify-content-start" href="/weeklycalendar" @click="toggleMenu" variant="plain">View
              Schedule</v-btn>
            <v-btn class="justify-content-start" href="/requestslist" @click="toggleMenu" variant="plain">View
              My Requests</v-btn>
            <v-btn v-if="userStore.user.role!=2" class="justify-content-start" href="/viewstaffrequests" @click="toggleMenu" variant="plain">View
              Staff Requests</v-btn>
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
      dialog: false,
      loading: false,
      requestType: "one-time",
      isMenuOpen: false,
      dayOfWeek: "",
      twoWeeksBefore: "",
      threeMonthsAfter: "",
      newEvent: {
        staffId: "",
        date: "",
        endDate: "",
        shift: "",
        reason: "",
      },
      errors: {
        date: "",
        endDate: "",
        shift: "",
        reason: "",
      }
    }
  },
  mounted() {
    this.twoWeeksBefore = two_months_before(new Date());
    this.threeMonthsAfter = three_months_after(new Date());
  },
  watch: {
    "newEvent.date"() {
      const date = new Date(this.newEvent.date);
      this.dayOfWeek = date.toLocaleString("en-US", { weekday: "long" });
      if (this.newEvent.date !== "") {
        this.errors.date = null;
      }
    },
    "newEvent.endDate"() {
      if (this.newEvent.endDate !== "") {
        this.errors.endDate = null;
      }
    },
    "newEvent.shift"() {
      if (this.newEvent.shift !== "") {
        this.errors.shift = null;
      }
    },
    "newEvent.reason"() {
      if (this.newEvent.reason !== "") {
        this.errors.reason = null;
      };
      if (this.newEvent.reason.length > 100) {
        this.errors.reason = "Reason needs to be below 100 characters";
      }
    },
  },
  methods: {
    toggleMenu() {
      this.isMenuOpen = !this.isMenuOpen;
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
    validateInputs() {
      let isValid = true;

      if (!this.newEvent.date) {
        this.errors.date = "Please select a date";
        isValid = false;
      } else {
        this.errors.date = null;
      }
      if (this.requestType === "recurring") {
        if (!this.newEvent.endDate) {
          this.errors.endDate = "Please select an end date";
          isValid = false;
        } else {
          this.errors.endDate = null;
        }
      }
      if (!this.newEvent.shift) {
        this.errors.shift = "Please select a shift";
        isValid = false;
      } else {
        this.errors.shift = null;
      }
      if (!this.newEvent.reason) {
        this.errors.reason = "Please enter a reason";
        isValid = false;
      } else if (this.newEvent.reason.length > 100) {
        this.errors.reason = "Reason needs to be below 100 characters";
        isValid = false;
      } else {
        this.errors.reason = null;
      }
      return isValid
    },
    validateAndConfirmApply() {
      if (this.validateInputs()) {
        this.loading = true;
        console.log("newEvent", this.newEvent);
        if (
          this.requestType === "one-time"
        ) {
          fetch("http://localhost:5001/request/create", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              staff_id: this.newEvent.staffId,
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
          this.requestType === "recurring"
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
          // alert("Please fill in all required fields and try again.");
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
}
</script>

<style scoped>
header {
  box-shadow: 0 3px 12px #00000014;
}

.btn {
  text-transform: unset;

  &:hover {
    background-color: #00000014;
  }
}
</style>