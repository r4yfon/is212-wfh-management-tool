<template>
  <!-- button to approve pending request -->
  <v-btn v-if="item.status === 'Pending Approval'" @click="openDialog('Approved')" color="green" :item="item"
    variant="outlined" small>
    Approve
  </v-btn>

  <!-- button to reject pending request -->
  <v-btn v-if="item.status === 'Pending Approval'" @click="openDialog('Rejected')" color="red" :item="item"
    variant="outlined" small>
    Reject
  </v-btn>

  <v-btn v-if="item.status === 'Approved' && withinRescindTimeLimit(item.request_date)" @click="openDialog('Rescinded')"
    color="red" :item="item" variant="outlined" small>
    Rescind
  </v-btn>

  <v-btn v-if="item.status === 'Pending Withdrawl'" @click="openDialog('Withdrawn')" color="green" :item="item"
    variant="outlined" small>
    Approve Withdrawal
  </v-btn>

  <!-- popup -->
  <v-dialog v-model="dialogOpened" max-width="600">

    <v-card>
      <!-- for request that will be approved -->
      <v-card-title v-if="this.newStatus === 'Approved'">
        Approve request
      </v-card-title>
      <!-- for request that will be rejected -->
      <v-card-title v-else-if="this.newStatus === 'Rejected'">
        Reject request
      </v-card-title>
      <!-- for request that will be withdrawn -->
      <v-card-title v-else-if="this.newStatus === 'Withdrawn'">
        Approve request withdrawal
      </v-card-title>
      <!-- for request that will be rescinded -->
      <v-card-title v-else-if="this.newStatus === 'Rescinded'">
        Select requested dates to rescind
      </v-card-title>

      <!-- loading indicator -->
      <v-card-text v-if="this.isLoading" class="align-self-center">
        <v-progress-circular indeterminate :size="40" :width="2" color="primary" class="me-1"></v-progress-circular>
      </v-card-text>

      <!-- display attendance rate if manager is about to approve request -->
      <v-card-text v-else-if="newStatus === 'Approved'">
        <p>Requested date(s): {{ this.request_dates.join(", ") }}</p>
        <p>By approving this request,</p>
        <div v-for="request_date in this.request_dates" :key="request_date" class="mb-3">
          <p>
            {{ request_date }}: {{ dept_wfh_schedule[request_date].length + 1 }}/{{ this.num_employees_in_dept
            }}
            employees in the department will be WFH.
          </p>
          <p
            :class="{ 'text-danger': attendance_in_office(request_date) < 50, 'text-success': attendance_in_office(request_date) >= 50 }">
            Attendance rate in office: {{ attendance_in_office(request_date) }}%
          </p>
        </div>
      </v-card-text>

      <!-- choose dates to rescind request for -->
      <v-card-text v-else-if="newStatus === 'Rescinded'">
        <v-checkbox v-for="request in alreadyRescinded" disabled value="1" :key="request.request_date_id"
          :label="request.request_date" model-value="1" hide-details></v-checkbox>
        <v-checkbox v-for="request in rescindableRequests" :key="request.request_date_id" :label="request.request_date"
          :value="request.request_date" v-model="datesToRescind"
          :error-messages="errorMessages.datesToRescind"></v-checkbox>
        <v-text-field v-model="reason" outlined label="Reason for rescinding" :error-messages="errorMessages.reason"
          class="mt-4"></v-text-field>
      </v-card-text>

      <!-- input reason (applies to all ManagerActions) -->
      <v-card-text v-else-if="newStatus === 'Rejected'">
        <v-text-field v-model="reason" outlined label="Reason for rejection"
          :error-messages="errorMessages.reason"></v-text-field>
      </v-card-text>
      <v-card-actions>
        <v-btn @click="closeDialog" text>Cancel</v-btn>
        <v-btn @click="confirmAction(item)" color="pink" text>
          <span v-if="buttonIsLoading">
            <v-progress-circular indeterminate :size="15" :width="2" color="primary" class="me-1"></v-progress-circular>
          </span>
          Confirm</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { useMainStore } from "@/store";
import { url_paths } from "@/url_paths";
const userStore = useMainStore();

