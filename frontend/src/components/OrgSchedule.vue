<template>
  <div class="container-fluid d-flex mt-4">
    <aside class="p-3 d-none d-lg-block bg-primary-subtle me-4 rounded w-auto" v-if="showSidebar">
      <!-- Sidebar content goes here -->
      <DatePicker v-model="selectedDate" inline class="mb-4" :minDate="datePicker.start" :maxDate="datePicker.end" />
      <v-checkbox v-for="department in departments" :key="department" :value="department" :label="department"
        :color="this.departmentColors[department]" v-model="selectedDepartments" hide-details></v-checkbox>
    </aside>
    <section class="flex-grow-1">
      <!-- <button @click="toggleSidebar" class="btn btn-outline-primary">Toggle Sidebar</button> -->
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

export default {
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
        eventTimeFormat: {
          hour: 'numeric',
          meridiem: true,
        },
        events: [],
        eventClick: this.handleEventClick,
      },

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
          { headerName: "Staff Name", field: "staff_name" },
          { headerName: "Staff ID", field: "staff_id" },
          { headerName: "Role", field: "role" },
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
      // showSidebar: true,
      departments: [],
      employeesByDepartment: {},
      selectedDepartments: [],
      formattedEvents: {},
      orgSchedule: {},
      scheduledData: {},
      clickedDateString: null,
      clickedEventDepartment: null,
    };
  },

  mounted() {
    this.get_org_schedule();
    this.getEmployeeDetails();
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
      return {
        html: `
          ${arg.event.title}<br />
          Attendance rate in office: <span class="${rateClass}">${rate}%</span>
        `
      }
    },

    get_org_schedule() {
      fetch(`${url_paths.view_schedule}/o_get_org_schedule`)
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          // "CEO": {
          //   "2024-10-24": {
          //     "AM": [],
          //       "PM": [150488],
          //     "Full": []
          //   }.
          //   "2024-10-25": { ... }
          // },
          // "Consultancy": {
          //   ...
          // }

          this.orgSchedule = data;
          this.displayDepartments(data);

          let formatted_events = [];
          for (const department in data) {
            for (const date in data[department]) {
              const departmentStrength = data[department]["num_employee"];
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

    // toggleSidebar() {
    //   this.showSidebar = !this.showSidebar;
    // },

    handleEventClick(arg) {
      const d = new Date(arg.event.start);
      const year = d.getFullYear();
      const month = String(d.getMonth() + 1).padStart(2, '0');
      const day = String(d.getDate()).padStart(2, '0');
      this.clickedDateString = `${year}-${month}-${day}`;
      this.showDialog = true;
      this.clickedEventDepartment = arg.event.extendedProps.department;
    },

    scheduleValueGetter(params) {
      const staff_id = params.data.staff_id;
      console.log(this.orgSchedule[this.clickedEventDepartment][this.clickedDateString]);

      const isInArray = (array, id) => array.some(item => item.staff_id === id);

      if (isInArray(this.orgSchedule[this.clickedEventDepartment][this.clickedDateString].AM, staff_id)) {
        return 'WFH - AM';
      } else if (isInArray(this.orgSchedule[this.clickedEventDepartment][this.clickedDateString].PM, staff_id)) {
        return 'WFH - PM';
      } else if (isInArray(this.orgSchedule[this.clickedEventDepartment][this.clickedDateString].Full, staff_id)) {
        return 'WFH - Full';
      } else {
        return 'In Office';
      }
    }
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