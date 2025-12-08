<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { initializeApp } from 'firebase/app'
import { getDatabase, ref as dbRef, onValue } from 'firebase/database'
import * as L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet-polylinedecorator' // Used for route arrows

// --- State Definitions ---
const showRoute = ref(true)
const autoRefresh = ref(true) // Not used yet, but kept for future controls
const map = ref(null)
const mapEl = ref(null)
const mapError = ref(null)

const bins = ref([])
const predictions = ref({})
const route = ref(null)

let markersLayer // LayerGroup for bins
let routeLayerGroup // LayerGroup for route elements
let binMarkers = {} // Store marker references for updates
let routeArrows = null

// --- Firebase Config (Ensure environment variables are loaded in main.js) ---
const firebaseConfig = {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
    databaseURL: import.meta.env.VITE_FIREBASE_DATABASE_URL,
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
    appId: import.meta.env.VITE_FIREBASE_APP_ID,
}

// --- Helper Functions ---

const getMarkerColor = (fillLevel, timeToFull) => {
    // Tailwind Color Classes as Hex for JS styling
    if (fillLevel >= 90) return '#dc2626' // red-600 (CRITICAL)
    if (fillLevel >= 80) return '#ea580c' // orange-600 (HIGH)
    if (timeToFull !== null && timeToFull !== undefined && timeToFull <= 6) return '#f59e0b' // amber-500 (URGENT)
    if (fillLevel >= 60) return '#eab308' // yellow-500 (MEDIUM)
    if (fillLevel >= 40) return '#84cc16' // lime-500 (LOW)
    return '#22c55e' // green-500 (NORMAL)
}

const getStatusInfo = (fillLevel, timeToFull) => {
    // Tailwind CSS classes for dynamic status text
    if (fillLevel >= 90) return { text: 'CRITICAL', color: 'bg-red-600', text_color: 'text-red-600', emoji: '🔴' }
    if (fillLevel >= 80) return { text: 'HIGH', color: 'bg-orange-600', text_color: 'text-orange-600', emoji: '🟠' }
    if (timeToFull !== null && timeToFull !== undefined && timeToFull <= 6) return { text: 'URGENT', color: 'bg-amber-500', text_color: 'text-amber-600', emoji: '⚠️' }
    if (fillLevel >= 60) return { text: 'MEDIUM', color: 'bg-yellow-500', text_color: 'text-yellow-600', emoji: '🟡' }
    if (fillLevel >= 40) return { text: 'LOW', color: 'bg-lime-500', text_color: 'text-lime-600', emoji: '🟢' }
    return { text: 'NORMAL', color: 'bg-green-500', text_color: 'text-green-600', emoji: '✅' }
}

