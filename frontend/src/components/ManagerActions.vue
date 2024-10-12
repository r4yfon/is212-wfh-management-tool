<template>
  <!-- button to approve pending request -->
  <v-btn v-if="item.status === 'Pending Approval'" @click="toggleDialog('Approved')" color="green" :item="item"
    variant="outlined" small>
    Approve
  </v-btn>

  <!-- button to reject pending request -->
  <v-btn v-if="item.status === 'Pending Approval'" @click="toggleDialog('Rejected')" color="red" :item="item"
    variant="outlined" small>
    Reject
  </v-btn>

  <v-btn v-if="item.status === 'Approved'" @click="toggleDialog('Rescinded')" color="red" :item="item"
    variant="outlined" small>
    Rescind
  </v-btn>

  <v-btn v-if="item.status === 'Pending Withdrawl'" @click="toggleDialog('Withdrawn')" color="green" :item="item"
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
      <v-card-text v-else-if="this.newStatus === 'Approved' && !this.isLoading">
        <p>Requested date(s): {{ this.request_dates.join(", ") }}</p>
        <p>By approving this request,</p>
        <div v-for="request_date in this.request_dates" :key="request_date" class="mb-3">
          <p>
            {{ request_date }}: {{ dept_wfh_schedule[request_date]?.length || 1 }}/{{ this.num_employees_in_dept }}
            employees in the department will be WFH.
          </p>
          <p
            :class="{ 'text-danger': attendance_in_office(request_date) < 50, 'text-success': attendance_in_office(request_date) >= 50 }">
            Attendance rate in office: {{ attendance_in_office(request_date) }}%
          </p>
        </div>
      </v-card-text>

      <!-- choose dates to rescind request for -->
      <v-card-text v-else-if="this.newStatus === 'Rescinded' && !this.isLoading">
        <v-checkbox v-for="request in alreadyRescinded" disabled value="1" :key="request.request_date_id"
          :label="request.request_date" model-value="1" hide-details></v-checkbox>
        <v-checkbox v-for="request in rescindableRequests" :key="request.request_date_id" :label="request.request_date"
          :value="request.request_date" v-model="datesToRescind" hide-details></v-checkbox>
        <v-text-field v-model="reason" outlined label="Reason for rescinding"></v-text-field>
      </v-card-text>

      <!-- input reason (applies to all ManagerActions) -->
      <v-card-text v-else-if="this.newStatus !== 'Approved'">
        <v-text-field v-model="reason" outlined label="Reason for rejection"></v-text-field>
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
const userStore = useMainStore();
const url_paths = userStore.paths;

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
    }
  },
  props: {
    item: Object,
  },
  emits: ['refresh-data'],
  methods: {
    toggleDialog(newStatus) {
      this.dialogOpened = !this.dialogOpened;
      if (newStatus) {
        this.newStatus = newStatus
      }

      if (newStatus === "Approved") {
        const item_request_id = this.item.request_id;
        this.isLoading = true;
        fetch(`${url_paths.view_schedule}/get_wfh_status/${userStore.user.department}`)
          .then(response => response.json())
          .then(data => {
            console.log(data);
            this.num_employees_in_dept = data.num_employee_in_dept;
            this.dept_wfh_schedule = data.data;
          })
        fetch(`${url_paths.request_dates}/get_by_request_id/${item_request_id}`)
          .then(response => response.json())
          .then(data => {
            // console.log(data[0].data);
            this.request_dates = data[0].data.map(item => item.request_date);
            console.log(this.request_dates)
            this.isLoading = false;
          });
      }

      if (newStatus === "Rescinded") {
        this.isLoading = true;
        const item_request_id = this.item.request_id;
        fetch(`http://localhost:5002/request_dates/get_by_request_id/${item_request_id}`)
          .then((response) => response.json())
          .then((data) => {
            console.log(data)
            this.rescindableRequests = data[0].data.filter(request => request.request_status !== "Rescinded");
            this.alreadyRescinded = data[0].data.filter(request => request.request_status === "Rescinded");
            // this.selectedRequestsToRescind = data[0].data.filter(request => request.request_status === "Approved");
            this.isLoading = false;
            console.log("alreadyRescinded", this.alreadyRescinded)
            // console.log("selectedRequestsToRescind", this.selectedRequestsToRescind)
            console.log("rescindableRequests", this.rescindableRequests)
          })
      }
    },
    compareItems(a, b) {
      console.log("a", a);
      console.log("b", b);
      console.log("selectedRequests", this.selectedRequestsToRescind)
      console.log("rescindable", this.rescindableRequests)
      return a.request_date === b;
    },
    isAlreadyRescinded(request_date) {
      return this.alreadyRescinded.some(item => item.request_date === request_date);
    },

    attendance_in_office(request_date) {
      return (100 - (this.dept_wfh_schedule[request_date]?.length / this.num_employees_in_dept * 100)).toFixed(2);
    },

    closeDialog() {
      this.reason = "";
      this.toggleDialog();
    },
    confirmAction(item) {
      if (this.newStatus === 'Rejected' || this.newStatus === "Approved" || this.newStatus === 'Withdrawn') {
        this.approveRejectWithdraw(item);
      } else if (this.newStatus === "Rescinded") {
        this.rescind(item);
      }
    },
    approveRejectWithdraw(item) {
      this.buttonIsLoading = true;
      fetch('http://localhost:5002/request_dates/change_all_status', {
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
          return response.json();
        })
        .then(responseData => {
          console.log('Success:', responseData);
          this.buttonIsLoading = false;
          location.reload();
          this.newStatus = '';
        })
        .catch(error => console.error('Error updating status:', error));
    },
    rescind(item) {
      this.buttonIsLoading = true;
      fetch('http://localhost:5002/request_dates/change_partial_status', {
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
        .then(response => response.json())
        .then(data => {
          console.log('Success:', data);
          this.buttonIsLoading = false;
          this.$emit('refresh-data');
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