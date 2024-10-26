<script setup>
const departmentColors = {
  CEO: '#FFB3BA',
  Consultancy: '#FFDFBA',
  Engineering: '#FFFFBA',
  Finance: '#BAFFC9',
  IT: '#BAE1FF',
  HR: '#D7BAFF',
  Sales: '#FFB3E6',
  Solutioning: '#A3E4D7'
}
</script>

<template>
  <div class="container-fluid d-flex mt-4">
    <aside class="p-3 d-none d-lg-block bg-primary-subtle me-4 rounded w-auto" v-if="showSidebar">
      <!-- Sidebar content goes here -->
      <DatePicker v-model="selectedDate" inline class="mb-4" :minDate="datePicker.start" :maxDate="datePicker.end" />
      <v-checkbox v-for="department in departments" :key="department" :value="department" :label="department"
        :color="departmentColors[department]" v-model="selectedDepartments" hide-details></v-checkbox>
    </aside>
    <section class="flex-grow-1">
      <button @click="toggleSidebar" class="btn btn-outline-primary">Toggle Sidebar</button>
      <FullCalendar ref="fullCalendar" :options="calendarOptions" />
      <v-dialog v-model="showDialog" max-width="80%">
        <v-card>
          <v-card-title>{{ clickedDateString }}: {{ clickedEventDepartment }}</v-card-title>
          <v-card-text>
            <table class="table table-striped">
              <thead>
                <tr>
                  <th>Employee Name</th>
                  <th>Employee ID</th>
                  <th>Employee Role</th>
                  <th>WFH Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="employee in Object.entries(employeesByDepartment[clickedEventDepartment])"
                  :key="employee.id">
                  <!-- {{ employee }} -->
                  <td>{{ employee[1].staff_name }}</td>
                  <td>{{ employee[0] }}</td>
                  <td>{{ employee[1].role }}</td>
                  <td>
                    <span v-if="orgSchedule[clickedEventDepartment][clickedDateString].AM.includes(employee.id)">WFH
                      AM</span>
                    <span
                      v-else-if="orgSchedule[clickedEventDepartment][clickedDateString].PM.includes(employee.id)">WFH
                      PM</span>
                    <span
                      v-else-if="orgSchedule[clickedEventDepartment][clickedDateString].Full.includes(employee.id)">WFH
                      Full</span>
                    <span v-else>In Office</span>
                  </td>
                </tr>
              </tbody>
            </table>
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

const departmentColors = {
  CEO: '#FFB3BA',
  Consultancy: '#FFDFBA',
  Engineering: '#FFFFBA',
  Finance: '#BAFFC9',
  IT: '#BAE1FF',
  HR: '#D7BAFF',
  Sales: '#FFB3E6',
  Solutioning: '#A3E4D7'
}

export default {
  components: {
    FullCalendar, DatePicker
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
        // displayEventEnd: true,
        events: [],
        // dateClick: this.handleDateClick,
        eventClick: this.handleEventClick,
      },

      datePicker: {
        start: new Date(new Date().getFullYear(), new Date().getMonth() - 2, new Date().getDate()),
        end: new Date(new Date().getFullYear(), new Date().getMonth() + 3, new Date().getDate()),
      },

      selectedDate: new Date(),
      showDialog: false,
      showSidebar: true,
      departments: [],
      employeesByDepartment: {},
      selectedDepartments: [],
      formattedEvents: {},
      orgSchedule: {},
      scheduledData: {},
      currentDate: new Date(),
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
        // Clear current events
        this.calendarOptions.events = [];

        // Populate events based on selected departments
        newDepartments.forEach(department => {
          // if (this.formattedEvents[department]) {
          this.calendarOptions.events.push(...this.formattedEvents[department]);
          // }
        });
      },
      deep: true,
    },

    selectedDate: {
      handler(value) {
        this.$nextTick(() => {
          this.$refs.fullCalendar.getApi().gotoDate(value);
        });
      },
    },
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
          // console.log(this.orgSchedule);

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
                  color: departmentColors[department],
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

    toggleSidebar() {
      this.showSidebar = !this.showSidebar;
    },

    handleEventClick(arg) {
      const d = new Date(arg.event.start);
      const year = d.getFullYear();
      const month = String(d.getMonth() + 1).padStart(2, '0');
      const day = String(d.getDate()).padStart(2, '0');
      this.clickedDateString = `${year}-${month}-${day}`;
      this.showDialog = true;
      this.clickedEventDepartment = arg.event.extendedProps.department;

      console.log(this.orgSchedule[this.clickedEventDepartment][this.clickedDateString]);
      console.log(this.employeesByDepartment[this.clickedEventDepartment]);
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
    /* box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2), 0 4px 20px rgba(0, 0, 0, 0.1); */
  }
}
</style>