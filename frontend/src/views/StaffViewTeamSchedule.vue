<script>
import FullCalendar from '@fullcalendar/vue3';
import interactionPlugin from '@fullcalendar/interaction';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import { useMainStore } from '@/store.js';
import DatePicker from 'primevue/datepicker';
import { url_paths } from '@/url_paths';
import { AgGridVue } from "ag-grid-vue3";

export default {
  components: {
    FullCalendar, DatePicker, AgGridVue
  },
  data() {
    return {
      workColors: {
        'WFH - AM': '#F48BA9',
        'WFH - PM': '#FFB6C1',
        'WFH - Full': '#BA55D3',
        Office: '#86CBED',
      },
      clickedDateString: null,
      clickedEventDetails: null,
      // searchTerm: '',
      columnDefs: [
        { headerName: "Staff Name", field: "name", suppressMovable: true, filter: true },
        { headerName: "Staff ID", field: "staff_id", suppressMovable: true, filter: true },
        { headerName: "Role", field: "role", suppressMovable: true, filter: true },
        {
          headerName: "WFH Status",
          field: "wfhStatus",
          cellStyle: params => {
            switch (params.value) {
              case 'WFH - AM': return { color: 'red' };
              case 'WFH - PM': return { color: 'red' };
              case 'WFH - Full': return { color: 'red' };
              default: return { color: 'green' }; // In Office
            }
          },
          suppressMovable: true,
          filter: true
        },
      ],
      gridOptions: {
        defaultColDef: {
          resizable: false,
        },
        domLayout: 'autoHeight',
        autoSizeStrategy: {
          type: "fitGridWidth",
          defaultMinWidth: 100,
        },

      },
      showDialog: false,
      clickedEventDepartment: null,

      calendarOptions: {
        plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
        initialView: 'dayGridWeek',
        validRange: {
          start: new Date(new Date().getFullYear(), new Date().getMonth() - 2, new Date().getDate()).toISOString().split("T")[0],
          end: new Date(new Date().getFullYear(), new Date().getMonth() + 3, new Date().getDate()).toISOString().split("T")[0],
        },
        height: 'auto',
        headerToolbar: {
          left: 'prev,next today',
          center: 'title',
          right: 'dayGridWeek,dayGridDay',
        },
        events: [],
        eventClick: this.handleEventClick,
      },
      selectedDate: new Date(),
      datePicker: {
        start: new Date(new Date().getFullYear(), new Date().getMonth() - 2, new Date().getDate()),
        end: new Date(new Date().getFullYear(), new Date().getMonth() + 3, new Date().getDate()),
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

      // console.log(hasPeople)

      this.showDialog = hasPeople;

    },

    async fetchAndDisplayData() {
      try {
        const employeeResponse = await fetch(`${url_paths.employee}/get_all_employees_by_dept`);
        if (!employeeResponse.ok) throw new Error('Failed to fetch employee details');
        const employeeData = await employeeResponse.json();

        const scheduleResponse = await fetch(`${url_paths.view_schedule}/s_get_team_schedule/${this.staff_id}`);
        if (!scheduleResponse.ok) throw new Error('Failed to fetch schedule');
        const scheduleData = await scheduleResponse.json();

        // console.log(employeeData.data)
        this.displayTeamSchedule(scheduleData, employeeData.data);
      } catch (error) {
        console.error(error);
      }
    },
    displayTeamSchedule(teamSchedule, employeesByDept) {
      const formattedEvents = [];
      const team = this.selectedTeam;

      const teamMembers = Object.values(employeesByDept[team])
        .filter(member => member.reporting_manager === this.user_store.user.reporting_manager && member.staff_id !== this.user_store.user.staff_id);

      for (const date in teamSchedule[team]) {
        const departmentStrength = teamSchedule[team].num_employee - 1;
        if (date !== 'num_employee') {
          const AMArray = teamSchedule[team][date].AM.filter(member => member.reporting_manager === this.user_store.user.reporting_manager);
          AMArray.map(staff => staff.wfhStatus = 'WFH - AM');
          const PMArray = teamSchedule[team][date].PM.filter(member => member.reporting_manager === this.user_store.user.reporting_manager);
          PMArray.map(staff => staff.wfhStatus = 'WFH - PM');
          const FullArray = teamSchedule[team][date].Full.filter(member => member.reporting_manager === this.user_store.user.reporting_manager);
          FullArray.map(staff => staff.wfhStatus = 'WFH - Full');
          const AMCount = AMArray.length;
          const PMCount = PMArray.length;
          const FullCount = FullArray.length;
          const inOfficeCount = departmentStrength - AMCount - PMCount - FullCount;


          const inOfficeStaffDetails = teamMembers
            .map(staff => ({
              name: staff.staff_name,
              staff_id: staff.staff_id,
              role: staff.role,
              wfhStatus: "In Office"
            }))
            .filter(staff => {
              const amStaff = teamSchedule[team][date].AM.map(s => s.staff_id);
              const pmStaff = teamSchedule[team][date].PM.map(s => s.staff_id);
              const fullStaff = teamSchedule[team][date].Full.map(s => s.staff_id);

              return !amStaff.includes(staff.staff_id) &&
                !pmStaff.includes(staff.staff_id) &&
                !fullStaff.includes(staff.staff_id);
            });

          formattedEvents.push(
            {
              title: `WFH - AM: ${AMCount} people`,
              start: date,
              color: this.workColors['WFH - AM'],
              extendedProps: {
                amCount: AMCount,
                staffDetails: AMArray,
              },
            },
            {
              title: `WFH - PM: ${PMCount} people`,
              start: date,
              color: this.workColors['WFH - PM'],
              extendedProps: {
                pmCount: PMCount,
                staffDetails: PMArray,
              },
            },
            {
              title: `WFH - Full: ${FullCount} people`,
              start: date,
              color: this.workColors['WFH - Full'],
              extendedProps: {
                fullCount: FullCount,
                staffDetails: FullArray,
              },
            },
            {
              title: `Office: ${inOfficeCount} people`,
              start: date,
              color: this.workColors.Office,
              extendedProps: {
                inOfficeCount: inOfficeCount,
                // staffDetails: inOfficeStaffDetails,
                staffDetails: inOfficeStaffDetails.filter(staff => staff.wfhStatus === 'In Office')
              },
            }
          );
        }
      }

      this.calendarOptions.events = formattedEvents;
    },

    filterStaffDetails() {
      // return staffList.filter(staff =>
      //   staff.name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
      //   staff.staff_id.toString().includes(this.searchTerm) ||
      //   staff.role.toLowerCase().includes(this.searchTerm.toLowerCase())
      // );
      return this.clickedEventDetails?.staffDetails || [];
    },
  },
  watch: {
    // searchTerm() {
    //   this.filteredAMStaffNames = this.filterStaffNames(this.clickedEventDetails?.staffNames || []);
    //   this.filteredPMStaffNames = this.filterStaffNames(this.clickedEventDetails?.pmStaffNames || []);
    //   this.filteredFullStaffNames = this.filterStaffNames(this.clickedEventDetails?.fullStaffNames || []);
    //   this.filteredInOfficeStaffNames = this.filterStaffNames(this.clickedEventDetails?.inOfficeStaffNames || []);
    // },
    // showDialog(value) {
    //   if (!value) {
    //     this.searchTerm = '';
    //   }
    // },
    user_store: {
      handler() {
        this.fetchAndDisplayData();
      },
      deep: true
    },

    selectedDate: {
      handler(value) {
        this.$refs.fullCalendar.getApi().gotoDate(value);
      },
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
    </aside>
    <section class="flex-grow-1">
      <FullCalendar ref="fullCalendar" :options="calendarOptions" />
      <v-dialog v-model="showDialog" max-width="70%">
        <v-card>
          <v-card-title>{{ clickedDateString }}</v-card-title>
          <v-card-text>
            <!-- <div class="search-container">
              <v-text-field v-model="searchTerm" label="Search" outlined dense hide-details></v-text-field>
            </div> -->
            <div class="staff-table-container">
              <AgGridVue class="ag-theme-quartz" :gridOptions="gridOptions" :rowData="filteredStaffList"
                :columnDefs="columnDefs">
              </AgGridVue>
            </div>
          </v-card-text>
        </v-card>
      </v-dialog>
    </section>
  </div>
</template>

<style>
.search-container {
  position: sticky;
  top: 0;
  background-color: white;
  z-index: 1;
  padding-bottom: 10px;
}

.staff-table-container {
  max-height: 100%;
  overflow-y: auto;
}

.ag-theme-alpine {
  width: 100%;
  height: 100%;
}
</style>