// Create clean, Tailwind-styled popup content
const createPopupContent = (bin, prediction) => {
    const timeToFull = prediction?.time_to_full_h
    const fillRate = prediction?.fill_rate
    const status = getStatusInfo(bin.fill_level, timeToFull)
    const predictedAt = prediction?.predicted_at ? new Date(prediction.predicted_at * 1000).toLocaleString() : null

    return `
        <div class="min-w-[260px] font-sans">
            <div class="bg-blue-600 text-white p-4 -mt-4 -mx-5 rounded-t-lg shadow-md flex items-center gap-2">
                <span class="text-xl">🗑️</span>
                <h3 class="text-lg font-bold">${bin.id}</h3>
            </div>

            <div class="p-2">
                <div class="mt-2 mb-4 p-3 rounded-lg font-bold text-center text-sm flex items-center justify-center gap-2
                    ${status.color.replace('bg-', 'bg-')}-100 ${status.text_color} border-l-4 border-${status.color.replace('bg-', '')}-600">
                    <span class="text-xl">${status.emoji}</span>
                    <span>${status.text}</span>
                </div>

                <div class="mb-3">
                    <div class="flex justify-between items-center mb-1">
                        <strong class="text-gray-600 text-sm">Fill Level</strong>
                        <strong class="text-gray-900 text-lg">${bin.fill_level.toFixed(1)}%</strong>
                    </div>
                    <div class="h-4 rounded-full bg-gray-200 overflow-hidden shadow-inner">
                        <div style="width: ${bin.fill_level}%; background-color: ${getMarkerColor(bin.fill_level, timeToFull)};"
                             class="h-full transition-all duration-500 shadow-md">
                        </div>
                    </div>
                </div>

                ${timeToFull !== null && timeToFull !== undefined ? `
                    <div class="mb-3 p-3 rounded-lg bg-gray-50 border-l-4 border-amber-600">
                        <div class="flex items-center gap-2 mb-1">
                            <span class="text-xl">⏱️</span>
                            <strong class="text-gray-600 text-sm">Time to Full (ML)</strong>
                        </div>
                        <div class="text-2xl font-extrabold ${timeToFull <= 6 ? 'text-red-600' : 'text-green-600'}">
                            ${timeToFull.toFixed(1)} hours
                        </div>
                    </div>
                ` : ''}

                ${fillRate !== null && fillRate !== undefined ? `
                    <div class="mb-3 p-2 bg-gray-100 rounded-md flex justify-between items-center text-sm">
                        <div class="flex items-center gap-1 text-gray-600">
                            <span class="text-lg">📈</span>
                            <strong>Fill Rate:</strong>
                        </div>
                        <span class="font-bold text-gray-800">${fillRate.toFixed(2)}% / hour</span>
                    </div>
                ` : ''}

                <div class="text-xs text-gray-500 text-center pt-2 border-t border-gray-200">
                    Lat/Lon: ${bin.latitude.toFixed(5)}, ${bin.longitude.toFixed(5)}
                    <br>
                    Last reading: ${new Date(bin.timestamp * 1000).toLocaleString()}
                </div>
            </div>
        </div>
    `
}

// Draw/Update Bins (uses L.circleMarker and dynamic style for animation)
const drawBins = () => {
    if (!map.value || !markersLayer) return

    const currentBinIds = new Set(bins.value.map(b => b.id))

    // 1. Remove obsolete markers
    Object.keys(binMarkers).forEach(id => {
        if (!currentBinIds.has(id)) {
            markersLayer.removeLayer(binMarkers[id])
            delete binMarkers[id]
        }
    })

    // 2. Add/Update markers
    bins.value.forEach((bin) => {
        const prediction = predictions.value[bin.id]
        const timeToFull = prediction?.time_to_full_h
        const color = getMarkerColor(bin.fill_level, timeToFull)
        // Dynamic radius based on fill level (10px base + 10px max increase)
        const radius = 10 + (bin.fill_level / 100) * 10
        const lat = parseFloat(bin.latitude);
        const lon = parseFloat(bin.longitude);

        if (isNaN(lat) || isNaN(lon)) return;

        const popupContent = createPopupContent(bin, prediction);

        if (binMarkers[bin.id]) {
            // Update existing marker style and position
            binMarkers[bin.id].setStyle({
                radius: radius,
                fillColor: color,
            }).setLatLng([lat, lon]);

            // Re-set the class for the pulse animation if critical
            const currentClassName = binMarkers[bin.id].options.className || '';
            const newClassName = bin.fill_level >= 90 ? 'pulse-marker' : '';
            if (currentClassName !== newClassName) {
                binMarkers[bin.id].options.className = newClassName;
            }

            binMarkers[bin.id].setPopupContent(popupContent);
        } else {
            // Create new marker
            const marker = L.circleMarker([lat, lon], {
                radius: radius,
                color: '#fff', // White border
                fillColor: color,
                fillOpacity: 0.85,
                weight: 2,
                className: bin.fill_level >= 90 ? 'pulse-marker' : ''
            })

            marker.bindPopup(popupContent, {
                maxWidth: 300,
                className: 'custom-popup'
            })

            // Center map on click
            marker.on('click', (e) => {
                map.value.panTo(e.latlng);
            })

            marker.addTo(markersLayer)
            binMarkers[bin.id] = marker
        }
    })
}

