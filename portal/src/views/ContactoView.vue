<script setup>
  import Contact from '../components/Contact.vue'
</script>
<template>
  <div class="about">
    <Contact />
  </div>
</template>

<style>
@media (min-width: 1024px) {
  .about {
    min-height: 100vh;
    display: flex;
    align-items: center;
  }
}
</style>