<template>
  <div class="container-fluid d-flex mt-4">
    <aside class="p-3 d-none d-lg-block bg-primary-subtle me-4 rounded w-auto">
      <!-- Sidebar content goes here -->
      <DatePicker v-model="selectedDate" inline class="mb-4" :minDate="datePicker.start" :maxDate="datePicker.end" />
      <v-checkbox v-for="department in departments" :key="department" :value="department" :label="department"
        :color="this.departmentColors[department]" v-model="selectedDepartments" hide-details></v-checkbox>
    </aside>

    <section class="flex-grow-1">
      <FullCalendar ref="fullCalendar" :options="calendarOptions" />

      <v-dialog v-model="showDialog" max-width="60%">
        <v-card>
          <v-card-title>{{ clickedDateString }}: {{ clickedEventDepartment }}</v-card-title>
          <v-card-text>
            <ag-grid-vue :rowData="Object.values(employeesByDepartment[clickedEventDepartment])"
              :defaultColDef="agGridOptions.defaultColDef" :columnDefs="agGridOptions.columnHeaders"
              style="height: 800px" class="ag-theme-quartz"
              :autoSizeStrategy="agGridOptions.autoSizeStrategy"></ag-grid-vue>

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
    FullCalendar, DatePicker, AgGridVue
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

      datePicker: {
        start: new Date(new Date().getFullYear(), new Date().getMonth() - 2, new Date().getDate()),
        end: new Date(new Date().getFullYear(), new Date().getMonth() + 3, new Date().getDate()),
      },

      agGridOptions: {
        columnHeaders: [
          { headerName: "Staff Name", field: "staff_name", filter: true },
          { headerName: "Staff ID", field: "staff_id", filter: true },
          { headerName: "Role", field: "role", filter: true },
          {
            headerName: "WFH Status", valueGetter: this.scheduleValueGetter, filter: true, cellStyle: params => {
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
        }
      },

      selectedDate: new Date(),
      showDialog: false,
      departments: [],
      employeesByDepartment: {},
      selectedDepartments: [],
      formattedEvents: {},
      orgSchedule: {},
      unformattedSchedule: {},
      scheduledData: {},
      clickedDateString: null,
      clickedEventDepartment: null,
    };
  },

  mounted() {
    this.userStore = useMainStore();
    this.getEmployeeDetails();
    if (this.role === 'director') {
      this.getOrgSchedule();
    } else if (this.role === 'manager') {
      this.managerTeamSchedule();
    }
  },

  watch: {
    selectedDepartments: {
      handler(newDepartments) {
        this.calendarOptions.events = [];
        newDepartments.forEach(department => {
          this.calendarOptions.events.push(...this.formattedEvents[department]);
        });
      },
      deep: true,
    },

    selectedDate: {
      handler(value) {
        this.$refs.fullCalendar.getApi().gotoDate(value);
      },
    }
  },

  methods: {
    displayDepartments(orgSchedule) {
      this.departments = Object.keys(orgSchedule);
      this.selectedDepartments = [...this.departments];
    },

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
            this.formattedEvents[department] = formatted_events;
            formatted_events = [];
          }
        })
    },

    // for the table in dialog for orgSchedule
    scheduleValueGetter(params) {
      const staff_id = params.data.staff_id;
      // console.log(this.orgSchedule[this.clickedEventDepartment][this.clickedDateString]);

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

    handleEventClick(arg) {
      const d = new Date(arg.event.start);
      const year = d.getFullYear();
      const month = String(d.getMonth() + 1).padStart(2, '0');
      const day = String(d.getDate()).padStart(2, '0');
      this.clickedDateString = `${year}-${month}-${day}`;
      this.showDialog = true;
      this.clickedEventDepartment = arg.event.extendedProps.department;
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