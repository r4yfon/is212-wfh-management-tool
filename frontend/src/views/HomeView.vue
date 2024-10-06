<script setup>
import TheWelcome from '../components/TheWelcome.vue'

fetch(`http://localhost:5002/request_dates/auto_reject`, {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json'
  }
})
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(responseData => {
    console.log('Success');
  })
  .catch(error => console.error('Error updating status:', error));

</script>

<template>
  <main>
    <TheWelcome />
  </main>
</template>
