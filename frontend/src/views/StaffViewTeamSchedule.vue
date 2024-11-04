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
        // { 
        //   headerName: "WFH Status", 
        //   field: "wfhStatus", 
        //   cellStyle: params => {
        //     switch(params.value) {
        //       case 'WFH - AM': return { color: '#F48BA9' };
        //       case 'WFH - PM': return { color: '#FFB6C1' };
        //       case 'WFH - Full': return { color: '#BA55D3' };
        //       default: return { color: 'green' }; // In Office
        //     }
        //   },
        //   suppressMovable: true, 
        //   filter: true
        // }, 
        { 
          headerName: "WFH Status", 
          field: "wfhStatus", 
          cellStyle: params => params.value === 'In Office' ? { color: 'green' } : { color: 'red' },
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
      
      clickedDateString: null,
      clickedEventDepartment: null,

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

      const teamMembers = Object.values(employeesByDept[team]).filter(member => member.reporting_manager === this.user_store.user.reporting_manager);
      console.log(teamMembers);
      for (const date in teamSchedule[team]) {
        if (date !== 'num_employee') {
          const departmentStrength = teamSchedule[team].num_employee;
          const AMCount = teamSchedule[team][date].AM.length;
          const PMCount = teamSchedule[team][date].PM.length;
          const FullCount = teamSchedule[team][date].Full.length;

          // Gather all staff IDs working during AM, PM, and Full shifts
          const amStaffIds = new Set(teamSchedule[team][date].AM.map(s => s.staff_id)); 
          const pmStaffIds = new Set(teamSchedule[team][date].PM.map(s => s.staff_id));
          const fullStaffIds = new Set(teamSchedule[team][date].Full.map(s => s.staff_id));

          // Combine all unique staff IDs from AM, PM, and Full shifts and calculate inOfficeStaff
          const allWfhStaffIds = new Set([...amStaffIds, ...pmStaffIds, ...fullStaffIds]);
          const inOfficeCount = departmentStrength - allWfhStaffIds.size;
        
          const inOfficeStaffDetails = teamMembers
            .map(staff => ({
              name: staff.staff_name,
              staff_id: staff.staff_id,
              role: staff.role, 
              wfhStatus: "In Office"
            }))
            .filter(staff => {
              const isWfh = allWfhStaffIds.has(staff.staff_id);
              // console.log(`Checking Staff ID: ${staff.staff_id}, Is Working: ${isWorking}`);
              return !isWfh;
            }
              
            );
            // console.log("In Office Staff Count:", inOfficeStaffDetails.length);
          
          const wfhDetails = ['AM', 'PM', "Full"].flatMap(shift =>
            teamSchedule[team][date][shift].map(staff =>  ({
              name: staff.name,
              staff_id: staff.staff_id,
              role: staff.role, 
              wfhStatus: `WFH - ${shift}`
            }))
          );

          const staffDetails = [...wfhDetails, ...inOfficeStaffDetails];

          formattedEvents.push(
            {
              title: `WFH - AM: ${AMCount} people`,
              start: date,
              color: this.workColors['WFH - AM'],
              extendedProps: {
                amCount: AMCount,
                // staffDetails: teamSchedule[team][date].AM,
                staffDetails: staffDetails.filter(staff => staff.wfhStatus === 'WFH - AM')
              },
            },
            {
              title: `WFH - PM: ${PMCount} people`,
              start: date,
              color: this.workColors['WFH - PM'],
              extendedProps: {
                pmCount: PMCount,
                // staffDetails: teamSchedule[team][date].PM,
                staffDetails: staffDetails.filter(staff => staff.wfhStatus === 'WFH - PM')
              },
            },
            {
              title: `WFH - Full: ${FullCount} people`,
              start: date,
              color: this.workColors['WFH - Full'],
              extendedProps: {
                fullCount: FullCount,
                // staffDetails: teamSchedule[team][date].Full,
                staffDetails: staffDetails.filter(staff => staff.wfhStatus === 'WFH - Full')
              },
            },
            {
              title: `Office: ${inOfficeCount} people`,
              start: date,
              color: this.workColors.Office,
              extendedProps: {
                inOfficeCount: inOfficeCount,
                // staffDetails: inOfficeStaffDetails,
                staffDetails: staffDetails.filter(staff => staff.wfhStatus === 'In Office')
              },
            }
          );
        }
      }

      this.calendarOptions.events = formattedEvents;
      // console.log(this.calendarOptions.events)
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
          <v-card-text>
            <!-- <div class="search-container">
              <v-text-field v-model="searchTerm" label="Search" outlined dense hide-details></v-text-field>
            </div> -->
            <div class="staff-table-container">
              <AgGridVue  class="ag-theme-quartz" 
                :gridOptions="gridOptions"
                :rowData="filteredStaffList"
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
  max-height: 100%;
  overflow-y: auto;
}

.ag-theme-alpine {
  width: 100%;
  height: 100%;
}
</style>