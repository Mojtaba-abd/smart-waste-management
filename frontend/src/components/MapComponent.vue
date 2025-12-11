<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { initializeApp } from 'firebase/app'
import { getDatabase, ref as dbRef, onValue } from 'firebase/database'
import * as L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet-polylinedecorator'

// --- State ---
const showRoute = ref(true)
const map = ref(null)
const mapEl = ref(null)
const mapError = ref(null)

const bins = ref([])
const predictions = ref({})
const route = ref(null)

let markersLayer = null
let routeLayerGroup = null
let binMarkers = {}
let routeArrows = null

// --- Firebase Config ---
const firebaseConfig = {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
    databaseURL: import.meta.env.VITE_FIREBASE_DATABASE_URL,
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
    appId: import.meta.env.VITE_FIREBASE_APP_ID,
}

// --- Helpers ---

const getMarkerColor = (fillLevel) => {
    const level = Number(fillLevel) || 0
    if (level >= 90) return '#dc2626' // red-600
    if (level >= 80) return '#ea580c' // orange-600
    if (level >= 60) return '#eab308' // yellow-500
    if (level >= 40) return '#84cc16' // lime-500
    return '#22c55e' // green-500
}

const getStatusInfo = (fillLevel, timeToFull) => {
    const level = Number(fillLevel) || 0
    const ttf = Number(timeToFull)

    // Logic for color/text
    if (level >= 90) return { text: 'CRITICAL', bg: 'bg-red-100', textCol: 'text-red-700', border: 'border-red-600', emoji: '🔴' }
    if (level >= 80) return { text: 'HIGH', bg: 'bg-orange-100', textCol: 'text-orange-700', border: 'border-orange-600', emoji: '🟠' }
    if (timeToFull !== null && ttf <= 6) return { text: 'URGENT', bg: 'bg-amber-100', textCol: 'text-amber-700', border: 'border-amber-600', emoji: '⚠️' }
    if (level >= 60) return { text: 'MEDIUM', bg: 'bg-yellow-100', textCol: 'text-yellow-700', border: 'border-yellow-600', emoji: '🟡' }

    return { text: 'NORMAL', bg: 'bg-green-100', textCol: 'text-green-700', border: 'border-green-600', emoji: '✅' }
}

// --- Popup Content Generator (Tailwind Styled) ---
const createPopupContent = (bin, prediction) => {
    // 🛡️ SECURITY: Force conversion to Number to prevent .toFixed crash
    const fillLevel = Number(bin.fill_level) || 0
    const lat = Number(bin.latitude) || 0
    const lon = Number(bin.longitude) || 0

    const timeToFull = prediction?.time_to_full_h !== undefined ? Number(prediction.time_to_full_h) : null
    const fillRate = prediction?.fill_rate !== undefined ? Number(prediction.fill_rate) : null

    const status = getStatusInfo(fillLevel, timeToFull)
    const lastUpdate = bin.timestamp ? new Date(bin.timestamp * 1000).toLocaleString() : 'N/A'

    // We build the HTML string using Tailwind classes
    return `
        <div class="min-w-[240px] font-sans text-gray-800">
            <div class="bg-blue-600 text-white px-4 py-3 rounded-t-lg flex items-center gap-2 -mx-5 -mt-4 mb-3">
                <span class="text-lg">🗑️</span>
                <h3 class="font-bold text-lg">${bin.id}</h3>
            </div>

            <div class="flex items-center justify-center gap-2 px-3 py-2 rounded-lg font-bold text-sm mb-4 border-l-4 ${status.bg} ${status.textCol} ${status.border}">
                <span class="text-lg">${status.emoji}</span>
                <span>${status.text}</span>
            </div>

            <div class="mb-4">
                <div class="flex justify-between items-end mb-1">
                    <span class="text-xs font-semibold text-gray-500 uppercase">Fill Level</span>
                    <span class="text-xl font-extrabold text-gray-900">${fillLevel.toFixed(1)}%</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-3">
                    <div class="h-3 rounded-full transition-all duration-500"
                         style="width: ${fillLevel}%; background-color: ${getMarkerColor(fillLevel)}">
                    </div>
                </div>
            </div>

            ${timeToFull !== null ? `
            <div class="mb-3 p-3 bg-gray-50 rounded-lg border border-gray-100">
                <div class="flex items-center gap-1 mb-1">
                    <span class="text-base">⏱️</span>
                    <span class="text-xs font-semibold text-gray-500 uppercase">Time to Full</span>
                </div>
                <div class="text-xl font-bold ${timeToFull <= 6 ? 'text-red-600' : 'text-emerald-600'}">
                    ${timeToFull.toFixed(1)} <span class="text-sm font-normal text-gray-500">hours</span>
                </div>
            </div>
            ` : ''}

            <div class="mt-3 pt-3 border-t border-gray-100 text-[10px] text-gray-400 text-center leading-tight">
                <div>${lat.toFixed(5)}, ${lon.toFixed(5)}</div>
                <div class="mt-1">Updated: ${lastUpdate}</div>
            </div>
        </div>
    `
}

