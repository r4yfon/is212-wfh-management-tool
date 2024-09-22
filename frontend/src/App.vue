<template>

  <v-container>
    <v-btn color="success" @click="onClick" border="1px">
      Click Me
    </v-btn>
  </v-container>

</template>

<script>
  export default {
    methods: {
      onClick() {
        alert('Button Clicked!');
      }
    }
  };
  </script>
