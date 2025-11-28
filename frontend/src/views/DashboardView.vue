<!-- src/views/DashboardView.vue -->
<script setup>
import MapComponent from '@/components/MapComponent.vue'
import StatsCard from '@/components/StatsCard.vue'
import {ref as vueRef,computed , onMounted} from 'vue'
import { db,ref, onValue} from '@/firebase.js'

const bins = vueRef([])
const totalBins = computed(() => bins.value.length)
// Use the same key name as in Firebase (fill_level) and coerce to Number
const fullBins = computed(() => bins.value.filter(bin => Number(bin.fill_level || bin.fillLevel || 0) >= 80).length)


onMounted(() => {
  const binsRef = ref(db, 'bins')
  onValue(binsRef, (snapshot) => {
    const data = snapshot.val()
    if (data) {
      bins.value = Object.keys(data).map(key => ({
        id: key,
        ...data[key]
      }))
    } else {
      bins.value = []
    }
  })
})
</script>

<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Header -->
    <header class="bg-blue-600 text-white p-6 shadow-lg">
      <h1 class="text-3xl font-bold">Smart Waste Dashboard</h1>
      <p class="text-blue-100">Real-time monitoring & predictive routing</p>
    </header>

    <!-- Stats Row -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 p-6">
      <StatsCard title="Total Bins" :value="totalBins" color="blue" />
      <StatsCard title="Full Bins" :value="fullBins" color="red" />
      <StatsCard title="Last Update" value="Live" color="purple" />
    </div>

    <!-- Map -->
    <div class="px-6 pb-6">
      <MapComponent />
    </div>
  </div>
</template>