<template>
  <div id="app">
    <TicketList />
  </div>
</template>

<script setup lang="ts">
import TicketList from './components/TicketList.vue';
</script>

<style>
body {
  font-family: Arial, sans-serif;
  margin: 20px;
  background: #f9f9f9;
}
#app {
  max-width: 900px;
  margin: 0 auto;
}
</style>