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

      <!-- choose dates to rescind request for -->
      <v-card-text v-if="this.newStatus === 'Rescinded' && this.isLoading" class="align-self-center">
        <v-progress-circular indeterminate :size="40" :width="2" color="primary" class="me-1"></v-progress-circular>
      </v-card-text>
      <v-card-text v-else-if="this.newStatus === 'Rescinded' && !this.isLoading">
        <v-checkbox v-for="request in rescindableRequests" v-bind:key="request.request_date_id"
          :label="request.request_date" :value="request.request_date" v-model="selectedRequestsToRescind"
          hide-details></v-checkbox>
        <v-text-field v-model="reason" outlined label="Reason for rescinding"></v-text-field>
      </v-card-text>

      <!-- input reason (applies to all ManagerActions) -->
      <v-card-text v-else-if="this.newStatus !== 'Approved'">
        <v-text-field v-model="reason" outlined label="Reason for rejection"></v-text-field>
      </v-card-text>
      <v-card-actions>
        <v-btn @click="closeDialog" text>Cancel</v-btn>
        <v-btn @click="confirmAction(item)" color="pink" text>Confirm</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
// import { VProgressCircular } from 'vuetify/lib/components/index.mjs';
export default {
  name: "ManagerActions",
  data() {
    return {
      dialogOpened: false,
      reason: "",
      newStatus: "",
      isLoading: false,
      rescindableRequests: [],
      selectedRequestsToRescind: [],
    }
  },
  props: {
    item: Object,
  },
  methods: {
    toggleDialog(newStatus) {
      this.dialogOpened = !this.dialogOpened;
      if (newStatus) {
        this.newStatus = newStatus
      }

      if (newStatus === "Rescinded") {
        this.isLoading = true;
        const item_request_id = this.item.request_id;
        fetch(`http://localhost:5002/request_dates/get_by_request_id/${item_request_id}`)
          .then((response) => response.json())
          .then((data) => {
            this.rescindableRequests = data[0].data;
            this.isLoading = false;
          })
      }
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
      console.log("hello!", item);
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
          location.reload();
          this.newStatus = '';
        })
        .catch(error => console.error('Error updating status:', error));
    },
    rescind(item) {
      fetch('http://localhost:5002/request_dates/change_partial_status', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          "request_id": item.request_id,
          "status": "Rescinded",
          "dates": this.selectedRequestsToRescind,
          "shift": item.shift,
          "reason": this.reason,
        })
      })
        .then(response => response.json())
        .then(data => {
          console.log('Success:', data);
          location.reload();
        })
    },
  },
}

</script>