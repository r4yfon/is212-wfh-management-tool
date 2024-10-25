<script setup>
import FullCalendar from '@fullcalendar/vue3';
import interactionPlugin from '@fullcalendar/interaction';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import { ref, onMounted } from 'vue';

const workColors = {
  'WFH - AM': '#F48BA9',  
  'WFH - PM': '#FFB6C1',  
  'WFH - Full': '#BA55D3', 
  Office: '#86CBED'        
};

const selectedTeam = ref('Engineering'); // Assumes the user is from the Engineering department

// Event click handler
const handleEventClick = (arg) => {
  const d = new Date(arg.event.start);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  clickedDateString.value = `${year}-${month}-${day}`;
  clickedEventDetails.value = arg.event.extendedProps;

  // Check if there are any staff names to display
  const hasStaff = 
    (clickedEventDetails.value.amCount > 0 && clickedEventDetails.value.staffNames.length > 0) ||
    (clickedEventDetails.value.pmCount > 0 && clickedEventDetails.value.pmStaffNames.length > 0) ||
    (clickedEventDetails.value.fullCount > 0 && clickedEventDetails.value.fullStaffNames.length > 0) ||
    (clickedEventDetails.value.inOfficeCount > 0 && clickedEventDetails.value.inOfficeStaffNames.length > 0);
  
  if (hasStaff) {
    showDialog.value = true;
  }
};

const calendarOptions = ref({
  plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
  initialView: 'dayGridWeek',
  height: '400px',
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridWeek,dayGridDay',
  },

  events: [],
  eventClick: handleEventClick,
});

const showDialog = ref(false);
const clickedDateString = ref(null);
const clickedEventDetails = ref(null);

// Fetch team schedule
const getTeamSchedule = async (staff_id) => {
  try {
    const response = await fetch(`http://127.0.0.1:5100/s_get_team_schedule/${staff_id}`);
    if (!response.ok) throw new Error('Failed to fetch schedule');

    const data = await response.json();
    displayTeamSchedule(data);
  } catch (error) {
    console.error(error);
  }
};

// Display team schedule on the calendar
const displayTeamSchedule = (teamSchedule) => {
  const formattedEvents = [];

  for (const date in teamSchedule[selectedTeam.value]) {
    if (date !== 'num_employee') {
      const departmentStrength = teamSchedule[selectedTeam.value].num_employee;
      const AMCount = teamSchedule[selectedTeam.value][date].AM.length;
      const PMCount = teamSchedule[selectedTeam.value][date].PM.length;
      const FullCount = teamSchedule[selectedTeam.value][date].Full.length;
      const inOfficeCount = departmentStrength - AMCount - PMCount - FullCount;

      // Create blocks for each time period
      formattedEvents.push(
        {
          title: `WFH - AM: ${AMCount} people`,
          start: date,
          color: workColors['WFH - AM'],
          extendedProps: { 
            amCount: AMCount, 
            staffNames: teamSchedule[selectedTeam.value][date].AM.map(staff => staff.name),
          },
        },
        {
          title: `WFH - PM: ${PMCount} people`,
          start: date,
          color: workColors['WFH - PM'],
          extendedProps: { 
            pmCount: PMCount,
            pmStaffNames: teamSchedule[selectedTeam.value][date].PM.map(staff => staff.name),
          },
        },
        {
          title: `WFH - Full: ${FullCount} people`,
          start: date,
          color: workColors['WFH - Full'],
          extendedProps: { 
            fullCount: FullCount, 
            fullStaffNames: teamSchedule[selectedTeam.value][date].Full.map(staff => staff.name),
          },
        },
        {
          title: `Office: ${inOfficeCount} people`,
          start: date,
          color: workColors.Office,
          extendedProps: { 
            inOfficeCount, 
            inOfficeStaffNames: [], 
            // inOfficeStaffNames: teamSchedule[selectedTeam.value][date].Office.map(staff => staff.name),
          },
        }
      );
    }
  }

  calendarOptions.value.events = formattedEvents;
};

// Fetch data on mount
onMounted(() => {
  const staff_id = 150488; // Assume Jacob Tan Staff_Id
  getTeamSchedule(staff_id);
});
</script>

<template>
  <div class="container-fluid d-flex mt-4">
    <section class="flex-grow-1">
      <FullCalendar :options="calendarOptions" />
      <v-dialog v-model="showDialog" max-width="75%" >
        <v-card>
          <v-card-title>Staff</v-card-title>
          <v-card-text class="dialog-content">
            <div v-if="clickedEventDetails.amCount">
              <ul>
                <li v-for="(name, index) in clickedEventDetails.staffNames" :key="index">{{ name }}</li>
              </ul>
            </div>
            <div v-if="clickedEventDetails.pmCount">
              <ul>
                <li v-for="(name, index) in clickedEventDetails.pmStaffNames" :key="index">{{ name }}</li>
              </ul>
            </div>
            <div v-if="clickedEventDetails.fullCount">
              <ul>
                <li v-for="(name, index) in clickedEventDetails.fullStaffNames" :key="index">{{ name }}</li>
              </ul>
            </div>
            <div v-if="clickedEventDetails.inOfficeCount">
              <ul>
                <li v-for="(name, index) in clickedEventDetails.inOfficeStaffNames" :key="index">{{ name }}</li>
              </ul>
            </div>
          </v-card-text>
        </v-card>
      </v-dialog>
    </section>
  </div>
</template>

<style>
.fc-h-event .fc-event-title {
  white-space: normal;
}

.fc-event-main {
  padding: 0.25rem;
}

.dialog-content {
  max-height: 300px;  /* Set maximum height */
  overflow-y: auto;   /* Enable vertical scrolling */
}
</style>
