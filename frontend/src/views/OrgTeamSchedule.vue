<template>
  <div class="container-fluid d-flex mt-4">
    <aside class="p-3 d-none d-lg-block bg-primary-subtle me-4 rounded w-auto">
      <!-- Sidebar content goes here -->
      <DatePicker v-model="selectedDate" inline class="mb-4" :minDate="datePicker.start" :maxDate="datePicker.end" />

      <template v-if="role === 'director'">
        <div class="fw-semibold">Managers under you</div>
        <v-checkbox v-for="(key, value, index) in managersIdAndNames" :key="key" :value="value" :label="key"
          :color="stylingColors['byManagers'][index]" v-model="selectedManagers" hide-details></v-checkbox>
      </template>

      <template v-else-if="role === 'organisation'">
        <div class="fw-semibold">Departments</div>
        <v-checkbox v-for="department in departments" :key="department" :value="department" :label="department"
          :color="this.stylingColors['byDepartments'][department]" v-model="selectedDepartments"
          hide-details></v-checkbox>
      </template>
    </aside>

    <section class="flex-grow-1">
      <v-btn class="mb-3" color="#37474F" @click="redirectToViewStaffRequests">View Approved Staff Requests</v-btn>
      <FullCalendar ref="fullCalendar" :options="calendarOptions" />

      <v-dialog v-model="showDialog" max-width="60%">
        <v-card>
          <v-card-title v-if="role === 'organisation'">
            {{ clickedDateString }}: {{ clickedEventDepartment }}
          </v-card-title>
          <v-card-title v-else-if="role === 'director'">
            {{ clickedDateString }}: {{ managersIdAndNames[clickedManagerId] }}'s team
          </v-card-title>
          <v-card-title v-else-if="role === 'manager'">
            {{ clickedDateString }}
          </v-card-title>
          <v-card-text>
            <ag-grid-vue :rowData="rowData" :defaultColDef="agGridOptions.defaultColDef"
              :columnDefs="agGridOptions.columnHeaders" style="height: 100%;" class="ag-theme-quartz"
              :domLayout="agGridOptions.domLayout" :autoSizeStrategy="agGridOptions.autoSizeStrategy">
            </ag-grid-vue>
          </v-card-text>
        </v-card>
      </v-dialog>
    </section>
  </div>
</template>

<script>
import FullCalendar from '@fullcalendar/vue3';
import interactionPlugin from '@fullcalendar/interaction';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import { url_paths } from '@/url_paths.js';
import DatePicker from 'primevue/datepicker';
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-quartz.css";
import { AgGridVue } from "ag-grid-vue3";
import { useMainStore } from '@/store';
import { useRouter } from 'vue-router';