export default {
  name: "ManagerActions",
  data() {
    return {
      dialogOpened: false,
      reason: "",
      newStatus: "",
      isLoading: false,
      buttonIsLoading: false,
      num_employees_in_dept: 0,
      dept_wfh_schedule: {},
      request_dates: [],
      alreadyRescinded: [],
      rescindableRequests: [],
      datesToRescind: [],
      errorMessages: {
        datesToRescind: [],
        reason: []
      },
    }
  },
  props: {
    item: Object,
  },

  emits: ['refresh-data'],

  computed: {
    attendance_in_office(request_date) {
      return ((1 - ((this.dept_wfh_schedule[request_date].length + 1) / this.num_employees_in_dept)) * 100).toFixed(2);
    },
  },

  methods: {
    openDialog(newStatus) {
      this.dialogOpened = true;
      this.newStatus = newStatus;

      if (newStatus === "Approved") {
        const item_request_id = this.item.request_id;
        this.isLoading = true;
        fetch(`${url_paths.view_schedule}/get_wfh_status_by_team/${userStore.user.staff_id}`)
          .then(response => response.json())
          .then(data => {
            this.num_employees_in_dept = data.num_employee_in_dept;
            this.dept_wfh_schedule = data.data;
          })
          .then(() => {
            fetch(`${url_paths.request_dates}/get_by_request_id/${item_request_id}`)
              .then(response => response.json())
              .then(data => {
                this.request_dates = data[0].data.map(item => item.request_date);
                this.isLoading = false;
              });
          })
      }

      if (newStatus === "Rescinded") {
        this.isLoading = true;
        const item_request_id = this.item.request_id;
        fetch(`${url_paths.request_dates}/get_by_request_id/${item_request_id}`)
          .then((response) => response.json())
          .then((data) => {
            this.rescindableRequests = data[0].data.filter(request => request.request_status !== "Rescinded");
            this.alreadyRescinded = data[0].data.filter(request => request.request_status === "Rescinded");
            this.isLoading = false;
          })
      }
    },

    closeDialog() {
      this.reason = "";
      this.errorMessages.datesToRescind = [];
      this.errorMessages.reason = [];
      this.dialogOpened = false;
    },

    noErrorMessages() {
      return Object.values(this.errorMessages).every(arr => arr.length === 0);
    },

    confirmAction(item) {
      this.errorMessages.reason = [];
      this.errorMessages.datesToRescind = [];

      if (this.newStatus !== "Approved" && !this.reason) {
        this.errorMessages.reason.push("Reason cannot be empty");
      }
      if (this.newStatus === "Rescinded" && this.datesToRescind.length === 0) {
        this.errorMessages.datesToRescind.push("Please select at least one date to rescind");
      }
      if (this.newStatus !== "Rescinded" && this.noErrorMessages()) {
        this.approveRejectWithdraw(item);
      } else if (this.newStatus === "Rescinded" && this.noErrorMessages()) {
        this.rescind(item);
      }
    },

    // Determine if the Rescind button should be shown
    withinRescindTimeLimit(request_date) {
      const currentDate = new Date();
      const requestDate = new Date(request_date);

      // Calculate the date 1 month before the current date
      const oneMonthBefore = new Date(currentDate);
      oneMonthBefore.setMonth(currentDate.getMonth() - 1);

      // Calculate the date 3 months after the current date
      const threeMonthsAfter = new Date(currentDate);
      threeMonthsAfter.setMonth(currentDate.getMonth() + 3);

      // Check if the request date is within the range
      return (requestDate >= oneMonthBefore && requestDate <= threeMonthsAfter);
    },

    approveRejectWithdraw(item) {
      this.buttonIsLoading = true;
      fetch(`${url_paths.request_dates}/change_all_status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          "request_id": item.request_id,
          "status": this.newStatus,
          "reason": this.reason,
        })
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          this.buttonIsLoading = false;
          this.newStatus = '';
          this.$emit('refresh-data');
          this.closeDialog();
          return response.json();
        })
        .catch(error => console.error('Error updating status:', error));
    },
    rescind(item) {
      this.buttonIsLoading = true;
      fetch(`${url_paths.request_dates}/change_partial_status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          "request_id": item.request_id,
          "status": "Rescinded",
          "dates": this.datesToRescind,
          "shift": item.shift,
          "reason": this.reason,
        })
      })
        .then(() => {
          this.buttonIsLoading = false;
          this.$emit('refresh-data');
          this.closeDialog();
        })
    },
  },
}

</script>

<style scoped>
div.mb-3>p {
  margin-bottom: 0.25rem;
}
</style>