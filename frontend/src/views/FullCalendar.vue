<script setup>
fetch(`http://localhost:5002/request_dates/auto_reject`, {
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
  .then(() => {
    console.log('Success');
  })
  .catch(error => console.error('Error updating status:', error));
</script>

<template>
  <div class="container">
    <FullCalendar :options="calendarOptions" class="calendar" />
  </div>
</template>

<script>
import FullCalendar from "@fullcalendar/vue3";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";
import timeGridPlugin from "@fullcalendar/timegrid";
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
    FullCalendar, // make the <FullCalendar> tag available
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
      getTextColors: {
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
      scheduledData: {},
      currentDate: new Date(),
    };
  },
  mounted() {
    const userStore = useMainStore();
    const nextButton = document.querySelector(".fc-next-button");
    nextButton.addEventListener("click", this.handleNextClick);
    const prevButton = document.querySelector(".fc-prev-button");
    prevButton.addEventListener("click", this.handlePrevClick);
    const todayButton = document.querySelector(".fc-today-button");
    todayButton.addEventListener("click", this.handleTodayClick);

    this.currentDate = new Date();
    this.getWeeklySchedule(userStore.user);
  },
  computed: {
    user_store() {
      return useMainStore();
    }
  },
  watch: {
    "user_store.user": {
      handler(newUser) {
        console.log('change detected')
        console.log('newuser', newUser);
        this.events = [];
        this.scheduledData = {};
        this.getWeeklySchedule(newUser);
      }

    }
  },
  methods: {
    handleDateClick(arg) {
      console.log(`Date ${arg.dateStr} clicked`);
    },
    handleEventClick(arg) {
      console.log(`Event ${arg.event.title} clicked`);
    },
    handleNextClick() {
      this.currentDate = new Date(this.currentDate).setDate(
        new Date(this.currentDate).getDate() + 7,
      );
      const dateISO = new Date(this.currentDate).toISOString().split("T")[0];
      if (!(dateISO in this.scheduledData)) {
        this.getWeeklySchedule(this.user_store.user);
      }
      console.log(`Next button clicked`);
    },
    handlePrevClick() {
      this.currentDate = new Date(this.currentDate).setDate(
        new Date(this.currentDate).getDate() - 7,
      );
      const dateISO = new Date(this.currentDate).toISOString().split("T")[0];
      if (!(dateISO in this.scheduledData)) {
        this.getWeeklySchedule(this.user_store.user);
      }
      console.log(`Prev button clicked`);
    },
    handleTodayClick() {
      this.currentDate = new Date();
      const dateISO = new Date(this.currentDate).toISOString().split("T")[0];
      if (!(dateISO in this.scheduledData)) {
        this.getWeeklySchedule(this.user_store.user);
      }
      console.log(`Today button clicked`);
    },
    eventDidMount(info) {
      info.el.style.color = info.event.textColor; // Set text color directly
    },
    getWeeklySchedule(user) {
      const staff_id = user.staff_id;
      if ((!this.currentDate) instanceof Date) {
        this.currentDate = new Date();
      }
      fetch(
        `http://localhost:5100/view_schedule/weekly/${staff_id}/${new Date(this.currentDate).toISOString().split("T")[0]}`,
      )
        .then((response) => response.json())
        .then((data) => {
          const retrievedData = data.data;

          // this.events = [];

          for (let day in retrievedData) {
            const dateString = day; // e.g. '2024-10-05'
            if (!(dateString in this.scheduledData)) {
              this.scheduledData[dateString] = retrievedData[dateString];
              const eventTitles = retrievedData[dateString]; // Get Home or Office from schedule data
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
                    textColor: this.getTextColors[eventTitle],
                  };
                }

                if (event) {
                  this.events.push(event);
                }

                // console.log(this.events)
              });
            }
          }

          this.calendarOptions.events = this.events;
          console.log(data.data);
        })
        .catch((error) => {
          console.error("Error fetching schedule data:", error);
        });
    },
  },
};
</script>

<style scoped>
.calendar-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  max-height: 100vh;
  /* Full viewport height */
  box-sizing: border-box;
  /* Include padding in total height/width */
}

.calendar {
  width: 95%;
  max-height: calc(100vh - 80px);
  position: fixed;
  top: 80px;
  /* Position below the header */
  left: 50%;
  /* Center horizontally */
  transform: translateX(-50%);
}

/* Hide scrollbars for Chrome and Safari */
.calendar::-webkit-scrollbar {
  display: none;
  /* Safari and Chrome */
}

/* Hide scrollbars for Firefox */
.calendar {
  scrollbar-width: none;
  /* Firefox */
}

/* Responsive styles for smaller screens */
@media (max-width: 768px) {
  .calendar {
    width: 100%;
    height: calc(100vh - 80px);
    top: 80px;
    left: 0;
    transform: none;
  }
}
</style>