<template>
  <div>
    <v-sheet>
      <v-calendar
        ref="calendar"
        v-model="value"
        @update:modelValue="changeDate"
        :events="events"
        :view-mode="type"
        :interval-start="8"
        :interval-duration="60"
        :intervals="10"
        class="full-width">
      </v-calendar>
    </v-sheet>
  </div>
</template>

<script>
  import { useDate } from "vuetify";

  export default {
    data: () => ({
      type: "week",
      weekdays: [0, 1, 2, 3, 4, 5, 6],
      value: [new Date()],
      today: new Date().toISOString().split("T")[0],
      events: [],
      colors: {
        "Home - AM": "cyan",
        "Home - PM": "cyan",
        Home: "cyan",
        "Office - AM": "green",
        "Office - PM": "green",
        Office: "green",
      },
      scheduleData: {},
    }),
    mounted() {
      const adapter = useDate();

      // Set the start date to 2 months back and end date to 3 months forward
      const currentDate = new Date().toISOString().split("T")[0];
      const min = adapter.startOfDay(adapter.addMonths(currentDate, -2)); // 2 months back
      const max = adapter.endOfDay(adapter.addMonths(currentDate, 3)); // 3 months forward
      fetch(`http://localhost:5100/view_schedule/weekly/150488/${currentDate}`)
        .then((response) => response.json())
        .then((data) => {
          this.scheduleData = data.data;
        })
        .catch((error) => {
          console.error("Error fetching schedule data:", error);
        });

      // Fetch events between the min and max date
      // this.getSchedule({ start: min, end: max });
      this.getWeeklySchedule(currentDate);
    },
    methods: {
      // getSchedule({ start, end }) {
      //   const events = [];
      //   const min = start;
      //   const max = end;
      //   const timeMapping = {
      //     "Home - AM": { start: 9, end: 13 },
      //     "Home - PM": { start: 14, end: 18 },
      //     "Home - Full": { start: 9, end: 18 },
      //     Office: { start: 9, end: 18 },
      //   };

      //   // Loop through each day in the date range
      //   for (let day = new Date(min); day <= max; day.setDate(day.getDate() + 1)) {
      //     const dateString = day.toISOString().split("T")[0]; // Format the date as YYYY-MM-DD
      //     const eventTitle = this.scheduleData[dateString]; // Get Home or Office from schedule data

      //     const times = timeMapping[eventTitle];

      //     // Only create the event if a valid title is found
      //     if (times) {
      //       const event = {
      //         title: eventTitle,
      //         start: new Date(day.getFullYear(), day.getMonth(), day.getDate() - 1, times.start, 0),
      //         end: new Date(day.getFullYear(), day.getMonth(), day.getDate() - 1, times.end, 0),
      //         color: this.colors[eventTitle], // Use the color defined for the title
      //       };

      //       events.push(event);
      //     }
      //   }

      //   this.events = events;
      // },

      getWeeklySchedule(date) {
        const timeMapping = {
          "Home - AM": { start: 9, end: 13 },
          "Home - PM": { start: 14, end: 18 },
          "Home - Full": { start: 9, end: 18 },
          Office: { start: 9, end: 18 },
        };
        fetch(`http://localhost:5100/view_schedule/weekly/150488/${date}`)
          .then((response) => response.json())
          .then((data) => {
            this.scheduleData = data.data;
            for (let day in this.scheduleData) {
              const dateString = day;
              // console.log(dateString);
              const eventTitle = this.scheduleData[dateString]; // Get Home or Office from schedule data
              const times = timeMapping[eventTitle];
              if (times) {
                const eventYear = Number(day.slice(0, 4));
                const eventMonthIndex = Number(day.slice(5, 7)) - 1;
                const eventDate = Number(day.slice(8, 10));
                const event = {
                  title: eventTitle,
                  start: new Date(eventYear, eventMonthIndex, eventDate, times.start, 0),
                  end: new Date(eventYear, eventMonthIndex, eventDate, times.end, 0),
                  color: this.colors[eventTitle], // Use the color defined for the title
                };
                // console.log(event);
                this.events.push(event);
              }
            }
          })
          .catch((error) => {
            console.error("Error fetching schedule data:", error);
          });
      },

      changeDate(e) {
        const newDate = e[0].toISOString().split("T")[0];
        this.getWeeklySchedule(newDate);
      },
    },
  };
</script>

<style scoped>
  .full-width {
    width: 100%; /* Makes the calendar span the full width of its container */
  }

  v-sheet {
    width: 100%; /* Ensure v-sheet also spans full width */
  }

  @media (max-width: 768px) {
    .full-width {
      /* Adjust calendar styling for smaller screens if necessary */
      font-size: 0.8rem;
    }
  }
</style>
