<!-- src/components/StatsCard.vue -->
<script setup>
defineProps(['title', 'value', 'color'])
</script>

<template>
  <div class="bg-white rounded-xl shadow-md p-6 text-center">
    <h3 class="text-gray-600 text-sm">{{ title }}</h3>
    <p class="text-4xl font-bold mt-2" :class="`text-${color}-600`">{{ value }}</p>
  </div>
</template>