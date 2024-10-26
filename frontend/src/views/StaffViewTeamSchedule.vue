<script>
import FullCalendar from '@fullcalendar/vue3';
import interactionPlugin from '@fullcalendar/interaction';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';

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
        Office: '#86CBED'
      },
      selectedTeam: 'Engineering', // Assumes the user is from the Engineering department
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
    async fetchAndDisplayData(staff_id) {
      try {
        const employeeResponse = await fetch('http://127.0.0.1:5000/employee/get_all_employees_by_dept');
        if (!employeeResponse.ok) throw new Error('Failed to fetch employee details');
        const employeeData = await employeeResponse.json();

        const scheduleResponse = await fetch(`http://127.0.0.1:5100/s_get_team_schedule/${staff_id}`);
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
          const FullCount = teamSchedule[team][date].Full.length;
          const inOfficeCount = departmentStrength - AMCount - PMCount - FullCount;

          const inOfficeStaffNames = Object.values(employeesByDept[team] || {})
            .map(staff => staff.staff_name)
            .filter(staffName =>
              !teamSchedule[team][date].AM.some(s => s.name === staffName) &&
              !teamSchedule[team][date].PM.some(s => s.name === staffName) &&
              !teamSchedule[team][date].Full.some(s => s.name === staffName)
            );

          formattedEvents.push(
            {
              title: `WFH - AM: ${AMCount} people`,
              start: date,
              color: this.workColors['WFH - AM'],
              extendedProps: {
                amCount: AMCount,
                staffNames: teamSchedule[team][date].AM.map(staff => staff.name),
              },
            },
            {
              title: `WFH - PM: ${PMCount} people`,
              start: date,
              color: this.workColors['WFH - PM'],
              extendedProps: {
                pmCount: PMCount,
                pmStaffNames: teamSchedule[team][date].PM.map(staff => staff.name),
              },
            },
            {
              title: `WFH - Full: ${FullCount} people`,
              start: date,
              color: this.workColors['WFH - Full'],
              extendedProps: {
                fullCount: FullCount,
                fullStaffNames: teamSchedule[team][date].Full.map(staff => staff.name),
              },
            },
            {
              title: `Office: ${inOfficeCount} people`,
              start: date,
              color: this.workColors.Office,
              extendedProps: {
                inOfficeCount,
                inOfficeStaffNames: inOfficeStaffNames,
              },
            }
          );
        }
      }

      this.calendarOptions.events = formattedEvents;
    },
    // Methods to filter staff names based on the search term
    filterStaffNames(staffList) {
      return staffList.filter(name =>
        name.toLowerCase().includes(this.searchTerm.toLowerCase())
      );
    },
  },
  watch: {
    searchTerm() {
      // Trigger reactivity for the filtered lists by watching searchTerm
      this.filteredAMStaffNames = this.filterStaffNames(this.clickedEventDetails?.staffNames || []);
      this.filteredPMStaffNames = this.filterStaffNames(this.clickedEventDetails?.pmStaffNames || []);
      this.filteredFullStaffNames = this.filterStaffNames(this.clickedEventDetails?.fullStaffNames || []);
      this.filteredInOfficeStaffNames = this.filterStaffNames(this.clickedEventDetails?.inOfficeStaffNames || []);
    }
  },
  mounted() {
    const staff_id = 150488; // Assume Jacob Tan Staff_Id
    this.fetchAndDisplayData(staff_id);
  }
};
</script>

<template>
  <div class="container-fluid d-flex mt-4">
    <section class="flex-grow-1">
      <FullCalendar :options="calendarOptions" />
      <v-dialog v-model="showDialog" max-width="70%">
        <v-card>
          <v-card-title>Staff</v-card-title>
          <v-card-text>
            <!-- Search box to search for staff names -->
            <div class="search-container">
              <v-text-field
                v-model="searchTerm"
                label="Search Staff Names"
                outlined
                dense
                hide-details
              ></v-text-field>
            </div>
            <div class="names-list">
              <div v-if="clickedEventDetails.amCount">
                <ul>
                  <li v-for="(name, index) in filterStaffNames(clickedEventDetails.staffNames || [])" :key="index">{{ name }}</li>
                </ul>
              </div>
              <div v-if="clickedEventDetails.pmCount">
                <ul>
                  <li v-for="(name, index) in filterStaffNames(clickedEventDetails.pmStaffNames || [])" :key="index">{{ name }}</li>
                </ul>
              </div>
              <div v-if="clickedEventDetails.fullCount">
                <ul>
                  <li v-for="(name, index) in filterStaffNames(clickedEventDetails.fullStaffNames || [])" :key="index">{{ name }}</li>
                </ul>
              </div>
              <div v-if="clickedEventDetails.inOfficeCount">
                <ul>
                  <li v-for="(name, index) in filterStaffNames(clickedEventDetails.inOfficeStaffNames || [])" :key="index">{{ name }}</li>
                </ul>
              </div>
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

.names-list {
  max-height: 200px;
  overflow-y: auto;
  padding-top: 10px;
}
</style>