// Draw/Update Route
const drawRoute = (routeData) => {
    if (!map.value || !routeLayerGroup) return

    // Clear existing route elements
    routeLayerGroup.clearLayers()
    if (routeArrows) {
        routeArrows.remove()
        routeArrows = null
    }

    if (!showRoute.value || !routeData || !routeData.stops || routeData.stops.length < 2) return

    const stops = routeData.stops
    // Ensure routeCoords are numbers and use latitude/longitude correctly
    const routeCoords = stops.map(s => [parseFloat(s.latitude), parseFloat(s.longitude)])

    // 1. Draw main polyline
    const polyline = L.polyline(routeCoords, {
        color: '#3b82f6', // blue-600
        weight: 6,
        opacity: 0.8,
        lineJoin: 'round',
        lineCap: 'round',
        dashArray: '10, 10', // Animated dash effect
        className: 'route-line'
    }).addTo(routeLayerGroup)

    // 2. Add animated arrows using PolylineDecorator
    routeArrows = L.polylineDecorator(polyline, {
        patterns: [
            {
                offset: '0', // Start at 0
                repeat: 80, // Repeat every 80 pixels
                symbol: L.Symbol.arrowHead({
                    pixelSize: 14,
                    polygon: false,
                    pathOptions: {
                        stroke: true,
                        color: '#1e40af', // blue-800
                        weight: 3,
                        opacity: 0.9
                    }
                })
            }
        ]
    }).addTo(map.value)

    // 3. Add enhanced markers for stops
    stops.forEach((stop, i) => {
        const lat = parseFloat(stop.latitude);
        const lon = parseFloat(stop.longitude);
        if (isNaN(lat) || isNaN(lon)) return;

        let iconHtml, markerClass;

        if (i === 0) { // Start/Depot
            iconHtml = `<div class="route-start-marker">🏢 START</div>`;
            markerClass = 'depot-marker';
        } else if (i === stops.length - 1) { // End/Return
            iconHtml = `<div class="route-end-marker">END</div>`;
            markerClass = 'return-marker';
        } else { // Numbered stop
            // Order is likely 1-indexed for stops, but loop index is 1-indexed after start
            const stopOrder = i;
            iconHtml = `<div class="route-stop-marker">${stopOrder}</div>`;
            markerClass = 'stop-marker';
        }

        const icon = L.divIcon({
            className: markerClass,
            html: iconHtml,
            iconSize: [80, 30],
            iconAnchor: [40, 15]
        });

        const marker = L.marker([lat, lon], { icon })
            .bindPopup(
                `
                <div class="font-sans text-sm p-1">
                    <strong class="text-blue-600">${i === 0 || i === stops.length - 1 ? stop.bin_id || 'DEPOT' : `Stop ${i}: ${stop.bin_id}`}</strong>
                    ${stop.fill_level ? `<br>Fill: ${stop.fill_level.toFixed(1)}%` : ''}
                    ${stop.time_to_full_h ? `<br>TTF: ${stop.time_to_full_h.toFixed(1)}h` : ''}
                </div>
                `
            )
            .addTo(routeLayerGroup);
    });

    // Fit the map to the route bounds when drawing
    map.value.fitBounds(polyline.getBounds(), { padding: [50, 50] });
}

