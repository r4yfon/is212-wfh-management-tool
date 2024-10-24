<template>
  <div class="container-fluid d-flex mt-4">
    <aside class="p-3 d-none d-lg-block bg-primary-subtle me-4 rounded w-auto" v-if="showSidebar">
      <!-- Sidebar content goes here -->
      <DatePicker v-model="selectedDate" inline class="mb-4" :minDate="datePicker.start" :maxDate="datePicker.end" />
      <v-checkbox v-for="department in departments" :key="department" :value="department" :label="department"
        :color="calendarOptions.departmentColors[department]" v-model="selectedDepartments" hide-details></v-checkbox>
    </aside>
    <section class="flex-grow-1">
      <button @click="toggleSidebar" class="btn btn-outline-primary">Toggle Sidebar</button>
      <FullCalendar ref="fullCalendar" :options="calendarOptions" />
      <v-dialog v-model="showDialog" max-width="75%">
        <v-card>
          <v-card-title>{{ clickedDate }}</v-card-title>
          <v-card-text>

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
        height: '373px',
        headerToolbar: {
          left: 'prev,next today',
          center: 'title',
          right: 'dayGridWeek,dayGridDay', // Options for week and day views
        },
        eventTimeFormat: {
          hour: 'numeric',
          meridiem: true,
        },
        displayEventEnd: true,
        // eventDisplay: "block",
        eventDidMount: this.eventDidMount,
        events: [],
        dateClick: this.handleDateClick,
        eventClick: this.handleEventClick,
        departmentColors: {
          CEO: '#FFB3BA',
          Consultancy: '#FFDFBA',
          Engineering: '#FFFFBA',
          Finance: '#BAFFC9',
          IT: '#BAE1FF',
          HR: '#D7BAFF',
          Sales: '#FFB3E6',
          Solutioning: '#FFDFD3'
        }
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
      clickedDate: null,
    };
  },

  mounted() {
    this.get_org_schedule();
  },
  watch: {
    selectedDepartments: {
      handler(newDepartments) {
        // Clear current events
        this.calendarOptions.events = [];

        // Populate events based on selected departments
        newDepartments.forEach(department => {
          if (this.events[department]) {
            this.calendarOptions.events.push(...this.events[department]);
          }
        });
      },
      deep: true,
    },

    selectedDate: {
      handler(value) {
        this.$refs.fullCalendar.getApi().gotoDate(value);
      },
    },
  },

  methods: {
    get_org_schedule() {
      fetch(`${url_paths.view_schedule}/o_get_org_schedule`)
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          // this.events = [
          //   {
          //     title: "WFH - AM",
          //     staff: [
          //       {
          //         staff_id: 150488,
          //         staff_name: "Jacob Tan"
          //       },
          //       {
          //         // ...
          //       }
          //     ],
          //     start: "2024-10-25"
          //   }
          // ]

          let formatted_events = [];

          for (const department in data) {
            for (const date in data[department]) {
              const staff_schedules = data[department][date];

              staff_schedules.forEach(schedule_item => {
                schedule_item.schedule.forEach(schedule_type => {
                  let event = formatted_events.find(event => event.title === schedule_type && event.start === date);

                  if (!event) {
                    event = {
                      title: schedule_type,
                      staff: [],
                      start: date,
                      description: department,
                      allDay: true,
                      color: this.calendarOptions.departmentColors[department],
                      textColor: "#000000",
                    };
                    formatted_events.push(event);
                  }

                  event.staff.push({
                    staff_id: schedule_item.staff_id,
                    staff_name: schedule_item.staff_name
                  });
                });
              });
            }
            this.events[department] = formatted_events;
            formatted_events = [];
          }

          this.calendarOptions.events = formatted_events;
          console.log(this.events);

          for (let department in this.events) {
            console.log(department)
            this.departments.push(department);
          }

          this.selectedDepartments = this.departments;
        })
    },

    toggleSidebar() {
      this.showSidebar = !this.showSidebar;
    },

    handleDateClick(arg) {
      this.showDialog = true;
      this.clickedDate = arg.dateStr;
    }
  }
}
</script>