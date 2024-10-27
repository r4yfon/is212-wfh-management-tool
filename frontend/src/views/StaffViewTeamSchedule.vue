<script>
import FullCalendar from '@fullcalendar/vue3';
import interactionPlugin from '@fullcalendar/interaction';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import { useMainStore } from '@/store.js';

export default {
  components: {
    FullCalendar,
  },
  data() {
    return {
      workColors: {
        'WFH - AM': '#F48BA9',
        'WFH - PM': '#FFB6C1',
        'WFH - Full': '#BA55D3',
        Office: '#86CBED',
      },
      showDialog: false,
      clickedDateString: null,
      clickedEventDetails: null,
      searchTerm: '',
      calendarOptions: {
        plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
        initialView: 'dayGridWeek',
        validRange: {
          start: new Date(new Date().getFullYear(), new Date().getMonth() - 2, new Date().getDate()).toISOString().split("T")[0],
          end: new Date(new Date().getFullYear(), new Date().getMonth() + 3, new Date().getDate()).toISOString().split("T")[0],
        },
        height: '400px',
        headerToolbar: {
          left: 'prev,next today',
          center: 'title',
          right: 'dayGridWeek,dayGridDay',
        },
        events: [],
        eventClick: this.handleEventClick,
      },
    };
  },
  computed: {
    user_store() {
      return useMainStore();
    },
    selectedTeam() {
      return this.user_store.user.department || null;
    },
    staff_id() {
      return this.user_store.user.staff_id || null;
    },
    filteredStaffList() {
      return this.filterStaffDetails(this.clickedEventDetails.staffDetails || []);
    }
  },
  methods: {
    handleEventClick(arg) {
      const d = new Date(arg.event.start);
      const year = d.getFullYear();
      const month = String(d.getMonth() + 1).padStart(2, '0');
      const day = String(d.getDate()).padStart(2, '0');
      this.clickedDateString = `${year}-${month}-${day}`;
      this.clickedEventDetails = arg.event.extendedProps;

      const hasPeople =
        this.clickedEventDetails.amCount > 0 ||
        this.clickedEventDetails.pmCount > 0 ||
        this.clickedEventDetails.fullCount > 0 ||
        this.clickedEventDetails.inOfficeCount > 0;

      this.showDialog = hasPeople;
    },
    async fetchAndDisplayData() {
      try {
        const employeeResponse = await fetch('http://127.0.0.1:5000/employee/get_all_employees_by_dept');
        if (!employeeResponse.ok) throw new Error('Failed to fetch employee details');
        const employeeData = await employeeResponse.json();

        const scheduleResponse = await fetch(`http://127.0.0.1:5100/s_get_team_schedule/${this.staff_id}`);
        if (!scheduleResponse.ok) throw new Error('Failed to fetch schedule');
        const scheduleData = await scheduleResponse.json();

        this.displayTeamSchedule(scheduleData, employeeData.data);
      } catch (error) {
        console.error(error);
      }
    },
    displayTeamSchedule(teamSchedule, employeesByDept) {
      const formattedEvents = [];
      const team = this.selectedTeam;

      for (const date in teamSchedule[team]) {
        if (date !== 'num_employee') {
          const departmentStrength = teamSchedule[team].num_employee;
          const AMCount = teamSchedule[team][date].AM.length;
          const PMCount = teamSchedule[team][date].PM.length;
          console.log(teamSchedule[team][date].PM);
          const FullCount = teamSchedule[team][date].Full.length;
          const inOfficeCount = departmentStrength - AMCount - PMCount - FullCount;

          const inOfficeStaffDetails = Object.values(employeesByDept[team] || {})
            .map(staff => ({
              name: staff.staff_name,
              staff_id: staff.staff_id,
              role: staff.role
            }))
            .filter(staff =>
              !teamSchedule[team][date].AM.some(s => s.staff_id === staff.staff_id) &&
              !teamSchedule[team][date].PM.some(s => s.staff_id === staff.staff_id) &&
              !teamSchedule[team][date].Full.some(s => s.staff_id === staff.staff_id)
            );


          formattedEvents.push(
            {
              title: `WFH - AM: ${AMCount} people`,
              start: date,
              color: this.workColors['WFH - AM'],
              extendedProps: {
                amCount: AMCount,
                staffDetails: teamSchedule[team][date].AM,
              },
            },
            {
              title: `WFH - PM: ${PMCount} people`,
              start: date,
              color: this.workColors['WFH - PM'],
              extendedProps: {
                pmCount: PMCount,
                staffDetails: teamSchedule[team][date].PM,
              },
            },
            {
              title: `WFH - Full: ${FullCount} people`,
              start: date,
              color: this.workColors['WFH - Full'],
              extendedProps: {
                fullCount: FullCount,
                staffDetails: teamSchedule[team][date].Full,
              },
            },
            {
              title: `Office: ${inOfficeCount} people`,
              start: date,
              color: this.workColors.Office,
              extendedProps: {
                inOfficeCount,
                staffDetails: inOfficeStaffDetails,
              },
            }
          );
        }
      }

      this.calendarOptions.events = formattedEvents;
      console.log(this.calendarOptions.events)
    },



    filterStaffDetails(staffList) {
      return staffList.filter(staff =>
        staff.name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        staff.staff_id.toString().includes(this.searchTerm) ||
        staff.role.toLowerCase().includes(this.searchTerm.toLowerCase())
      );
    },
  },
  watch: {
    // searchTerm() {
    //   this.filteredAMStaffNames = this.filterStaffNames(this.clickedEventDetails?.staffNames || []);
    //   this.filteredPMStaffNames = this.filterStaffNames(this.clickedEventDetails?.pmStaffNames || []);
    //   this.filteredFullStaffNames = this.filterStaffNames(this.clickedEventDetails?.fullStaffNames || []);
    //   this.filteredInOfficeStaffNames = this.filterStaffNames(this.clickedEventDetails?.inOfficeStaffNames || []);
    // },
    showDialog(value) {
      if (!value) {
        this.searchTerm = ''; // Clear the search bar
      }
    },
    user_store: {
      handler() {
        this.fetchAndDisplayData(); // Refetch data if user data changes
      },
      deep: true
    }
  },
  mounted() {
    this.fetchAndDisplayData();
  }
};
</script>

