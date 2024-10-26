<script setup>
import FullCalendar from '@fullcalendar/vue3';
import interactionPlugin from '@fullcalendar/interaction';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import { ref, onMounted, computed } from 'vue';

const workColors = {
  'WFH - AM': '#F48BA9',
  'WFH - PM': '#FFB6C1',
  'WFH - Full': '#BA55D3',
  Office: '#86CBED'
};

const selectedTeam = ref('Engineering'); // Assumes the user is from the Engineering department

const handleEventClick = (arg) => {
  const d = new Date(arg.event.start);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  clickedDateString.value = `${year}-${month}-${day}`;
  clickedEventDetails.value = arg.event.extendedProps;

  const hasPeople = 
    clickedEventDetails.value.amCount > 0 || 
    clickedEventDetails.value.pmCount > 0 || 
    clickedEventDetails.value.fullCount > 0 || 
    clickedEventDetails.value.inOfficeCount > 0;

  if (hasPeople) {
    showDialog.value = true;
  } else {
    showDialog.value = false;
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
const searchTerm = ref(''); // Search term for filtering staff names

// Computed properties to filter staff names based on the search term
const filteredAMStaffNames = computed(() => {
  if (!clickedEventDetails.value?.staffNames) return [];
  return clickedEventDetails.value.staffNames.filter(name => 
    name.toLowerCase().includes(searchTerm.value.toLowerCase())
  );
});

const filteredPMStaffNames = computed(() => {
  if (!clickedEventDetails.value?.pmStaffNames) return [];
  return clickedEventDetails.value.pmStaffNames.filter(name => 
    name.toLowerCase().includes(searchTerm.value.toLowerCase())
  );
});

const filteredFullStaffNames = computed(() => {
  if (!clickedEventDetails.value?.fullStaffNames) return [];
  return clickedEventDetails.value.fullStaffNames.filter(name => 
    name.toLowerCase().includes(searchTerm.value.toLowerCase())
  );
});

const filteredInOfficeStaffNames = computed(() => {
  if (!clickedEventDetails.value?.inOfficeStaffNames) return [];
  return clickedEventDetails.value.inOfficeStaffNames.filter(name => 
    name.toLowerCase().includes(searchTerm.value.toLowerCase())
  );
});

// Fetch both employee details and team schedule
const fetchAndDisplayData = async (staff_id) => {
  try {
    const employeeResponse = await fetch('http://127.0.0.1:5000/employee/get_all_employees_by_dept');
    if (!employeeResponse.ok) throw new Error('Failed to fetch employee details');
    const employeeData = await employeeResponse.json();

    const scheduleResponse = await fetch(`http://127.0.0.1:5100/s_get_team_schedule/${staff_id}`);
    if (!scheduleResponse.ok) throw new Error('Failed to fetch schedule');
    const scheduleData = await scheduleResponse.json();

    displayTeamSchedule(scheduleData, employeeData.data);
  } catch (error) {
    console.error(error);
  }
};

// Display team schedule on the calendar
const displayTeamSchedule = (teamSchedule, employeesByDept) => {
  const formattedEvents = [];

  for (const date in teamSchedule[selectedTeam.value]) {
    if (date !== 'num_employee') {
      const departmentStrength = teamSchedule[selectedTeam.value].num_employee;
      const AMCount = teamSchedule[selectedTeam.value][date].AM.length;
      const PMCount = teamSchedule[selectedTeam.value][date].PM.length;
      const FullCount = teamSchedule[selectedTeam.value][date].Full.length;
      const inOfficeCount = departmentStrength - AMCount - PMCount - FullCount;

      const inOfficeStaffNames = Object.values(employeesByDept[selectedTeam.value] || {})
        .map(staff => staff.staff_name)
        .filter(staffName =>
          !teamSchedule[selectedTeam.value][date].AM.some(s => s.name === staffName) &&
          !teamSchedule[selectedTeam.value][date].PM.some(s => s.name === staffName) &&
          !teamSchedule[selectedTeam.value][date].Full.some(s => s.name === staffName)
        );

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
            inOfficeStaffNames: inOfficeStaffNames,
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
  fetchAndDisplayData(staff_id);
});
</script>

<template>
  <div class="container-fluid d-flex mt-4">
    <section class="flex-grow-1">
      <FullCalendar :options="calendarOptions" />
      <v-dialog v-model="showDialog" max-width="70%">
        <v-card>
          <v-card-title>Staff</v-card-title>
          <v-card-text>
            <!-- Search box to search for staff names -->
            <div class="search-container">
              <v-text-field
                v-model="searchTerm"
                label="Search Staff Names"
                outlined
                dense
                hide-details
              ></v-text-field>
            </div>
            <div class= "names-list">
                <div v-if="clickedEventDetails.amCount">
                <ul>
                    <li v-for="(name, index) in filteredAMStaffNames" :key="index">{{ name }}</li>
                </ul>
                </div>
                <div v-if="clickedEventDetails.pmCount">
                <ul>
                    <li v-for="(name, index) in filteredPMStaffNames" :key="index">{{ name }}</li>
                </ul>
                </div>
                <div v-if="clickedEventDetails.fullCount">
                <ul>
                    <li v-for="(name, index) in filteredFullStaffNames" :key="index">{{ name }}</li>
                </ul>
                </div>
                <div v-if="clickedEventDetails.inOfficeCount">
                <ul>
                    <li v-for="(name, index) in filteredInOfficeStaffNames" :key="index">{{ name }}</li>
                </ul>
                </div>
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

.search-container {
  position: sticky;
  top: 0;
  background-color: white; 
  z-index: 1; /* Keep it above the scrollable list */
  padding-bottom: 10px; 
}

.names-list {
  max-height: 200px; 
  overflow-y: auto; 
  padding-top: 10px; 
 
}
</style>
