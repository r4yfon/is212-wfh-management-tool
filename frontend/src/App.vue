<script setup>
  import { RouterLink, RouterView } from "vue-router";
</script>

<template>
  <header>
    <!-- <div class="wrapper"> -->
    <h1 class="title">WFH Management System</h1>
    <v-menu>
      <template v-slot:activator="{ props }">
        <v-btn icon="mdi-dots-vertical" variant="text" v-bind="props"></v-btn>
      </template>
      <v-list>
        <v-list-item>
          <RouterLink to="/weeklycalendar">Own Weekly Schedule</RouterLink>
        </v-list-item>
      </v-list>
    </v-menu>
    <!-- </div> -->
  </header>
  <div class="content">
    <RouterView />
  </div>
</template>

<style scoped>
  header {
    max-height: 100vh;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 50px;
    background-color: rgb(115, 236, 240);
    z-index: 1000; /* Ensures the header is always on top of other elements */
    width: 100%;
    display: flex;
    justify-content: space-between; /* Space between title and nav */
    align-items: center;
    padding-left: 10px;
  }

  .content {
    padding-top: 30px;
    padding-bottom: 30px;
    height: calc(100vh - 50px);
    width: 100%; /* Ensure content spans full width */
  }

  .logo {
    display: block;
    margin: 0 auto 2rem;
  }

  nav {
    width: 100%;
    font-size: 12px;
    text-align: center;
    margin-top: 2rem;
  }

  nav a.router-link-exact-active {
    color: var(--color-text);
  }

  nav a.router-link-exact-active:hover {
    background-color: transparent;
  }

  nav a {
    display: inline-block;
    padding: 0 1rem;
    border-left: 1px solid var(--color-border);
  }

  nav a:first-of-type {
    border: 0;
  }

  @media (min-width: 1024px) {
    header {
      display: flex;
      place-items: center;
      padding-right: calc(var(--section-gap) / 2);
    }

    .logo {
      margin: 0 2rem 0 0;
    }

    header .wrapper {
      display: flex;
      place-items: flex-start;
      flex-wrap: wrap;
    }

    nav {
      text-align: left;
      margin-left: -1rem;
      font-size: 1rem;

      padding: 1rem 0;
      margin-top: 1rem;
    }
  }
</style>
