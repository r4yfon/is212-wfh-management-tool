<script setup>
import { RouterLink, RouterView } from 'vue-router'
// import { VTextField, VDatePicker, VBtn, VDialog, VCard, VCardTitle, VCardText, VCardActions, VSpacer } from 'vuetify/components'; 
import { ref, reactive } from 'vue';

// State variables
const dialog = ref(false);
const newEvent = reactive({
  reason: '',
});
const events = ref([]);

const confirmWithdraw = () => {
  if (newEvent.reason) {
    const event = {
      reason: newEvent.reason,
      color: 'blue',
    };

    events.value.push(event); // Add new event to the calendar

    // Clear the form fields
    Object.assign(newEvent, {
      reason: '',
    });

    dialog.value = false
  }
};
</script>

<template>
    <v-dialog v-model="dialog" max-width="400px">
        <template v-slot:activator="{ props: activatorProps }">
          <v-btn
            v-bind="activatorProps"
            color="purple"
            text="Withdraw"
            variant="flat"
          ></v-btn>
        </template>

        <v-card title="Reason for Withdrawal">
          <v-card-text>
            <v-form>
              <!-- reason -->
              <v-text-field v-model="newEvent.reason" required></v-text-field>

            </v-form>
          </v-card-text>

          <v-card-actions>
            <v-spacer></v-spacer>

            <v-btn color="orange darken-1" text @click="confirmWithdraw">
              Apply
            </v-btn>
            <v-btn color="red darken-1" text @click="dialog = false">
              Cancel
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
</template>