<template>
  <div class="container-fluid d-flex mt-4">
    <aside class="p-3 d-none d-lg-block bg-primary-subtle me-4 rounded w-auto">
      <!-- Sidebar content goes here -->
      <DatePicker v-model="selectedDate" inline class="mb-4" :minDate="datePicker.start" :maxDate="datePicker.end" />
      <template v-if="role === 'director'">
        <!-- {{ managersIdAndNames }}
        {{ selectedManagers }} -->
        <v-checkbox v-for="(key, value) in managersIdAndNames" :key="key" :value="value" :label="key"
          v-model="selectedManagers" hide-details></v-checkbox>

      </template>

      <template v-else>
        <v-checkbox v-for="department in departments" :key="department" :value="department" :label="department"
          :color="this.departmentColors[department]" v-model="selectedDepartments" hide-details></v-checkbox>
      </template>
    </aside>

    <section class="flex-grow-1">
      <FullCalendar ref="fullCalendar" :options="calendarOptions" />

      <v-dialog v-model="showDialog" max-width="60%">
        <v-card>
          <v-card-title>{{ clickedDateString }}: {{ clickedEventDepartment }}</v-card-title>
          <v-card-text>
            <ag-grid-vue :rowData="rowData" :defaultColDef="agGridOptions.defaultColDef"
              :columnDefs="agGridOptions.columnHeaders" style="height: 100%;" class="ag-theme-quartz"
              :domLayout="agGridOptions.domLayout" :autoSizeStrategy="agGridOptions.autoSizeStrategy"></ag-grid-vue>

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
import "ag-grid-community/styles/ag-grid.css"; // Mandatory CSS required by the Data Grid
import "ag-grid-community/styles/ag-theme-quartz.css"; // Optional Theme applied to the Data Grid
import { AgGridVue } from "ag-grid-vue3"; // Vue Data Grid Component
import { useMainStore } from '@/store';

