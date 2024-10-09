<template>
    <div class="requests-container">
        <v-card flat>
            <v-card-title class="d-flex align-center pe-2">
                WFH Requests List from Staff
                <v-spacer></v-spacer>
                <v-text-field v-model="search" density="compact" label="Search" prepend-inner-icon="mdi-magnify"
                    variant="solo-filled" flat hide-details single-line></v-text-field>
            </v-card-title>

            <v-divider></v-divider>

            <v-card>
            <v-tabs
                v-model="tab"
                align-tabs="center"
                color="red-lighten-2"
            >
                <v-tab :value="1">Pending Requests</v-tab>
                <v-tab :value="2">Approved Requests</v-tab>
                <v-tab :value="3">Rejected/Rescinded Requests</v-tab>
            </v-tabs>

            <v-tabs-window v-model="tab" color="red-lighten-2">
                <v-tabs-window-item
                    v-for="n in 3"
                    :key="n"
                    :value="n"
                ></v-tabs-window-item>

                <v-card-text>
                    <v-tabs-window v-model="tab">
                        <v-tabs-window-item value="1">
                            <v-data-table v-model:search="search" :items="items">

                            <!-- Date Requested Column -->
                            <template v-slot:item.request_id="{ item }">
                                <div>{{ item.request_id }}</div>
                            </template>

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

                            <!-- Approve Column -->
                            <template v-slot:item.approve="{ item }">
                                <v-btn color="green" variant="outlined" small>
                                    Approve
                                </v-btn>
                            </template>

                            <!-- Reject Column -->
                            <template v-slot:item.reject="{ item }">
                                <v-btn color="red" @click="openRejectDialog(item)" variant="outlined" small>
                                    Reject
                                </v-btn>
                            </template>
                            </v-data-table>

                        </v-tabs-window-item>

                        <v-tabs-window-item value="2">
                            <v-data-table v-model:search="search" :items="items">

                            <!-- Date Requested Column -->
                            <template v-slot:item.request_id="{ item }">
                                <div>{{ item.request_id }}</div>
                            </template>

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

                            <!-- Rescind Column -->
                            <template v-slot:item.rescind="{ item }">
                                <div class="text-end">
                                    <v-btn v-if="canRescind(item.status, item.wfhRequestDate)" @click="openRescindDialog(item)" color="red"
                                        variant="outlined" small>
                                        Rescind
                                    </v-btn>
                                </div>
                            </template>
                            </v-data-table>
                        </v-tabs-window-item>

                        <v-tabs-window-item value="3">
                            <v-data-table v-model:search="search" :items="items">

                            <!-- Date Requested Column -->
                            <template v-slot:item.request_id="{ item }">
                                <div>{{ item.request_id }}</div>
                            </template>

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
                            </v-data-table>
                        </v-tabs-window-item>
                    </v-tabs-window>
                </v-card-text>
            </v-tabs-window>
            </v-card>
    </v-card>

        <!-- Reject Dialog -->
        <v-dialog v-model="RejectDialog" max-width="600">
            <v-card>
                <v-card-title>Reject Request</v-card-title>
                <v-card-text>
                    <v-text-field v-model="rejectReason" label="Reason for Rejection" outlined></v-text-field>
                </v-card-text>
                <v-card-actions>
                    <v-btn @click="rejectDialog = false" text>Cancel</v-btn>
                    <v-btn @click="confirmReject(selectedItem)" color="red" text>Confirm</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>

        <!-- Rescind Dialog -->
        <v-dialog v-model="RescindDialog" max-width="600">
            <v-card>
                <v-card-title>Rescind Approved Request</v-card-title>
                <v-card-text>
                    <v-text-field v-model="rescindReason" label="Reason to Rescind Approved Request" outlined></v-text-field>
                </v-card-text>
                <v-card-actions>
                    <v-btn @click="rescindDialog = false" text>Cancel</v-btn>
                    <v-btn @click="confirmRescind(selectedItem)" color="red" text>Confirm</v-btn>
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
            rejectDialog: false,
            rejectReason: "",
            rescindDialog: false,
            rescindReason: "",
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
            fetch(`http://localhost:5101/s_retrieve_requests`)
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
                            request_date: item.request_date,
                            wfhRequestDate: wfh.request_date,
                            shift: wfh.request_shift,
                            status: wfh.request_status,
                            reject: wfh.reject_reason,
                            rescind: wfh.rescind_reason,
                        }))
                    );
                })
                .catch(error => {
                    console.error('Error fetching requests:', error);
                });
        },

        // Determine if the Rescind button should be shown
        canRescind(status, wfhRequestDate) {
            // const TWO_MTH_IN_MS = 14 * 24 * 60 * 60 * 1000;  // 2 weeks in milliseconds
            const currentDate = new Date();
            const currentDateStr = currentDate.toString()

            const mthOfRequestMade = Number(wfhRequestDate.slice(5,6))

            const isWithinTwoMonths = (mthOfRequestMade + 3 > currentDateStr.slice(5,7));

            return (status === "Approved" && isWithinTwoMonths);
        },


        // Get status color classes for each status
        getStatusColor(status) {
            if (status === "Approved") return "text-success";
            if (status === "Rejected") return "text-error";
            if (status === "Rescinded") return "text-error";
            if (status === "Pending Withdrawal") return "text-pink";
            return "text-warning";
        },

        // Open the Reject dialog
        openRejectDialog(item) {
            this.selectedItem = item;
            this.rejectReason = "";
            this.rejectDialog = true;
        },

        // Confirm reject action
        confirmReject(item) {
            item.reject_reason = this.rejectReason;
            let new_status;

            if (item.status === "Pending Approval") {
                new_status = "Rejected";
            } else if (item.status === "Pending Withdrawal") {
                new_status = "Rejected";
            }

            const data = {
                "request_id": item.request_id,
                "status": new_status,
                "reason": item.reject_reason,
                "dates": [item.wfhRequestDate]
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

            this.rejectDialog = false;
        },


        // Open the Rescind dialog
        openRescindDialog(item) {
            this.selectedItem = item;
            this.rescindReason = "";
            this.rescindDialog = true;
        },

        // Confirm rescind action
        confirmRescind(item) {
            item.rescind_reason = this.rescindReason;
            let new_status;

            if (item.status === "Approved") {
                new_status = "Rescinded";
            } 

            const data = {
                "request_id": item.request_id,
                "status": new_status,
                "reason": item.rescind_reason,
                "dates": [item.wfhRequestDate]
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

            this.rescindDialog = false;
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