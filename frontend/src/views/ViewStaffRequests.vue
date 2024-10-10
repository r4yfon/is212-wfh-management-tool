<template>
    <div class="container mt-4">
        <v-card flat>
            <v-card-title class="d-flex flex-column flex-md-row align-center mb-3 row-gap-1 row-gap-md-0">
                Staff Requests List
                <v-spacer></v-spacer>
                <v-text-field v-model="search" density="compact" label="Search" prepend-inner-icon="mdi-magnify"
                    variant="solo-filled" flat hide-details single-line class="w-100 w-md-initial"></v-text-field>
            </v-card-title>

            <!-- <v-card> -->
            <v-tabs v-model="tab" align-tabs="center" color="red-lighten-2">
                <v-tab :value="1">Pending Approval</v-tab>
                <v-tab :value="2">Approved</v-tab>
                <v-tab :value="3">Pending Withdrawal</v-tab>
                <v-tab :value="4">Rescinded</v-tab>
                <v-tab :value="5">Rejected</v-tab>
            </v-tabs>

            <v-tabs-window v-model="tab">
                <v-tabs-window-item v-for="n in 5" :key="n" :value="n">
                    <v-card-text>
                        <v-data-table v-model:search="search" :headers="headers" :items="filteredItems">
                            <template v-slot:item="{ item }">
                                <tr>
                                    <td>{{ item.request_id }}</td>
                                    <td>{{ item.creationDate }}</td>
                                    <td>{{ item.wfhRequestDate }}</td>
                                    <td>{{ item.shift }}</td>
                                    <td :class="getStatusColor(item.status)">
                                        {{ item.status }}</td>
                                    <td>
                                        <ManagerActions :item="item"></ManagerActions>
                                    </td>
                                </tr>
                            </template>
                        </v-data-table>
                    </v-card-text>
                </v-tabs-window-item>
            </v-tabs-window>
            <!-- </v-card> -->
        </v-card>

        <!-- Reject Dialog -->
        <v-dialog v-model="rejectDialog" max-width="600">
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
        <v-dialog v-model="rescindDialog" max-width="600">
            <v-card>
                <v-card-title>Rescind Approved Request</v-card-title>
                <v-card-text>
                    <v-text-field v-model="rescindReason" label="Reason to Rescind Approved Request"
                        outlined></v-text-field>
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
import ManagerActions from '@/components/ManagerActions.vue';
export default {
    components: {
        ManagerActions
    },
    data() {
        return {
            tab: 1,
            search: "",
            rejectDialog: false,
            rejectReason: "",
            rescindDialog: false,
            rescindReason: "",
            selectedItem: null,
            items: [],
            headers: [
                { title: 'Request ID', value: 'request_id' },
                { title: 'Creation Date', value: 'creationDate' },
                { title: 'Request Date', value: 'wfhRequestDate' },
                { title: 'Shift', value: 'shift' },
                { title: 'Status', value: 'status' },
                { title: 'Actions', value: 'actions' },
            ]
        };
    },
    computed: {
        filteredItems() {
            switch (this.tab) {
                case 1:
                    return this.items.filter(item => item.status === 'Pending Approval');
                case 2:
                    return this.items.filter(item => item.status === 'Approved');
                case 3:
                    return this.items.filter(item => item.status === 'Pending Withdrawal');
                case 4:
                    return this.items.filter(item => item.status === 'Rescinded');
                case 5:
                    return this.items.filter(item => item.status === 'Rejected');
                default:
                    return [];
            }
        },
    },
    mounted() {
        this.formatData();
    },
    methods: {
        // Format the data to the structure needed for the table
        formatData() {
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
                        item.wfh_dates.map((wfh) => ({
                            request_id: item.request_id,
                            creationDate: item.creation_date,
                            wfhRequestDate: wfh.request_date,
                            shift: wfh.request_shift,
                            status: wfh.request_status,
                            reject: wfh.reject_reason,
                            rescind: wfh.rescind_reason,
                        }))
                    );
                    console.log(this.items);
                })
                .catch(error => {
                    console.error('Error fetching requests:', error);
                });
        },

        // Determine if the Rescind button should be shown
        canRescind(status, wfhRequestDate) {
            const currentDate = new Date();
            const requestDate = new Date(wfhRequestDate);

            // Calculate the time difference in milliseconds
            const timeDiff = currentDate.getTime() - requestDate.getTime();

            // Convert time difference to months
            const diffInMonths = timeDiff / (1000 * 60 * 60 * 24 * 30);

            // Check if it's within 3 months and status is 'Approved'
            return (status === "Approved" && diffInMonths <= 3);
        },

        // Get status color classes for each status
        getStatusColor(status) {
            if (status === "Approved") return "text-success";
            if (status === "Rejected") return "text-error";
            if (status === "Rescinded") return "text-error";
            if (status === "Pending Withdrawal") return "text-pink";
            return "text-warning";
        },
    }
};
</script>

<style scoped>
.w-md-initial {
    @media (min-width: 767px) {
        width: unset !important
    }
}
</style>