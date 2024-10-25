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
      <v-dialog v-model="showDialog" max-width="75%">
        <v-card>
          <v-card-title>{{ clickedDateString }}</v-card-title>
          <v-card-text>
            {{ clickedEventDepartment }}
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
          right: 'dayGridWeek,dayGridDay', // Options for week and day views
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
      selectedDepartments: [],
      events: {},
      scheduledData: {},
      currentDate: new Date(),
      clickedDateString: null,
      clickedEventDepartment: null,
    };
  },

  mounted() {
    this.get_org_schedule();
  },
  watch: {
    selectedDepartments: {
      handler(newDepts, oldDepts) {
        if (newDepts === oldDepts) {
          return;
        }
        if (!oldDepts || newDepts.length !== oldDepts.length || newDepts.some(dept => !oldDepts.includes(dept))) {
          // Only update events if there is a change in departments
          this.updateCalendarEvents(newDepts);
        }
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

    updateCalendarEvents(departments) {
      const newEvents = departments.flatMap(dept => this.events[dept] || []);
      this.calendarOptions = {
        ...this.calendarOptions,
        events: newEvents,
      };
    },

    renderEventContent(arg) {
      const rate = Math.floor(arg.event.extendedProps.officeAttendanceRate);
      const rateClass = rate > 50 ? 'text-success-emphasis' : 'text-danger';
      return {
        html: `
        <div>
          ${arg.event.title}<br />
          Attendance rate in office: <span class="${rateClass}">${rate}%</span>
        </div>
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
                  color: departmentColors[department],
                  textColor: "#000000",
                };
                formatted_events.push(event);
              }
            }
            this.events[department] = formatted_events;
            formatted_events = [];
          }
          this.calendarOptions.events = formatted_events;
        })
    },

    toggleSidebar() {
      this.showSidebar = !this.showSidebar;
    },

    // handleDateClick(arg) {
    //   this.clickedDateString = arg.dateStr;
    //   this.showDialog = true;
    //   console.log(this.clickedDateString);
    // },

    modifySelectedDepartments() {
      this.selectedDepartments = this.selectedDepartments.filter(department => this.departments.includes(department));
    },

    handleEventClick(arg) {
      const d = new Date(arg.event.start);
      const year = d.getFullYear();
      const month = String(d.getMonth() + 1).padStart(2, '0');
      const day = String(d.getDate()).padStart(2, '0');
      this.clickedDateString = `${year}-${month}-${day}`;
      this.showDialog = true;
      this.clickedEventDepartment = arg.event.extendedProps.department;
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
}
</style>

formatDate(date) {
const d = new Date(date);
const year = d.getFullYear();
const month = String(d.getMonth() + 1).padStart(2, '0'); // Months are zero-based
const day = String(d.getDate()).padStart(2, '0');
return `${year}-${month}-${day}`;
}