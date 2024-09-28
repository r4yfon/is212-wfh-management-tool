<template>
  <div class="calendar-container">
    <FullCalendar :options="calendarOptions" class="calendar" />
  </div>
</template>

<script>
  import FullCalendar from "@fullcalendar/vue3";
  import dayGridPlugin from "@fullcalendar/daygrid";
  import interactionPlugin from "@fullcalendar/interaction";
  import timeGridPlugin from "@fullcalendar/timegrid";

  export default {
    components: {
      FullCalendar, // make the <FullCalendar> tag available
    },
    data() {
      return {
        calendarOptions: {
          plugins: [timeGridPlugin, dayGridPlugin, interactionPlugin],
          initialView: "timeGridWeek",
          slotMinTime: "09:00:00",
          slotMaxTime: "18:00:00",
          slotDuration: "01:00:00",
          headerToolbar: {
            left: "prev,next today",
            center: "title",
            right: "timeGridWeek,timeGridDay", // Options for week and day views
          },
          events: [],
          dateClick: this.handleDateClick,
          eventClick: this.handleEventClick,
        },
        events: [],
        colors: {
          "WFH - AM": "purple",
          "WFH - PM": "purple",
          "WFH - Full": "purple",
          Office: "blue",
          "Pending: WFH - AM": "grey",
          "Pending: WFH - PM": "grey",
          "Pending: WFH - Full": "grey",
          "Pending Withdraw: WFH - AM": "orange",
          "Pending Withdrawal: WFH - PM": "orange",
          "Pending Withdrawal: WFH - Full": "orange",
        },
        scheduleData: {},
        currentDate: new Date(),
      };
    },
    mounted() {
      const nextButton = document.querySelector(".fc-next-button");
      nextButton.addEventListener("click", this.handleNextClick);
      const prevButton = document.querySelector(".fc-prev-button");
      prevButton.addEventListener("click", this.handlePrevClick);
      const todayButton = document.querySelector(".fc-today-button");
      todayButton.addEventListener("click", this.handleTodayClick);

      this.currentDate = new Date();
      this.getWeeklySchedule();
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
        this.getWeeklySchedule();
        console.log(`Next button clicked`);
      },
      handlePrevClick() {
        this.currentDate = new Date(this.currentDate).setDate(
          new Date(this.currentDate).getDate() - 7,
        );
        this.getWeeklySchedule();
        console.log(`Prev button clicked`);
      },
      handleTodayClick() {
        console.log(`Today button clicked`);
      },
      getWeeklySchedule() {
        if (!(this.currentDate instanceof Date)) {
          this.currentDate = new Date();
        }
        fetch(
          `http://localhost:5100/view_schedule/weekly/150488/${new Date(this.currentDate).toISOString().split("T")[0]}`,
        )
          .then((response) => response.json())
          .then((data) => {
            this.scheduleData = data.data;

            const timeMapping = {
              "WFH - AM": { start: 9, end: 13 },
              "WFH - PM": { start: 14, end: 18 },
              "Pending: WFH - AM": { start: 9, end: 13 },
              "Pending: WFH - PM": { start: 14, end: 18 },
            };

            this.events = [];

            for (let day in this.scheduleData) {
              const dateString = day;
              const eventTitles = this.scheduleData[dateString]; // Get Home or Office from schedule data

              eventTitles.forEach((eventTitle) => {
                let event;
                const times = timeMapping[eventTitle];

                if (
                  eventTitle.includes("WFH - Full") ||
                  eventTitle.includes("Office") ||
                  eventTitle.includes("Pending: WFH - Full")
                ) {
                  event = {
                    title: eventTitle,
                    start: dateString,
                    allDay: true,
                    color: this.colors[eventTitle],
                  };
                } else if (times) {
                  const eventYear = Number(day.slice(0, 4));
                  const eventMonthIndex = Number(day.slice(5, 7)) - 1;
                  const eventDate = Number(day.slice(8, 10));
                  event = {
                    title: eventTitle,
                    start: new Date(eventYear, eventMonthIndex, eventDate, times.start, 0),
                    end: new Date(eventYear, eventMonthIndex, eventDate, times.end, 0),
                    color: this.colors[eventTitle],
                  };
                } else if (eventTitle.includes("Pending Withdrawal")) {
                  event = {
                    title: eventTitle,
                    start: dateString,
                    allDay: true,
                    color: this.colors[eventTitle],
                  };
                }

                if (event) {
                  this.events.push(event);
                }
                // console.log(this.events)
              });
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
    max-height: 100vh; /* Full viewport height */
    box-sizing: border-box; /* Include padding in total height/width */
  }

  .calendar {
    width: 95%;
    max-height: calc(100vh - 80px);
    position: fixed;
    top: 80px; /* Position below the header */
    left: 50%; /* Center horizontally */
    transform: translateX(-50%);
  }

  /* Hide scrollbars for Chrome and Safari */
  .calendar::-webkit-scrollbar {
    display: none; /* Safari and Chrome */
  }

  /* Hide scrollbars for Firefox */
  .calendar {
    scrollbar-width: none; /* Firefox */
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