export default {
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

      departmentColors: {
        CEO: '#FFB3BA',
        Consultancy: '#FFDFBA',
        Engineering: '#FFFFBA',
        Finance: '#BAFFC9',
        IT: '#BAE1FF',
        HR: '#D7BAFF',
        Sales: '#FFB3E6',
        Solutioning: '#A3E4D7'
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
              return params.value === 'In Office' ? { color: 'green' } : { color: 'red' };
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

      // HRView
      departments: [],
      employeesByDepartment: {},
      selectedDepartments: [],
      unformattedSchedule: {},
      formattedEventsByDepartment: {},
      orgSchedule: {},
      scheduledData: {},

      // directorView
      managersIdAndNames: {},
      managersUnderDirector: [],
      selectedManagers: [],
      formattedEventsByManager: {},
    };
  },

  mounted() {
    this.userStore = useMainStore();
    this.getEmployeeDetails();

    // to reflect the current date in datePicker when "today" button is clicked
    const todayButton = document.querySelector(".fc-today-button");
    todayButton.addEventListener("click", this.handleTodayClick);


    if (this.role === 'director') {
      // for HR and CEO
      if (this.userStore.user.position !== 'Director') {
        this.getOrgSchedule();
      } else {
        // for directors
        this.displayManagersInSidebar();
      }
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
      this.showDialog = true;
      this.clickedEventDepartment = arg.event.extendedProps.department;
      if (this.role === 'director') {
        if (this.userStore.user.position !== 'Director') {
          this.rowData = Object.values(this.employeesByDepartment[this.clickedEventDepartment]);
        } else {
          this.rowData = Object.values(this.employeesByDepartment[this.clickedEventDepartment]).filter(employee => employee.reporting_manager === this.reportingManagerId);
        }
      } else if (this.role === 'manager') {
        this.rowData = Object.values(this.employeesByDepartment[this.userStore.user.department]).filter(employee => employee.reporting_manager === this.userStore.user.staff_id);
      }
    },

    // to render content in the events in FullCalendar
    renderEventContent(arg) {
      const rate = Math.floor(arg.event.extendedProps.officeAttendanceRate);
      const rateClass = rate > 50 ? 'text-success-emphasis' : 'text-danger';
      if (this.role === 'director') {
        return {
          html: `
            ${arg.event.title}<br />
            Attendance rate in office: <span class="${rateClass}">${rate}%</span>
            `
        }
      } else {
        return {
          html: `
              ${arg.event.title}
            `
        }
      }
    },

    // get employees by department
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

    // FUNCTIONS USED BY DIRECTORVIEW
    displayManagersInSidebar() {
      fetch(`${url_paths.employee}/get_team/${this.userStore.user.staff_id}`)
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          data["managers_and_teams"].forEach(team => {
            this.managersIdAndNames[Number(team["manager_id"])] = this.employeesByDepartment[this.userStore.user.department][team["manager_id"]].staff_name;
          })
          this.selectedManagers = [...Object.keys(this.managersIdAndNames)];
        })
    },

    getDirectorSchedule() {
      // TODO: yubin's function
      fetch(`${url_paths.view_schedule}/o_get_org_schedule`)
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          let formatted_events = [];
          for (const manager in data) {
            const departmentStrength = data[manager]["num_employee"];
            for (const date in data[manager]) {
              if (date !== "num_employee") {
                const manpowerInOffice = departmentStrength - data[manager][date]["AM"].length - data[manager][date]["PM"].length - data[manager][date]["Full"].length;
                const officeAttendanceRate = Math.floor(manpowerInOffice / departmentStrength * 100);
                const event = {
                  title: `${manager}'s Team': ${manpowerInOffice} / ${departmentStrength} in office`,
                  start: date,
                  manager: manager,
                  manpowerInOffice: manpowerInOffice,
                  departmentStrength: departmentStrength,
                  officeAttendanceRate: officeAttendanceRate,
                  color: this.departmentColors[manager],
                  textColor: "#000000",
                };
                formatted_events.push(event);
              }
            }
            if (manager === "direct_subordinates") {
              this.formattedEventsByManager[this.userStore.user.staff_id] = formatted_events;
            } else {
              this.formattedEventsByManager[manager] = formatted_events;
            };
            formatted_events = [];
          }
        })
    },

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
                const manpowerInOffice = departmentStrength - data[department][date]["AM"].length - data[department][date]["PM"].length - data[department][date]["Full"].length;
                const officeAttendanceRate = Math.floor(manpowerInOffice / departmentStrength * 100);
                const event = {
                  title: `${department}: ${manpowerInOffice} / ${departmentStrength} in office`,
                  start: date,
                  department: department,
                  manpowerInOffice: manpowerInOffice,
                  departmentStrength: departmentStrength,
                  officeAttendanceRate: officeAttendanceRate,
                  color: this.departmentColors[department],
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

    // for the table in dialog for orgSchedule
    scheduleValueGetter(params) {
      const staff_id = params.data.staff_id;
      const isInArray = (array, id) => array.some(item => item.staff_id === id);

      if (isInArray(this.unformattedSchedule[this.clickedEventDepartment][this.clickedDateString].AM, staff_id)) {
        return 'WFH - AM';
      } else if (isInArray(this.unformattedSchedule[this.clickedEventDepartment][this.clickedDateString].PM, staff_id)) {
        return 'WFH - PM';
      } else if (isInArray(this.unformattedSchedule[this.clickedEventDepartment][this.clickedDateString].Full, staff_id)) {
        return 'WFH - Full';
      } else {
        return 'In Office';
      }
    },

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
                const manpowerInOffice = departmentStrength - data[department][date]["AM"].length - data[department][date]["PM"].length - data[department][date]["Full"].length;
                const officeAttendanceRate = Math.floor(manpowerInOffice / departmentStrength * 100);
                const manpowerAllocation = (Object.entries(data[department][date]));

                const eventYear = Number(date.slice(0, 4));
                const eventMonthIndex = Number(date.slice(5, 7)) - 1;
                const eventDate = Number(date.slice(8, 10));
                manpowerAllocation.forEach((workShift) => {
                  // console.log(workShift);
                  const event = {
                    title: `WFH - ${workShift[0]}: ${workShift[1].length} people`,
                    start: new Date(eventYear, eventMonthIndex, eventDate, workShiftsTimes[workShift[0]].start),
                    end: new Date(eventYear, eventMonthIndex, eventDate, workShiftsTimes[workShift[0]].end),
                    department: department,
                    manpowerInOffice: manpowerInOffice,
                    departmentStrength: departmentStrength,
                    officeAttendanceRate: officeAttendanceRate,
                    color: this.departmentColors[department],
                    textColor: "#000000",
                  };
                  // console.log(event)
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
                  color: this.departmentColors[department],
                  textColor: "#000000",
                }
                formatted_events.push(officeWorkers);
              }
              // formatted_events = [];

            }
          }
          this.calendarOptions.events = formatted_events;
        })
    },
  }
}
</script>

<style>
.fc-h-event .fc-event-title {
  white-space: normal;
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
</style>