// --- Map Logic ---

const drawBins = () => {
    if (!map.value || !markersLayer) return

    // 1. Cleanup old markers
    const currentIds = new Set(bins.value.map(b => b.id))
    Object.keys(binMarkers).forEach(id => {
        if (!currentIds.has(id)) {
            markersLayer.removeLayer(binMarkers[id])
            delete binMarkers[id]
        }
    })

    // 2. Add/Update markers
    bins.value.forEach(bin => {
        // Safe casting
        const fill = Number(bin.fill_level) || 0
        const lat = Number(bin.latitude)
        const lon = Number(bin.longitude)

        if (isNaN(lat) || isNaN(lon)) return

        const prediction = predictions.value[bin.id]
        const color = getMarkerColor(fill)
        const radius = 8 + (fill / 100) * 8 // 8px to 16px
        const popup = createPopupContent(bin, prediction)

        if (binMarkers[bin.id]) {
            // Update existing
            binMarkers[bin.id].setLatLng([lat, lon])
            binMarkers[bin.id].setStyle({ fillColor: color, radius: radius })
            binMarkers[bin.id].setPopupContent(popup)

            // Toggle pulse class
            const el = binMarkers[bin.id].getElement()
            if (el) {
                if (fill >= 90) el.classList.add('pulse-marker')
                else el.classList.remove('pulse-marker')
            }
        } else {
            // Create new
            const marker = L.circleMarker([lat, lon], {
                radius: radius,
                fillColor: color,
                color: 'white',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.9,
                className: fill >= 90 ? 'pulse-marker' : ''
            })

            marker.bindPopup(popup, { minWidth: 260, className: 'tailwind-popup' })
            marker.on('click', (e) => map.value.setView(e.latlng, map.value.getZoom()))

            markersLayer.addLayer(marker)
            binMarkers[bin.id] = marker
        }
    })
}

const drawRoute = (routeData) => {
    if (!map.value || !routeLayerGroup) return
    routeLayerGroup.clearLayers()
    if (routeArrows) { routeArrows.remove(); routeArrows = null; }

    if (!showRoute.value || !routeData || !routeData.stops) return

    const latLngs = routeData.stops.map(s => [Number(s.latitude), Number(s.longitude)])
    if (latLngs.length < 2) return

    // Polyline
    const polyline = L.polyline(latLngs, {
        color: '#3b82f6', // blue-500
        weight: 5,
        opacity: 0.8,
        lineCap: 'round',
        lineJoin: 'round',
        dashArray: '12, 12'
    }).addTo(routeLayerGroup)

    // Arrows
    try {
        routeArrows = L.polylineDecorator(polyline, {
            patterns: [{
                offset: '5%', repeat: '100px',
                symbol: L.Symbol.arrowHead({ pixelSize: 12, polygon: false, pathOptions: { stroke: true, color: '#1d4ed8', weight: 3 } })
            }]
        }).addTo(map.value)
    } catch (e) { console.warn("PolylineDecorator error:", e) }

    // Markers (Start/End/Stops)
    routeData.stops.forEach((stop, i) => {
        const isStart = i === 0
        const isEnd = i === routeData.stops.length - 1
        const lat = Number(stop.latitude)
        const lon = Number(stop.longitude)

        let html = ''
        if (isStart) html = `<div class="bg-blue-700 text-white font-bold px-2 py-1 rounded shadow text-xs border-2 border-white">START</div>`
        else if (isEnd) html = `<div class="bg-red-600 text-white font-bold px-2 py-1 rounded shadow text-xs border-2 border-white">END</div>`
        else html = `<div class="bg-blue-500 text-white font-bold w-6 h-6 rounded-full flex items-center justify-center shadow border-2 border-white text-xs">${i}</div>`

        const icon = L.divIcon({ className: 'bg-transparent border-0', html, iconSize: [40, 40], iconAnchor: [20, 20] })
        L.marker([lat, lon], { icon }).addTo(routeLayerGroup)
    })

    map.value.fitBounds(polyline.getBounds(), { padding: [50, 50] })
}

