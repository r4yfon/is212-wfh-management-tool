import { createApp } from "vue";
import { createPinia } from "pinia";
import piniaPluginPersistedstate from "pinia-plugin-persistedstate";
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
import "./assets/base.css";

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
    VLabel: {
      style: "color: black;",
    },
  },
});

const app = createApp(App);
const pinia = createPinia();
pinia.use(piniaPluginPersistedstate); // Add persisted state plugin
// Use Vuetify and router with the Vue app
app.use(vuetify); // Add Vuetify to the app
app.use(pinia);
app.use(router); // Add router to the app

// Mount the Vue app
app.mount("#app");