export default {
  setup(){
    const router = useRouter();

    const redirectToViewStaffRequests = () => {
      router.push({ path: '/viewstaffrequests', query: { tab: 2 } });
    };

    return {
      redirectToViewStaffRequests,
    };
  },   
  props: {
    role: {
      type: String,
      Required: true,
    }
  },
  components: {
    FullCalendar, DatePicker, AgGridVue,
  },
  data() {
    return {
      calendarOptions: {
        plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
        initialView: 'dayGridWeek',
        validRange: {
          start: new Date(new Date().getFullYear(), new Date().getMonth() - 2, new Date().getDate()).toISOString().split('T')[0],
          end: new Date(new Date().getFullYear(), new Date().getMonth() + 3, new Date().getDate()).toISOString().split('T')[0],
        },
        eventContent: this.renderEventContent,
        height: 'auto',
        headerToolbar: {
          left: 'prev,next today',
          center: 'title',
          right: 'dayGridWeek,dayGridDay',
        },
        eventDisplay: 'block',
        eventTimeFormat: {
          hour: 'numeric',
          meridiem: true,
        },
        events: [],
        eventClick: this.handleEventClick,
      },

      userStore: null,

      // for calendar events, checkboxes
      stylingColors: {
        byDepartments: {
          CEO: '#FFB3BA',
          Consultancy: '#FFDFBA',
          Engineering: '#FFFFBA',
          Finance: '#BAFFC9',
          IT: '#BAE1FF',
          HR: '#D7BAFF',
          Sales: '#FFB3E6',
          Solutioning: '#A3E4D7'
        },
        byWorkShifts: {
          'AM': '#F48BA9',
          'PM': '#FFB6C1',
          'Full': '#BA55D3',
          Office: '#86CBED',
        },
        byManagers: [
          "#AEC6CF", "#FFB7B2", "#FFDAC1", "#E6E6FA", "#C3B1E1",
          "#B5EAD7", "#FFDFD3", "#FFC3A0", "#FFDDC1", "#B39EB5",
          "#FDFD96", "#CFCFC4", "#A1CAF1", "#E0BBE4", "#FFDFE5"
        ]
      },

      // datePicker
      datePicker: {
        start: new Date(new Date().getFullYear(), new Date().getMonth() - 2, new Date().getDate()),
        end: new Date(new Date().getFullYear(), new Date().getMonth() + 3, new Date().getDate()),
      },
      selectedDate: new Date(),

      // dialog
      showDialog: false,
      agGridOptions: {
        columnHeaders: [
          { headerName: "Staff Name", field: "staff_name", filter: true, suppressMovable: true },
          { headerName: "Staff ID", field: "staff_id", filter: true, suppressMovable: true },
          { headerName: "Role", field: "role", filter: true, suppressMovable: true },
          {
            headerName: "WFH Status", valueGetter: this.scheduleValueGetter, filter: true, suppressMovable: true, cellStyle: params => {
              return params.value[0] === 'In Office' ? { color: 'green' } : { color: 'red' };
            }
          }
        ],
        autoSizeStrategy: {
          type: "fitGridWidth",
          defaultMinWidth: 100,
        },
        defaultColDef: {
          resizable: false,
        },
        rowData: null,
        domLayout: 'autoHeight',
      },
      clickedDateString: null,
      clickedEventDepartment: null,

      unformattedSchedule: {},

      // HRView
      departments: [],
      employeesByDepartment: {},
      selectedDepartments: [],
      formattedEventsByDepartment: {},
      orgSchedule: {},
      scheduledData: {},

      // directorView
      managersIdAndNames: {},
      selectedManagers: [],
      formattedEventsByManager: {},
      clickedManagerId: null,
    };
  },

  mounted() {
    this.userStore = useMainStore();
    this.getEmployeeDetails();

    // to reset datePicker when "today" button is clicked
    const todayButton = document.querySelector(".fc-today-button");
    todayButton.addEventListener("click", this.handleTodayClick);

    if (this.role === 'organisation') {
      this.getOrgSchedule();
    } else if (this.role === 'director') {
      this.getDirectorSchedule();
    } else if (this.role === 'manager') {
      this.managerTeamSchedule();
    }
  },

  watch: {
    selectedDate: {
      handler(value) {
        this.$refs.fullCalendar.getApi().gotoDate(value);
      },
    },

    selectedDepartments: {
      handler(newDepartments) {
        this.calendarOptions.events = [];
        newDepartments.forEach(department => {
          this.calendarOptions.events.push(...this.formattedEventsByDepartment[department]);
        });
      },
      deep: true,
    },

    selectedManagers: {
      handler(newManagers) {
        this.calendarOptions.events = [];
        newManagers.forEach(manager => {
          this.calendarOptions.events.push(...this.formattedEventsByManager[manager]);
        });
      }
    }
  },

  methods: {
    // FUNCTIONS USED BY ALL VIEWS
    handleTodayClick() {
      this.selectedDate = new Date();
    },

    handleEventClick(arg) {
      const d = new Date(arg.event.start);
      const year = d.getFullYear();
      const month = String(d.getMonth() + 1).padStart(2, '0');
      const day = String(d.getDate()).padStart(2, '0');
      this.clickedDateString = `${year}-${month}-${day}`;

      if (this.role === 'organisation') {
        this.clickedEventDepartment = arg.event.extendedProps.department;
        this.rowData = Object.values(this.employeesByDepartment[this.clickedEventDepartment]);
        // console.log(this.rowData.length);
      } else if (this.role === 'director') {
        const managerDepartment = this.userStore.user.department;
        this.clickedManagerId = arg.event.extendedProps.managerId;
        this.rowData = Object.values(this.employeesByDepartment[managerDepartment]).filter(employee =>
          Number(employee.reporting_manager) === Number(this.clickedManagerId)
        );
      } else if (this.role === 'manager') {
        this.clickedEventDepartment = arg.event.extendedProps.department;
        this.rowData = Object.values(this.employeesByDepartment[this.clickedEventDepartment]).filter(employee => employee.reporting_manager === this.userStore.user.staff_id);
      }
      this.showDialog = true;
    },

    // to render content in the events in FullCalendar
    renderEventContent(arg) {
      const rate = Math.floor(arg.event.extendedProps.officeAttendanceRate);
      const rateClass = rate > 50 ? 'text-success-emphasis' : 'text-danger';
      if (this.role === 'organisation') {
        return {
          html: `
            ${arg.event.title}<br />
            In office: <span class="${rateClass}">${rate}%</span>
            `
        }
      } else if (this.role === 'director') {
        return {
          html: `
            ${arg.event.title}<br />
            In office: ${arg.event.extendedProps.manpowerInOffice} / ${arg.event.extendedProps.teamStrength} (<span class="${rateClass}">${rate}%</span>)
            `
        }
      }
      return {
        html: `
              ${arg.event.title}
            `
      }
    },

    // get all employees details
    getEmployeeDetails() {
      fetch(`${url_paths.employee}/get_all_employees_by_dept`)
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          this.employeesByDepartment = data.data;
        })
    },

    // for WFH status in ag-grid in dialog
    scheduleValueGetter(params) {
      const staff_id = params.data.staff_id;
      const isInArray = (array, id) => array.some(item => item.staff_id === id);

      let statuses = [];

      if (this.role === 'organisation' || this.role === 'manager') {
        if (isInArray(this.unformattedSchedule[this.clickedEventDepartment][this.clickedDateString]["AM"], staff_id)) {
          statuses.push('WFH - AM');
        } if (isInArray(this.unformattedSchedule[this.clickedEventDepartment][this.clickedDateString]["PM"], staff_id)) {
          statuses.push('WFH - PM');
        } if (isInArray(this.unformattedSchedule[this.clickedEventDepartment][this.clickedDateString]["Full"], staff_id)) {
          statuses.push('WFH - Full');
        } if (statuses.length === 0) {
          statuses.push('In Office');
        }
        return statuses;
      } else if (this.role === 'director') {
        if (isInArray(this.unformattedSchedule[this.clickedManagerId][this.clickedDateString].AM, staff_id)) {
          statuses.push('WFH - AM');
        } if (isInArray(this.unformattedSchedule[this.clickedManagerId][this.clickedDateString].PM, staff_id)) {
          statuses.push('WFH - PM');
        } if (isInArray(this.unformattedSchedule[this.clickedManagerId][this.clickedDateString].Full, staff_id)) {
          statuses.push('WFH - Full');
        } if (statuses.length === 0) {
          statuses.push('In Office');
        }
        return statuses;
      }
    },

    // --------
    // FUNCTIONS USED BY HRVIEW
    displayDepartments(orgSchedule) {
      this.departments = Object.keys(orgSchedule);
      this.selectedDepartments = [...this.departments];
    },

    getOrgSchedule() {
      fetch(`${url_paths.view_schedule}/o_get_org_schedule`)
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          this.unformattedSchedule = data;
          this.displayDepartments(data);

          let formatted_events = [];
          for (const department in data) {
            const departmentStrength = data[department]["num_employee"];
            for (const date in data[department]) {
              if (date !== "num_employee") {
                // Create a map to track unique employees by their staff_id
                const uniqueEmployees = new Map();

                // Helper function to add employees to the map
                const addUniqueEmployees = (shift) => {
                  data[department][date][shift].forEach(employee => {
                    uniqueEmployees.set(employee.staff_id, employee);
                  });
                };

                // Add employees from all shifts
                addUniqueEmployees("AM");
                addUniqueEmployees("PM");
                addUniqueEmployees("Full");

                // Calculate manpower in office
                const manpowerInOffice = departmentStrength - uniqueEmployees.size;
                const officeAttendanceRate = Math.floor(manpowerInOffice / departmentStrength * 100);
                const event = {
                  title: `${department}: ${manpowerInOffice} / ${departmentStrength}`,
                  start: date,
                  department: department,
                  manpowerInOffice: manpowerInOffice,
                  departmentStrength: departmentStrength,
                  officeAttendanceRate: officeAttendanceRate,
                  color: this.stylingColors['byDepartments'][department],
                  textColor: "#000000",
                };
                formatted_events.push(event);
              }
            }
            this.formattedEventsByDepartment[department] = formatted_events;
            formatted_events = [];
          }
        })
    },

    // --------
    // FUNCTIONS USED BY DIRECTORVIEW
    displayManagersInSidebar(directorSchedule) {
      const managersIds = Object.keys(directorSchedule);
      for (const managerId of managersIds) {
        if (managerId === this.userStore.user.staff_id) {
          this.managersIdAndNames[Number(managerId)] = "Own team"
        } else {
          this.managersIdAndNames[Number(managerId)] = this.employeesByDepartment[this.userStore.user.department][managerId].staff_name;
        }
      }
      this.selectedManagers = [...managersIds];
    },

    getDirectorSchedule() {
      fetch(`${url_paths.view_schedule}/m_get_team_schedule/${this.userStore.user.staff_id}`)
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          this.unformattedSchedule = data;
          this.displayManagersInSidebar(data);

          let formatted_events = [];
          let colorIndex = 0;
          for (const managerId in data) {
            const teamStrength = data[managerId]["num_employee"];
            for (const date in data[managerId]) {
              if (date !== "num_employee") {
                // Create a map to track unique employees by their staff_id
                const uniqueEmployees = new Map();

                // Helper function to add employees to the map
                const addUniqueEmployees = (shift) => {
                  data[managerId][date][shift].forEach(employee => {
                    uniqueEmployees.set(employee.staff_id, employee);
                  });
                };

                // Add employees from all shifts
                addUniqueEmployees("AM");
                addUniqueEmployees("PM");
                addUniqueEmployees("Full");
                const manpowerInOffice = teamStrength - uniqueEmployees.size;
                const officeAttendanceRate = Math.floor(manpowerInOffice / teamStrength * 100);
                const managerName = this.managersIdAndNames[managerId];
                const event = {
                  title: `${managerName}'s Team`,
                  start: date,
                  managerId: managerId,
                  manpowerInOffice: manpowerInOffice,
                  teamStrength: teamStrength,
                  officeAttendanceRate: officeAttendanceRate,
                  color: this.stylingColors['byManagers'][colorIndex],
                  textColor: "#000000",
                };
                formatted_events.push(event);
              }
            }
            colorIndex += 1;
            this.formattedEventsByManager[managerId] = formatted_events;
            formatted_events = [];
          }
        })
    },

    // --------
    // FUNCTIONS FOR MANAGERVIEW
    managerTeamSchedule() {
      const workShiftsTimes = {
        AM: { start: 9, end: 13 },
        PM: { start: 14, end: 18 },
        Full: { start: 9, end: 18 },
      };

      fetch(`${url_paths.view_schedule}/m_get_team_schedule/${this.userStore.user.staff_id}`)
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          this.unformattedSchedule = data;

          let formatted_events = [];
          for (const department in data) {
            const departmentStrength = data[department]["num_employee"];
            for (const date in data[department]) {
              if (date !== "num_employee") {
                // Create a map to track unique employees by their staff_id
                const uniqueEmployees = new Map();

                // Helper function to add employees to the map
                const addUniqueEmployees = (shift) => {
                  data[department][date][shift].forEach(employee => {
                    uniqueEmployees.set(employee.staff_id, employee);
                  });
                };

                // Add employees from all shifts
                addUniqueEmployees("AM");
                addUniqueEmployees("PM");
                addUniqueEmployees("Full");
                const manpowerInOffice = departmentStrength - uniqueEmployees.size;
                const officeAttendanceRate = Math.floor(manpowerInOffice / departmentStrength * 100);
                const manpowerAllocation = (Object.entries(data[department][date]));

                const eventYear = Number(date.slice(0, 4));
                const eventMonthIndex = Number(date.slice(5, 7)) - 1;
                const eventDate = Number(date.slice(8, 10));
                manpowerAllocation.forEach((workShift) => {
                  const event = {
                    title: `WFH - ${workShift[0]}: ${workShift[1].length} people`,
                    start: new Date(eventYear, eventMonthIndex, eventDate, workShiftsTimes[workShift[0]].start),
                    end: new Date(eventYear, eventMonthIndex, eventDate, workShiftsTimes[workShift[0]].end),
                    department: department,
                    manpowerInOffice: manpowerInOffice,
                    departmentStrength: departmentStrength,
                    officeAttendanceRate: officeAttendanceRate,
                    color: this.stylingColors['byWorkShifts'][workShift[0]],
                    textColor: "#ffffff",
                  };
                  formatted_events.push(event);
                });
                const officeWorkers = {
                  title: `Office: ${manpowerInOffice} people`,
                  start: new Date(eventYear, eventMonthIndex, eventDate, workShiftsTimes.Full.start),
                  end: new Date(eventYear, eventMonthIndex, eventDate, workShiftsTimes.Full.end),
                  department: department,
                  manpowerInOffice: manpowerInOffice,
                  departmentStrength: departmentStrength,
                  officeAttendanceRate: officeAttendanceRate,
                  color: this.stylingColors['byWorkShifts']['Office'],
                  textColor: "#ffffff",
                }
                formatted_events.push(officeWorkers);
              }
            }
          }
          this.calendarOptions.events = formatted_events;
        })
    },
  }
}
</script>

<style>
.fc-h-event {
  white-space: normal;
  overflow: hidden;
}

.fc-event-main {
  padding: 0.25rem;
  margin: 1px;
  cursor: pointer;

  &:hover {
    border: 1px solid rgba(0, 0, 0, 0.4);
    border-radius: 3px;
    margin: 0;
  }
}

.fc-icon {
  display: flex;
}

.fc-col-header-cell-cushion {
  text-decoration: none;
  color: black;
}

.v-card-title {
  position: sticky;
  top: 0;
  background-color: white;
  z-index: 1000;
}
</style>