<template>
  <div class="container-fluid d-flex mt-4">
    <aside class="p-3 d-none d-lg-block bg-primary-subtle me-4 rounded w-auto">
      <!-- Sidebar content goes here -->
      <DatePicker v-model="selectedDate" inline class="mb-4" :minDate="datePicker.start" :maxDate="datePicker.end" />
      <v-checkbox v-for="department in departments" :key="department" :value="department" :label="department"
        :color="this.departmentColors[department]" v-model="selectedDepartments" hide-details></v-checkbox>
    </aside>
    <section class="flex-grow-1">
      <FullCalendar :options="calendarOptions" />
      <v-dialog v-model="showDialog" max-width="70%">
        <v-card>
          <v-card-title>Staff</v-card-title>
          <v-card-text>
            <div class="search-container">
              <v-text-field v-model="searchTerm" label="Search" outlined dense hide-details></v-text-field>
            </div>
            <div class="staff-table-container">
              <v-table class="staff-table">
                <thead>
                  <tr>
                    <th>Staff Name</th>
                    <th>Staff ID</th>
                    <th>Role</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(staff, index) in filteredStaffList" :key="index">
                    <td>{{ staff.name }}</td>
                    <td>{{ staff.staff_id }}</td>
                    <td>{{ staff.role }}</td>
                  </tr>
                </tbody>
              </v-table>
            </div>
          </v-card-text>
        </v-card>
      </v-dialog>
    </section>
  </div>
</template>

<style>
.fc-h-event .fc-event-title {
  white-space: normal;
}

.fc-event-main {
  padding: 0.25rem;
}

.search-container {
  position: sticky;
  top: 0;
  background-color: white;
  z-index: 1;
  padding-bottom: 10px;
}

.staff-table-container {
  max-height: 300px;
  overflow-y: auto;
  border-bottom: 2px solid #ddd;
}

.staff-table thead th {
  position: sticky;
  top: 0;
  background-color: #f9f9f9;
  z-index: 2;
  /* Ensure it's above the content */
  border-bottom: 2px solid #ddd;
  padding: 10px;
  text-align: left;
}

.staff-table tbody td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}
</style>