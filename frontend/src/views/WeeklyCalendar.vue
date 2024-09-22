<template>
<div>
    <v-sheet>
    <v-calendar
        ref="calendar"
        v-model="value"
        :events="events"
        :view-mode="type"
        :weekdays="weekday"
        :interval-start="8"          
        :interval-duration="60"     
        :intervals="10"  
        class= "full-width">
    </v-calendar>
    </v-sheet>
</div>
</template>

<script>
import { useDate } from 'vuetify'

export default {
    data: () => ({
        type: 'week',
        weekdays: [0, 1, 2, 3, 4, 5, 6],
        value: [new Date()],
        events: [],
        colors: {
        'Home - AM': 'cyan',
        'Home - PM': 'cyan',
        'Home': 'cyan', 
        'Office - AM': 'green',
        'Office - PM': 'green',
        'Office' : 'green'

        },
        scheduleData: {
        "2024-09-22": "Office - AM",
        "2024-09-23": "Office - PM",
        "2024-09-24": "Home - AM",
        "2024-09-15": "Home",
        "2024-09-16": "Office",
        "2024-09-30": "Home - PM",
        },
}),
    mounted () {
        const adapter = useDate()

        // Set the start date to 2 months back and end date to 3 months forward
        const currentDate = new Date()
        const min = adapter.startOfDay(adapter.addMonths(currentDate, -2)) // 2 months back
        const max = adapter.endOfDay(adapter.addMonths(currentDate, 3))    // 3 months forward

        // Fetch events between the min and max date
        this.getSchedule({ start: min, end: max })
},
    methods: {
        getSchedule ({ start, end }) {
        const events = []
        const min = start
        const max = end
        const timeMapping = {
            "Home - AM": { start: 9, end: 18 },  
            "Home - PM": { start: 14, end: 18 }, 
            "Home": { start: 9, end: 18 },       
            "Office - AM": { start: 9, end: 13 },
            "Office - PM": { start: 14, end: 18 },
            "Office": { start: 9, end: 18 },   
        };

        // Loop through each day in the date range
        for (let day = new Date(min); day <= max; day.setDate(day.getDate() + 1)) {
            const dateString = day.toISOString().split('T')[0]; // Format the date as YYYY-MM-DD
            const eventTitle = this.scheduleData[dateString]; // Get Home or Office from schedule data

            const times = timeMapping[eventTitle];

        // Only create the event if a valid title is found
            if (times) {
                const event = {
                    title: eventTitle,
                    start: new Date(day.getFullYear(), day.getMonth(), day.getDate(), times.start, 0),
                    end: new Date(day.getFullYear(), day.getMonth(), day.getDate(), times.end, 0),
                    color: this.colors[eventTitle] // Use the color defined for the title
                };

                events.push(event);
            }
        }

            this.events = events;
        }
    }
}
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