// Add Legend Control (using Tailwind classes in HTML)
const addLegend = () => {
    if (!map.value) return

    const legend = L.control({ position: 'bottomright' })

    legend.onAdd = function() {
        const div = L.DomUtil.create('div', 'map-legend bg-white p-3 rounded-xl shadow-xl border border-gray-100 font-sans text-xs')
        div.innerHTML = `
            <div class="font-bold mb-2 text-gray-800 border-b pb-1">🗑️ Fill Level Status</div>
            <div class="flex items-center gap-2 mb-1">
                <div style="background: #dc2626;" class="w-3 h-3 rounded-full border border-white shadow"></div>
                <span>CRITICAL (&ge;90%)</span>
            </div>
            <div class="flex items-center gap-2 mb-1">
                <div style="background: #ea580c;" class="w-3 h-3 rounded-full border border-white shadow"></div>
                <span>HIGH (&ge;80%)</span>
            </div>
            <div class="flex items-center gap-2 mb-1">
                <div style="background: #f59e0b;" class="w-3 h-3 rounded-full border border-white shadow"></div>
                <span>URGENT (TTF &le;6h)</span>
            </div>
            <div class="flex items-center gap-2 mb-1">
                <div style="background: #22c55e;" class="w-3 h-3 rounded-full border border-white shadow"></div>
                <span>LOW / NORMAL</span>
            </div>
            <div class="font-bold mt-3 mb-2 text-blue-700 border-t pt-2">🚛 Routing</div>
             <div class="flex items-center gap-2">
                <div class="w-4 h-2 bg-blue-600 border border-white shadow"></div>
                <span>Optimized Path</span>
            </div>
        `
        return div
    }

    legend.addTo(map.value)
}

// --- Lifecycle Hooks ---

onMounted(() => {
    // 1. Fix Leaflet default icon path issues
    const iconRetinaUrl = new URL('leaflet/dist/images/marker-icon-2x.png', import.meta.url).href
    const iconUrl = new URL('leaflet/dist/images/marker-icon.png', import.meta.url).href
    const shadowUrl = new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href
    L.Icon.Default.mergeOptions({ iconRetinaUrl, iconUrl, shadowUrl })

    try {
        // 2. Initialize Map
        map.value = L.map(mapEl.value || 'map', {
            zoomControl: true,
            attributionControl: true
        }).setView([33.3152, 44.3667], 11) // Default to Baghdad/Hillah area (Example)

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(map.value)

        // 3. Setup Layers
        markersLayer = L.layerGroup().addTo(map.value)
        routeLayerGroup = L.layerGroup().addTo(map.value)
        addLegend()

    } catch (err) {
        console.error('Failed to create map', err)
        mapError.value = 'Unable to initialize map. Check console for details.'
        return;
    }

    // 4. Initialize Firebase & Listeners
    const app = initializeApp(firebaseConfig)
    const db = getDatabase(app)

    const binsRef = dbRef(db, 'bins')
    onValue(binsRef, snapshot => {
        const data = snapshot.val()
        bins.value = data ? Object.keys(data).map(key => ({ id: key, ...data[key] })) : []
        drawBins()
    })

    const predRef = dbRef(db, 'predictions')
    onValue(predRef, snapshot => {
        predictions.value = snapshot.val() || {}
        drawBins() // Re-draw bins to update popups with new predictions
    })

    const routeRef = dbRef(db, 'routes/route_1')
    onValue(routeRef, snapshot => {
        route.value = snapshot.val()
        drawRoute(route.value)
    })
})

onUnmounted(() => {
    if (map.value) {
        map.value.remove()
        map.value = null
    }
})

// Watchers
watch(showRoute, () => drawRoute(route.value))

// Expose functions for parent component access (e.g., DashboardView clicking a bin)
const flyToBin = (lat, lon) => {
    if (map.value) {
        map.value.flyTo([lat, lon], 15, { duration: 1.5 });
        // Optional: Open the bin's popup if the marker exists
        const binId = bins.value.find(b => parseFloat(b.latitude) === lat && parseFloat(b.longitude) === lon)?.id;
        if (binId && binMarkers[binId]) {
             binMarkers[binId].openPopup();
        }
    }
}
defineExpose({ flyToBin });

</script>

