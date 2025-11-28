<!-- Previous code block removed: using new implementation below -->

<!-- src/components/MapComponent.vue -->
<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { initializeApp } from 'firebase/app'
import { getDatabase, ref as dbRef, onValue } from 'firebase/database'
import * as L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const bins = ref([])
const map = ref(null)
const mapEl = ref(null)
const mapError = ref(null)

onMounted(() => {
  console.log('MapComponent: onMounted')
  // Fix Leaflet's default icon URLs for Vite so markers show properly
  const iconRetinaUrl = new URL('leaflet/dist/images/marker-icon-2x.png', import.meta.url).href
  const iconUrl = new URL('leaflet/dist/images/marker-icon.png', import.meta.url).href
  const shadowUrl = new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href
  L.Icon.Default.mergeOptions({ iconRetinaUrl, iconUrl, shadowUrl })
  try {
    console.log('MapComponent: creating map container', mapEl.value)
    if (mapEl.value) {
      console.log(
        'MapComponent: mapEl computedHeight=',
        window.getComputedStyle(mapEl.value).height,
      )
      console.log('MapComponent: mapEl boundingClientRect=', mapEl.value.getBoundingClientRect())
    } else {
      console.log('MapComponent: mapEl not set (fallback to id=map)')
    }
    map.value = L.map(mapEl.value || 'map').setView([33.3152, 44.3667], 11)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map.value)
    map.value.invalidateSize()
    console.log('MapComponent: tileLayer added')
  } catch (err) {
    // capture and display error if the map couldn't be created
    console.error('MapComponent: failed to create map or tile layer', err)
    mapError.value = 'Unable to initialize map. See console for details.'
    return
  }
  const firebaseConfig = {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
    databaseURL: import.meta.env.VITE_FIREBASE_DATABASE_URL,
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
    appId: import.meta.env.VITE_FIREBASE_APP_ID,
  }
  // Validate firebase config quickly and log helpful error if missing
  if (!firebaseConfig.projectId || !firebaseConfig.databaseURL) {
    console.error(
      'Firebase config missing projectId or databaseURL. Check your VITE_FIREBASE_* environment variables.',
    )
    return
  }

  let app
  try {
    app = initializeApp(firebaseConfig)
  } catch (err) {
    console.error('Unable to initialize Firebase', err)
    return
  }
  const db = getDatabase(app)
  const binsRef = dbRef(db, 'bins')

  onValue(binsRef, (snapshot) => {
    bins.value = snapshot.val() ? Object.values(snapshot.val()) : []
    console.log('MapComponent: got bins', bins.value.length)
    // Clear old markers (leave tile layer intact)
    map.value.eachLayer((layer) => {
      if (layer instanceof L.Marker || layer instanceof L.CircleMarker) {
        map.value.removeLayer(layer)
      }
    })

    bins.value.forEach((bin) => {
      const color = bin.fill_level < 40 ? 'green' : bin.fill_level < 80 ? 'orange' : 'red'
      L.circleMarker([bin.latitude, bin.longitude], {
        radius: 12,
        color: color,
        fillColor: color,
        fillOpacity: 1,
        weight: 1,
      })
        .addTo(map.value)
        .bindPopup(`Bin ${bin.id}<br>Fill: ${bin.fill_level}%`)
    })
  })
})
onUnmounted(() => {
  if (map.value) {
    map.value.remove()
    map.value = null
  }
})
</script>

<template>
  <div class="map-wrapper">
    <!-- Use the DOM ref and inline height fallback if tailwind isn't configured -->
    <div
      id="map"
      ref="mapEl"
      class="h-96 md:h-screen rounded-lg shadow-lg"
      style="height: 90vh; min-height: 360px; background: #f1f5f9"
    ></div>
    <div v-if="mapError" class="map-error">{{ mapError }}</div>
  </div>
</template>

<style scoped>
.map-error {
  position: absolute;
  z-index: 1000;
  top: 8px;
  left: 8px;
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 4px;
  color: #c53030;
}
</style>
