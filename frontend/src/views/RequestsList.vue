<template>
  <div class="requests-container"> 
      <v-card flat>
          <v-card-title class="d-flex align-center pe-2">
          Requests List
          <v-spacer></v-spacer>
          <v-text-field
              v-model="search"
              density="compact"
              label="Search"
              prepend-inner-icon="mdi-magnify"
              variant="solo-filled"
              flat
              hide-details
              single-line
          ></v-text-field>
          </v-card-title>
  
          <v-divider></v-divider>
  
          <!-- Define the Data Table with headers and items -->
          <v-data-table v-model:search="search" :items="items">
          
              <!-- Date Requested Column -->
              <template v-slot:item.request_date="{ item }">
                  <div>{{ item.request_date }}</div>
              </template>
  
              <!-- WFH Request Date Column -->
              <template v-slot:item.wfhRequestDate="{ item }">
                  <div>{{ item.wfhRequestDate }}</div>
              </template>

              <!-- Shift Column -->
              <template v-slot:item.shift="{ item }">
                  <div>{{ item.shift }}</div>
              </template>
  
              <!-- Status Column with color coding -->
              <template v-slot:item.status="{ item }">
                  <div :class="getStatusColor(item.status)">
                  {{ item.status }}
                  </div>
              </template>
  
              <!-- Withdraw Column -->
              <template v-slot:item.withdraw="{ item }">
                  <div class="text-end">
                  <!-- Show Withdraw button only for Approved or Pending statuses -->
                  <v-btn
                      v-if="canWithdraw(item.status)"
                      @click="openWithdrawDialog(item)"
                      color="pink"
                      variant="outlined"
                      small
                  >
                      Withdraw
                  </v-btn>
                  </div>
              </template>
          </v-data-table>
      </v-card>

      <!-- Withdraw Dialog -->
      <v-dialog v-model="withdrawDialog" max-width="600">
          <v-card>
          <v-card-title>Withdraw Request</v-card-title>
          <v-card-text>
              <v-text-field
                  v-model="withdrawReason"
                  label="Reason for withdrawal"
                  outlined
              ></v-text-field>
          </v-card-text>
          <v-card-actions>
              <v-btn @click="withdrawDialog = false" text>Cancel</v-btn>
              <v-btn @click="confirmWithdraw(selectedItem)" color="pink" text>Confirm</v-btn>
          </v-card-actions>
          </v-card>
      </v-dialog>

  </div>
</template>


<script>
export default {
  data() {
    return {
      search: "",
      withdrawDialog: false,
      withdrawReason: "",
      selectedItem: null, // Track the selected item for withdrawal
      items: this.formatData(),
    };
  },
  methods: {
    // Format the data to the structure needed for the table
    formatData() {
      const rawData = [
        {
          apply_reason: "Family event",
          reject_reason: null,
          request_date: "2024-09-15",
          request_id: 1,
          staff_id: 150488,
          wfh_dates: [
            {
              code: 200,
              data: [
                {
                  request_date: "2024-09-15",
                  request_shift: "PM",
                  request_status: "Approved",
                  withdraw_reason: null
                },
                {
                  request_date: "2024-09-22",
                  request_shift: "Full",
                  request_status: "Pending Approval",
                  withdraw_reason: null
                },
                {
                  request_date: "2024-09-29",
                  request_shift: "AM",
                  request_status: "Rejected",
                  withdraw_reason: null
                },
                {
                  request_date: "2024-09-15",
                  request_shift: "PM",
                  request_status: "Approved",
                  withdraw_reason: null
                },
                {
                  request_date: "2024-09-30",
                  request_shift: "AM",
                  request_status: "Pending Approval",
                  withdraw_reason: null
                },
                {
                  request_date: "2024-09-15",
                  request_shift: "Full",
                  request_status: "Approved",
                  withdraw_reason: null
                },
                {
                  request_date: "2024-09-25",
                  request_shift: "PM",
                  request_status: "Approved",
                  withdraw_reason: null
                },
                {
                  request_date: "2024-09-24",
                  request_shift: "PM",
                  request_status: "Rejected",
                  withdraw_reason: null
                },
                {
                  request_date: "2024-09-23",
                  request_shift: "PM",
                  request_status: "Approved",
                  withdraw_reason: null
                },
                {
                  request_date: "2024-09-15",
                  request_shift: "PM",
                  request_status: "Approved",
                  withdraw_reason: null
                },
                {
                  request_date: "2024-09-16",
                  request_shift: "PM",
                  request_status: "Approved",
                  withdraw_reason: null
                },
                {
                  request_date: "2024-09-17",
                  request_shift: "AM",
                  request_status: "Approved",
                  withdraw_reason: null
                },

              ]
            }
          ]
        },
        {
          apply_reason: "Family event",
          reject_reason: null,
          request_date: "2024-10-15",
          request_id: 11,
          staff_id: 150488,
          wfh_dates: [
            {
              code: 200,
              data: [
                {
                  request_date: "2024-10-15",
                  request_shift: "PM",
                  request_status: "Approved",
                  withdraw_reason: null
                }
              ]
            }
          ]
        }
      ];

      return rawData.flatMap((item) =>
        item.wfh_dates[0].data.map((wfh) => ({
          dateRequested: item.request_date,
          WFHRequestDate: wfh.request_date,
          shift: wfh.request_shift,
          status: wfh.request_status,
          withdraw: wfh.withdraw_reason
        }))
      );
    },
    
    // Determine if the Withdraw button should be shown (Approved or Pending statuses only)
    canWithdraw(status) {
      return status === "Approved" || status === "Pending Approval";
    },
    
    // Get status color classes for each status
    getStatusColor(status) {
      if (status === "Approved") return "text-success";
      if (status === "Rejected") return "text-error";
      if (status === "Pending Withdrawal") return "text-pink";
      return "text-warning"; // For Pending Approval
    },

    // Open the Withdraw dialog
    openWithdrawDialog(item) {
      this.selectedItem = item;
      this.withdrawReason = "";
      this.withdrawDialog = true;
    },

    // Confirm withdrawal action
    confirmWithdraw(item) {
      item.withdraw_reason = this.withdrawReason;
      item.status = "Pending Withdrawal";
      this.withdrawDialog = false;
    }
  }
};
</script>



<style scoped>
.requests-container {
display: flex;
justify-content: center;   
align-items: flex-start;   
box-sizing: border-box;   
width: 95%;                    
max-height: calc(100vh - 80px);      
position: fixed;                 
top: 80px;                       /* Position below the header */
left: 50%;                       /* Center horizontally */
transform: translateX(-50%);   /* Include padding in total height/width */
overflow-y: auto;                /* Allow vertical scrolling for overflow */
bottom: 40px;
}


/* Hide scrollbars for Chrome and Safari */
.requests::-webkit-scrollbar {
display: none; /* Safari and Chrome */
}

/* Hide scrollbars for Firefox */
.requests {
scrollbar-width: none; /* Firefox */
}

/* Responsive styles for smaller screens */
@media (max-width: 768px) {
.requests {
  width: 100%;                  
  height: calc(100vh - 80px);     
  top: 80px;                    
  left: 0;                      
  transform: none;              
}
}

</style> 