// --- Lifecycle ---

onMounted(() => {
    // 1. Init Map
    try {
        map.value = L.map(mapEl.value, { zoomControl: false }).setView([33.3152, 44.3667], 12)
        L.control.zoom({ position: 'bottomright' }).addTo(map.value)

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap',
            maxZoom: 19
        }).addTo(map.value)

        markersLayer = L.layerGroup().addTo(map.value)
        routeLayerGroup = L.layerGroup().addTo(map.value)
    } catch (e) {
        mapError.value = "Map Error: " + e.message
        return
    }

    // 2. Firebase Listener
    const app = initializeApp(firebaseConfig)
    const db = getDatabase(app)

    // Bins Listener (CRITICAL FIX FOR DATA TYPES)
    onValue(dbRef(db, 'bins'), (snap) => {
        const val = snap.val()
        if (val) {
            bins.value = Object.keys(val).map(key => ({
                id: key,
                ...val[key],
                // 🛠️ CRITICAL FIX: Cast to Number immediately
                fill_level: Number(val[key].fill_level) || 0,
                latitude: Number(val[key].latitude) || 0,
                longitude: Number(val[key].longitude) || 0,
                timestamp: Number(val[key].timestamp) || 0
            }))
        } else {
            bins.value = []
        }
        drawBins()
    })

    // Predictions & Route Listeners
    onValue(dbRef(db, 'predictions'), snap => { predictions.value = snap.val() || {}; drawBins() })
    onValue(dbRef(db, 'routes/route_1'), snap => { route.value = snap.val(); drawRoute(route.value) })
})

onUnmounted(() => { if (map.value) map.value.remove() })
watch(showRoute, () => drawRoute(route.value))

defineExpose({
    flyToBin: (lat, lon) => {
        if (map.value && lat && lon) map.value.flyTo([lat, lon], 16)
    }
})
</script>

<template>
    <div class="relative w-full h-full bg-gray-100 rounded-xl overflow-hidden shadow-inner">
        <div v-if="mapError" class="absolute inset-0 z-50 flex items-center justify-center bg-red-50 p-4">
            <div class="text-red-600 font-bold">{{ mapError }}</div>
        </div>

        <div ref="mapEl" class="w-full h-full z-0"></div>

        <div class="absolute top-4 right-4 z-[400] flex flex-col gap-2">
            <button @click="showRoute = !showRoute"
                class="bg-white hover:bg-gray-50 text-blue-600 font-bold py-2 px-4 rounded-lg shadow-lg border border-blue-100 transition-transform active:scale-95 flex items-center gap-2">
                <span>{{ showRoute ? '🚛' : '🗺️' }}</span>
                <span>{{ showRoute ? 'Hide Route' : 'Show Route' }}</span>
            </button>

            <button @click="map?.fitBounds(markersLayer?.getBounds())"
                class="bg-white hover:bg-gray-50 text-gray-700 font-bold py-2 px-4 rounded-lg shadow-lg border border-gray-100 transition-transform active:scale-95 flex items-center gap-2">
                <span>🎯</span>
                <span>Center View</span>
            </button>
        </div>
    </div>
</template>

<style>
/* Leaflet Global Styles */
.leaflet-popup-content-wrapper {
    @apply rounded-xl shadow-xl p-0 border-0;
}
.leaflet-popup-content {
    @apply m-0 p-0 w-auto !important;
}

/* Pulse Animation for Critical Bins */
@keyframes pulse-ring {
    0% { transform: scale(0.8); opacity: 0.8; }
    100% { transform: scale(2.5); opacity: 0; }
}
.pulse-marker {
    animation: pulse-ring 2s cubic-bezier(0.215, 0.61, 0.355, 1) infinite;
    transform-origin: center;
}
</style>
