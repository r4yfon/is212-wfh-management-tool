import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import Vue from 'vue';
import Vuetify from 'vuetify';
import 'vuetify/dist/vuetify.min.css';

Vue.use(Vuetify);

new Vue({
  vuetify: new Vuetify(),
  render: h => h(App),
}).$mount('#app');


// const app = createApp(App)

// app.use(router)

// app.mount('#app')
