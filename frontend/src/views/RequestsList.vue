<template>
    <div class="container mt-5">
        <v-card flat>
            <v-card-title class="d-flex align-center pe-2">
                Requests List
                <v-spacer></v-spacer>
                <v-text-field v-model="search" density="compact" label="Search" prepend-inner-icon="mdi-magnify"
                    variant="solo-filled" flat hide-details single-line></v-text-field>
            </v-card-title>

            <v-divider></v-divider>

            <!-- Define the Data Table with headers and items -->
            <v-data-table v-model:search="search" :items="items">

                <!-- Date Requested Column -->
                <template v-slot:item.request_id="{ item }">
                    <div>{{ item.request_id }}</div>
                </template>

                <!-- Date Requested Column -->
                <template v-slot:item.creationdate="{ item }">
                    <div>{{ item.creationdate }}</div>
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
                    <div>
                        <!-- Show Withdraw button only for Approved or Pending statuses -->
                        <v-btn v-if="canWithdraw(item.status, item.wfhRequestDate)" @click="openWithdrawDialog(item)"
                            color="pink" variant="outlined" small>
                            Withdraw
                        </v-btn>
                        <ManagerActions :item="item" />
                    </div>
                </template>

                <!-- Status Column with color coding -->
                <template v-slot:item.reject_reason="{ item }">
                    <div>{{ item.reject_reason }}</div>
                </template>
            </v-data-table>
        </v-card>

        <!-- Withdraw Dialog -->
        <v-dialog v-model="withdrawDialog" max-width="600">
            <v-card>
                <v-card-title>Withdraw Request</v-card-title>
                <v-card-text>
                    <v-text-field v-model="withdrawReason" label="Reason for withdrawal" outlined></v-text-field>
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
import ManagerActions from '@/components/ManagerActions.vue';

export default {
    components: {
        ManagerActions
    },
    data() {
        return {
            search: "",
            withdrawDialog: false,
            withdrawReason: "",
            selectedItem: null,
            items: [],
        };
    },
    created() {
        this.formatData();
    },
    methods: {
        // Format the data to the structure needed for the table
        formatData() {
            // #####################################################################################
            fetch(`http://localhost:5101/s_retrieve_requests/150488`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    const rawData = data["data"];

                    this.items = rawData.flatMap((item) =>
                        item.wfh_dates[0].data.map((wfh) => ({
                            request_id: item.request_id,
                            creationdate: item.creation_date,
                            wfhRequestDate: wfh.request_date,
                            shift: wfh.request_shift,
                            status: wfh.request_status,
                            withdraw: wfh.withdraw_reason,
                            Remarks: item.reject_reason
                        }))
                    );
                })
                .catch(error => {
                    console.error('Error fetching requests:', error);
                });
        },

        // Determine if the Withdraw button should be shown (Approved or Pending statuses only)
        canWithdraw(status, wfhRequestDate) {
            const TWO_WEEKS_IN_MS = 14 * 24 * 60 * 60 * 1000;  // 2 weeks in milliseconds
            const currentDate = new Date();
            const requestDate = new Date(wfhRequestDate);  // Convert wfhRequestDate to a Date object

            const isWithinTwoWeeks = (requestDate - currentDate) <= TWO_WEEKS_IN_MS && (requestDate >= currentDate);

            return (status === "Approved" && isWithinTwoWeeks) || status === "Pending Approval";
        },


        // Get status color classes for each status
        getStatusColor(status) {
            if (status === "Approved") return "text-success";
            if (status === "Rejected") return "text-error";
            if (status === "Pending Withdrawal") return "text-pink";
            return "text-warning";
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
            let new_status;

            if (item.status === "Approved") {
                new_status = "Pending Withdrawal";
            } else {
                new_status = "Withdrawn";
            }

            const data = {
                "request_id": item.request_id,
                "status": new_status,
                "reason": item.withdraw_reason,
                "dates": [item.wfhRequestDate],
                "shift": item.shift
            };

            fetch(`http://localhost:5002/request_dates/change_partial_status`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
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
                })
                .catch(error => console.error('Error updating status:', error));

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
    top: 80px;
    /* Position below the header */
    left: 50%;
    /* Center horizontally */
    transform: translateX(-50%);
    /* Include padding in total height/width */
    overflow-y: auto;
    /* Allow vertical scrolling for overflow */
    bottom: 40px;
}


/* Hide scrollbars for Chrome and Safari */
.requests::-webkit-scrollbar {
    display: none;
    /* Safari and Chrome */
}

/* Hide scrollbars for Firefox */
.requests {
    scrollbar-width: none;
    /* Firefox */
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