<template>
    <div class="map-wrapper relative h-full w-full">
        <div class="absolute top-4 right-4 z-[1000] flex flex-col gap-3">
            <button
                @click="showRoute = !showRoute"
                :class="[
                    'w-36 px-4 py-2 rounded-xl shadow-lg font-bold transition-all duration-300 transform hover:scale-[1.02] border-2',
                    showRoute
                        ? 'bg-blue-600 text-white border-blue-600 hover:bg-blue-700'
                        : 'bg-white text-blue-600 border-blue-600 hover:bg-blue-50'
                ]"
            >
                <span class="flex items-center justify-center gap-2">
                    <span>{{ showRoute ? '🚛' : '🗺️' }}</span>
                    <span>{{ showRoute ? 'Hide Route' : 'Show Route' }}</span>
                </span>
            </button>

            <button
                @click="map?.fitBounds(markersLayer?.getBounds() || routeLayerGroup?.getBounds(), { padding: [50, 50], maxZoom: 14 })"
                class="w-36 px-4 py-2 bg-white text-gray-700 rounded-xl shadow-lg font-medium transition-all duration-300 transform hover:scale-[1.02] hover:bg-gray-50 border-2 border-gray-200"
                title="Fit all urgent bins or route in view"
            >
                <span class="flex items-center justify-center gap-2">
                    <span>🎯</span>
                    <span>Fit View</span>
                </span>
            </button>
        </div>

        <div v-if="mapError" class="absolute inset-0 z-[1000] bg-red-100/80 backdrop-blur flex items-center justify-center p-8">
            <p class="text-xl font-medium text-red-700">{{ mapError }}</p>
        </div>

        <div id="map" ref="mapEl" class="h-full w-full"></div>
    </div>
</template>

<style>
/* --- Global Leaflet Overrides (Use :root or global styles if scoped fails) --- */
:root {
    --color-blue-600: #2563eb;
    --color-red-600: #dc2626;
}

/* Bin Marker Animations */
@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 0.85; }
    50% { transform: scale(1.15); opacity: 1; }
}
.pulse-marker {
    animation: pulse 2s ease-in-out infinite;
    /* !important to ensure L.circleMarker options don't override */
    border-radius: 50% !important;
}

/* Route Line Animation */
@keyframes routeFlow {
    0% { stroke-dashoffset: 20; }
    100% { stroke-dashoffset: 0; }
}
.route-line {
    animation: routeFlow 1s linear infinite;
    stroke-linecap: round !important;
    stroke-linejoin: round !important;
}

/* Custom Popup Styling */
.custom-popup .leaflet-popup-content-wrapper {
    border-radius: 12px;
    padding: 0;
    box-shadow: 0 8px 24px rgba(0,0,0,0.25);
    border: none;
}
.custom-popup .leaflet-popup-content {
    margin: 0;
    padding: 0;
}
.custom-popup .leaflet-popup-tip {
    background: white;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

/* --- Route Marker Styles (Tailwind look with fixed sizes) --- */

.route-start-marker {
    background: linear-gradient(135deg, var(--color-blue-600), #1e40af); /* blue-800 */
    color: white;
    padding: 6px 10px;
    border-radius: 8px;
    font-weight: bold;
    font-size: 13px;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
    border: 3px solid white;
    white-space: nowrap;
}

.route-end-marker {
    background: linear-gradient(135deg, var(--color-red-600), #991b1b); /* red-800 */
    color: white;
    padding: 6px 10px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    box-shadow: 0 3px 8px rgba(239, 68, 68, 0.4);
    border: 2px solid white;
}

.route-stop-marker {
    background: linear-gradient(135deg, #3b82f6, var(--color-blue-600));
    color: white;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: bold;
    box-shadow: 0 3px 8px rgba(59, 130, 246, 0.5);
    border: 2px solid white;
    min-width: 28px;
    text-align: center;
}
</style>
