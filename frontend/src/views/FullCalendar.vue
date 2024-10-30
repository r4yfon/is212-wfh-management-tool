<script setup>
import { url_paths } from "@/url_paths";

fetch(`${url_paths.request_dates}/auto_reject`, {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json'
  }
})
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .catch(error => console.error('Error updating status:', error));
</script>

<template>
  <div class="container-fluid d-flex mt-4">

    <aside class="p-3 d-none d-lg-block bg-primary-subtle me-4 rounded w-auto">
      <!-- Sidebar content goes here -->
      <DatePicker v-model="selectedDate" inline class="mb-4" :minDate="datePicker.start" :maxDate="datePicker.end" />
    </aside>
    <div class="flex-grow-1">
      <FullCalendar ref="fullCalendar" :options="calendarOptions" />
    </div>
  </div>
</template>

<script>
import FullCalendar from "@fullcalendar/vue3";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";
import timeGridPlugin from "@fullcalendar/timegrid";
import DatePicker from "primevue/datepicker";
import { useMainStore } from '@/store.js';

// for mapping event's duration
const timeMapping = {
  "WFH - AM": { start: 9, end: 13 },
  "WFH - PM": { start: 14, end: 18 },
  "WFH - Full": { start: 9, end: 18 },
  "Pending: WFH - AM": { start: 9, end: 13 },
  "Pending: WFH - PM": { start: 14, end: 18 },
  "Pending: WFH - Full": { start: 9, end: 18 },
  "Office": { start: 9, end: 18 },
  "Pending Withdrawal: WFH - AM": { start: 9, end: 13 },
  "Pending Withdrawal: WFH - PM": { start: 14, end: 18 },
  "Pending Withdrawal: WFH - Full": { start: 9, end: 18 },
};


export default {
  components: {
    FullCalendar, DatePicker
  },
  data() {
    return {
      calendarOptions: {
        plugins: [timeGridPlugin, dayGridPlugin, interactionPlugin],
        initialView: "dayGridWeek",
        validRange: {
          start: new Date(new Date().getFullYear(), new Date().getMonth() - 2, new Date().getDate()).toISOString().split("T")[0],
          end: new Date(new Date().getFullYear(), new Date().getMonth() + 3, new Date().getDate()).toISOString().split("T")[0],
        },
        height: "373px",
        headerToolbar: {
          left: "prev,next today",
          center: "title",
          right: "dayGridWeek,dayGridDay", // Options for week and day views
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
      },
      events: [],
      colors: {
        "WFH - AM": "#BA55D3",
        "WFH - PM": "#BA55D3",
        "WFH - Full": "#BA55D3",
        Office: "#4169E1",
        "Pending: WFH - AM": "#FF7F50",
        "Pending: WFH - PM": "#FF7F50",
        "Pending: WFH - Full": "#FF7F50",
        "Pending Withdrawal: WFH - AM": "pink",
        "Pending Withdrawal: WFH - PM": "pink",
        "Pending Withdrawal: WFH - Full": "pink",
      },

      datePicker: {
        start: new Date(new Date().getFullYear(), new Date().getMonth() - 2, new Date().getDate()),
        end: new Date(new Date().getFullYear(), new Date().getMonth() + 3, new Date().getDate()),
      },

      selectedDate: new Date(),
      scheduledData: {},
      currentDate: new Date(),
      userStore: null,
    };
  },

  mounted() {
    this.userStore = useMainStore();
    this.getWeeklySchedule(this.userStore.user);
    const nextButton = document.querySelector(".fc-next-button");
    nextButton.addEventListener("click", this.handleNextClick);
    const prevButton = document.querySelector(".fc-prev-button");
    prevButton.addEventListener("click", this.handlePrevClick);
    const todayButton = document.querySelector(".fc-today-button");
    todayButton.addEventListener("click", this.handleTodayClick);
  },

  watch: {
    selectedDate: {
      handler(value) {
        // console.log(value)
        this.$refs.fullCalendar.getApi().gotoDate(value);
        this.currentDate = value.toISOString().split("T")[0];
        this.getWeeklySchedule(this.userStore.user);
      },
    },
  },

  methods: {
    handleNextClick() {
      this.currentDate = new Date(this.currentDate).setDate(
        new Date(this.currentDate).getDate() + 7,
      );
      const dateISO = new Date(this.currentDate).toISOString().split("T")[0];
      if (!(dateISO in this.scheduledData)) {
        this.getWeeklySchedule(this.userStore.user);
      }
    },
    handlePrevClick() {
      this.currentDate = new Date(this.currentDate).setDate(
        new Date(this.currentDate).getDate() - 7,
      );
      const dateISO = new Date(this.currentDate).toISOString().split("T")[0];
      if (!(dateISO in this.scheduledData)) {
        this.getWeeklySchedule(this.userStore.user);
      }
    },
    handleTodayClick() {
      this.currentDate = new Date();
      const dateISO = new Date(this.currentDate).toISOString().split("T")[0];
      if (!(dateISO in this.scheduledData)) {
        this.getWeeklySchedule(this.userStore.user);
      }
    },
    getWeeklySchedule(user) {
      const staff_id = user.staff_id;
      if ((!this.currentDate) instanceof Date) {
        this.currentDate = new Date();
      }
      fetch(
        `${url_paths.view_schedule}/view_schedule/weekly/${staff_id}/${new Date(this.currentDate).toISOString().split("T")[0]}`,
      )
        .then((response) => response.json())
        .then((data) => {
          const retrievedData = data.data;

          for (let day in retrievedData) {
            const dateString = day;
            if (!(dateString in this.scheduledData)) {
              this.scheduledData[dateString] = retrievedData[dateString];
              const eventTitles = retrievedData[dateString];
              eventTitles.forEach((eventTitle) => {
                let event;
                const times = timeMapping[eventTitle];

                if (times) {
                  const eventYear = Number(day.slice(0, 4));
                  const eventMonthIndex = Number(day.slice(5, 7)) - 1;
                  const eventDate = Number(day.slice(8, 10));
                  event = {
                    title: eventTitle,
                    start: new Date(eventYear, eventMonthIndex, eventDate, times.start, 0),
                    end: new Date(eventYear, eventMonthIndex, eventDate, times.end, 0),
                    color: this.colors[eventTitle],
                    textColor: this.colors[eventTitle],
                  };
                }

                if (event) {
                  this.events.push(event);
                }
              });
            }
          }
          this.calendarOptions.events = this.events;
        })
        .catch((error) => {
          console.error("Error fetching schedule data:", error);
        });
    },
  },
};
</script>