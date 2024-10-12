<template>
    <div class="container mt-5">
        <v-card flat>
            <v-card-title class="d-flex align-center pe-2">
                Requests List
                <v-spacer></v-spacer>
                <v-text-field v-model="search" density="compact" label="Search" prepend-inner-icon="mdi-magnify"
                    variant="solo-filled" flat hide-details single-line></v-text-field>
            </v-card-title>

            <!-- Define the Data Table with headers and items -->
            <v-data-table v-model:search="search" :headers="headers" :items="items" item-key="request_id">
                <template v-slot:item="{ item }">
                    <tr>
                        <td>{{ item.request_id }}</td>
                        <td>{{ item.creationdate }}</td>
                        <td>{{ item.wfhRequestDate }}</td>
                        <td>{{ item.shift }}</td>
                        <td :class="getStatusColor(item.status)">
                            {{ item.status }}</td>
                        <td>
                            <v-btn v-if="canWithdraw(item.status, item.wfhRequestDate)"
                                @click="openWithdrawDialog(item)" color="pink" variant="outlined" small>
                                Withdraw
                            </v-btn>
                        </td>
                        <td>
                            <div>{{ item.remarks }}</div>
                        </td>
                    </tr>
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
import { useMainStore } from '@/store';
const userStore = useMainStore();

export default {
    data() {
        return {
            search: "",
            withdrawDialog: false,
            withdrawReason: "",
            selectedItem: null,
            items: [],
            headers: [
                { title: 'Request ID', value: 'request_id', key: "request_id" },
                { title: 'Creation Date', value: 'creationdate', key: "creationdate" },
                { title: 'Request Date', value: 'wfhRequestDate', key: "wfhRequestDate" },
                { title: 'Shift', value: 'shift', key: "shift" },
                { title: 'Status', value: 'status', key: "status" },
                { title: 'Actions', value: 'actions', key: "actions" },
                { title: 'Remarks', value: 'remarks', key: "remarks" }
            ]
        };
    },
    created() {
        fetch(`http://localhost:5002/request_dates/auto_reject`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(() => {
                console.log('Success');
            })
            .catch(error => console.error('Error updating status:', error));
        this.formatData();
    },
    methods: {
        // Format the data to the structure needed for the table
        formatData() {
            // #####################################################################################
            fetch(`http://localhost:5101/s_retrieve_requests/${userStore.user.staff_id}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    const rawData = data["data"];
                    console.log(data)
                    this.items = rawData.flatMap((item) =>
                        item.wfh_dates.map((wfh) => ({
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