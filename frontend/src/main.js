import "./assets/main.css";

import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";

// Vuetify imports
import "vuetify/styles"; // Import Vuetify styles
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import { VCalendar } from "vuetify/labs/VCalendar";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.bundle.min.js";

// Create Vuetify instance
const vuetify = createVuetify({
  components: {
    ...components,
    VCalendar, // Register VCalendar here
  },
  directives,
  defaults: {
    global: {
      ripple: false,
    },
  },
});

const app = createApp(App);

// Use Vuetify and router with the Vue app
app.use(vuetify); // Add Vuetify to the app
app.use(router); // Add router to the app

// Mount the Vue app
app.mount("#app");
