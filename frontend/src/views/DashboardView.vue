<script setup>
import MapComponent from '@/components/MapComponent.vue'
import StatsCard from '@/components/StatsCard.vue'
import { ref as vueRef, computed, onMounted, watch } from 'vue'
import { initializeApp } from 'firebase/app'
import { getDatabase, ref as dbRef, onValue } from 'firebase/database'

// --- State Definitions ---
const bins = vueRef([])
const predictions = vueRef({})
const route = vueRef(null)
const loading = vueRef(true)
const selectedFilter = vueRef('all')
const showSidebar = vueRef(true)
const lastUpdate = vueRef(new Date())
const mapComponentRef = vueRef(null) // Reference to MapComponent

// Firebase config (Use the same config as MapComponent, but initialize here for Dashboard data)
const firebaseConfig = {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
    databaseURL: import.meta.env.VITE_FIREBASE_DATABASE_URL,
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
    appId: import.meta.env.VITE_FIREBASE_APP_ID,
}

// --- Computed Statistics (Using the existing, solid logic) ---

const totalBins = computed(() => bins.value.length)
const criticalBins = computed(() => bins.value.filter(bin => Number(bin.fill_level || 0) >= 90).length)
const fullBins = computed(() => bins.value.filter(bin => Number(bin.fill_level || 0) >= 80).length)
const urgentBins = computed(() => {
    return Object.keys(predictions.value).filter(binId => {
        const pred = predictions.value[binId]
        return pred?.time_to_full_h && pred.time_to_full_h <= 12
    }).length
})
const averageFillLevel = computed(() => {
    if (bins.value.length === 0) return 0
    const sum = bins.value.reduce((acc, bin) => acc + Number(bin.fill_level || 0), 0)
    return Math.round(sum / bins.value.length)
})
const routeDistance = computed(() => {
    // Assuming 'total_distance_km' is added by your routing.py
    return route.value?.total_distance_km?.toFixed(1) || 'N/A'
})
const binsInRoute = computed(() => {
    // Assuming 'stops' array has length > 0
    return route.value?.stops?.filter(s => s.bin_id !== 'DEPOT').length || 0
})

// --- Status Info Helper (Simplified Tailwind Classes) ---
const getStatusInfo = (fillLevel, timeToFull) => {
    if (fillLevel >= 90) return { text: 'CRITICAL', color: 'red', bgColor: 'bg-red-100', textColor: 'text-red-700', emoji: '🔴' }
    if (fillLevel >= 80) return { text: 'HIGH', color: 'orange', bgColor: 'bg-orange-100', textColor: 'text-orange-700', emoji: '🟠' }
    if (timeToFull !== null && timeToFull !== undefined && timeToFull <= 6) return { text: 'URGENT', color: 'amber', bgColor: 'bg-amber-100', textColor: 'text-amber-700', emoji: '⚠️' }
    if (fillLevel >= 60) return { text: 'MEDIUM', color: 'yellow', bgColor: 'bg-yellow-100', textColor: 'text-yellow-700', emoji: '🟡' }
    return { text: 'NORMAL', color: 'green', bgColor: 'bg-green-100', textColor: 'text-green-700', emoji: '🟢' }
}

// --- Filtered Bins ---
const filteredBins = computed(() => {
    let filtered = bins.value.map(bin => {
        const prediction = predictions.value[bin.id]
        return {
            ...bin,
            prediction,
            status: getStatusInfo(Number(bin.fill_level), prediction?.time_to_full_h)
        }
    })

    switch(selectedFilter.value) {
        case 'critical':
            filtered = filtered.filter(b => b.fill_level >= 90)
            break
        case 'high':
            filtered = filtered.filter(b => b.fill_level >= 80 && b.fill_level < 90)
            break
        case 'urgent':
            filtered = filtered.filter(b => b.prediction?.time_to_full_h && b.prediction.time_to_full_h <= 12)
            break
        case 'medium':
            filtered = filtered.filter(b => b.fill_level >= 60 && b.fill_level < 80)
            break
        case 'low':
            filtered = filtered.filter(b => b.fill_level < 60)
            break
    }

    return filtered.sort((a, b) => {
        // Sort by fill level descending
        return Number(b.fill_level) - Number(a.fill_level)
    })
})

// Filter options with dynamic counts
const filterOptions = computed(() => [
    { value: 'all', label: 'All Bins', count: totalBins.value, color: 'blue' },
    { value: 'critical', label: 'Critical', count: criticalBins.value, color: 'red' },
    { value: 'high', label: 'High', count: fullBins.value - criticalBins.value, color: 'orange' },
    { value: 'urgent', label: 'Urgent TTF', count: urgentBins.value, color: 'amber' },
    { value: 'medium', label: 'Medium', count: bins.value.filter(b => b.fill_level >= 60 && b.fill_level < 80).length, color: 'yellow' },
    { value: 'low', label: 'Low', count: bins.value.filter(b => b.fill_level < 60).length, color: 'green' }
])

// --- Actions ---
const handleBinClick = (bin) => {
    // Fly to the bin on the map using the exposed function from MapComponent
    if (mapComponentRef.value && bin.latitude && bin.longitude) {
        mapComponentRef.value.flyToBin(Number(bin.latitude), Number(bin.longitude));
    }
}

// --- Lifecycle & Firebase Listeners ---
onMounted(() => {
    const app = initializeApp(firebaseConfig)
    const db = getDatabase(app)

    // Listener setup (from original code, kept simple for consistency)
    const binsRef = dbRef(db, 'bins')
    onValue(binsRef, (snapshot) => {
        const data = snapshot.val()
        if (data) {
            bins.value = Object.keys(data).map(key => ({
                id: key,
                fill_level: Number(data[key].fill_level), // Ensure numeric
                latitude: Number(data[key].latitude),
                longitude: Number(data[key].longitude),
                timestamp: Number(data[key].timestamp),
                ...data[key]
            }))
        } else {
            bins.value = []
        }
        loading.value = false
        lastUpdate.value = new Date()
    })

    const predictionsRef = dbRef(db, 'predictions')
    onValue(predictionsRef, (snapshot) => {
        predictions.value = snapshot.val() || {}
    })

    const routeRef = dbRef(db, 'routes/route_1')
    onValue(routeRef, (snapshot) => {
        route.value = snapshot.val()
    })
})

</script>

<template>
    <div class="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-gray-100">
        <header class="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-700 text-white shadow-2xl sticky top-0 z-50">
            <div class="container mx-auto px-6 py-4">
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-4">
                        <div class="bg-white/20 p-3 rounded-xl">
                            <span class="text-3xl">🗑️</span>
                        </div>
                        <div>
                            <h1 class="text-3xl font-bold">Smart Waste Dashboard</h1>
                            <p class="text-blue-200 mt-0.5 text-sm">Real-time monitoring & AI-powered routing</p>
                        </div>
                    </div>

                    <div class="flex items-center gap-3">
                         <div class="text-xs text-blue-200 text-right hidden sm:block">
                            Last Update:<br>
                            <span class="font-medium text-white">{{ lastUpdate.toLocaleTimeString() }}</span>
                        </div>
                        <button
                            @click="showSidebar = !showSidebar"
                            class="bg-white/20 hover:bg-white/30 px-4 py-2 rounded-xl transition-all duration-300 font-medium text-sm shadow-md"
                        >
                            {{ showSidebar ? '👁️ Hide Sidebar' : '👁️ Show Sidebar' }}
                        </button>
                    </div>
                </div>
            </div>
        </header>

        <div class="container mx-auto px-6 py-6">
            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-5 mb-6">
                <StatsCard
                    title="Total Bins"
                    :value="totalBins"
                    color="blue"
                    icon="📦"
                    :loading="loading"
                    subtitle="Active units"
                />
                <StatsCard
                    title="Critical"
                    :value="criticalBins"
                    color="red"
                    icon="🚨"
                    :loading="loading"
                    subtitle="≥90% full"
                />
                <StatsCard
                    title="Urgent TTF"
                    :value="urgentBins"
                    color="amber"
                    icon="⏱️"
                    :loading="loading"
                    subtitle="<12h to full"
                />
                <StatsCard
                    title="Avg Fill"
                    :value="`${averageFillLevel}%`"
                    color="purple"
                    icon="📊"
                    :loading="loading"
                    subtitle="System-wide"
                />
                <StatsCard
                    title="Route Distance"
                    :value="`${routeDistance} km`"
                    color="green"
                    icon="🛣️"
                    :loading="loading"
                    subtitle="Optimized path"
                />
                <StatsCard
                    title="Route Stops"
                    :value="binsInRoute"
                    color="indigo"
                    icon="🚛"
                    :loading="loading"
                    subtitle="Bins to collect"
                />
            </div>

            <div class="grid grid-cols-1 lg:gap-6" :class="showSidebar ? 'lg:grid-cols-3' : 'lg:grid-cols-1'">
                <div :class="showSidebar ? 'lg:col-span-2' : 'lg:col-span-1'">
                    <div class="bg-white rounded-2xl shadow-xl overflow-hidden h-[700px]">
                        <MapComponent ref="mapComponentRef" />
                    </div>
                </div>

                <transition name="slide-fade">
                    <div v-if="showSidebar" class="space-y-6 lg:col-span-1">
                        <div class="bg-white rounded-2xl shadow-xl p-5 border-t-4 border-gray-200">
                            <h3 class="font-bold text-gray-800 text-lg mb-4 flex items-center gap-2">
                                <span>🔍</span>
                                <span>Filter & Status Breakdown</span>
                            </h3>
                            <div class="grid grid-cols-3 gap-2">
                                <button
                                    v-for="option in filterOptions"
                                    :key="option.value"
                                    @click="selectedFilter = option.value"
                                    :class="[
                                        'p-2 rounded-xl text-xs font-medium transition-all duration-200 flex flex-col items-center justify-center border-2 hover:scale-[1.05]',
                                        selectedFilter === option.value
                                            ? `bg-${option.color}-600 text-white border-${option.color}-700 shadow-md`
                                            : `bg-${option.color}-50 text-${option.color}-700 border-${option.color}-100 hover:bg-${option.color}-100`
                                    ]"
                                >
                                    <span class="font-extrabold text-xl">{{ option.count }}</span>
                                    <span>{{ option.label }}</span>
                                </button>
                            </div>
                        </div>

                        <div class="bg-white rounded-2xl shadow-xl max-h-[450px] overflow-y-auto custom-scroll p-5">
                            <h3 class="font-bold text-gray-800 mb-4 sticky top-0 bg-white pb-2 text-lg z-10 flex items-center gap-2">
                                <span>📋</span>
                                <span>{{ filterOptions.find(o => o.value === selectedFilter).label }} List ({{ filteredBins.length }})</span>
                            </h3>

                            <div class="space-y-3">
                                <div
                                    v-for="bin in filteredBins.slice(0, 50)"
                                    :key="bin.id"
                                    @click="handleBinClick(bin)"
                                    class="border-2 border-gray-100 rounded-xl p-3 hover:shadow-lg hover:border-blue-300 transition-all duration-300 cursor-pointer group"
                                >
                                    <div class="flex justify-between items-center mb-1">
                                        <div class="font-bold text-gray-800 flex items-center gap-2">
                                            <span class="text-xl">{{ bin.status.emoji }}</span>
                                            <span>{{ bin.id }}</span>
                                        </div>
                                        <div :class="[bin.status.bgColor, bin.status.textColor, 'px-2 py-0.5 rounded-full text-xs font-semibold']">
                                            {{ bin.status.text }}
                                        </div>
                                    </div>

                                    <div class="flex justify-between items-center text-sm">
                                        <span class="text-gray-600">Fill:
                                            <strong :class="`text-${bin.status.color}-600`">
                                                {{ bin.fill_level.toFixed(1) }}%
                                            </strong>
                                        </span>
                                        <span v-if="bin.prediction?.time_to_full_h" class="text-gray-600">TTF:
                                            <strong :class="bin.prediction.time_to_full_h <= 12 ? 'text-red-600' : 'text-green-600'">
                                                {{ bin.prediction.time_to_full_h.toFixed(1) }}h
                                            </strong>
                                        </span>
                                        <span v-else class="text-gray-400">TTF: N/A</span>
                                    </div>
                                    <div class="h-1 bg-gray-200 rounded-full mt-1">
                                        <div :style="`width: ${bin.fill_level}%`" :class="`h-full rounded-full bg-${bin.status.color}-500`"></div>
                                    </div>
                                </div>
                            </div>
                             <div v-if="filteredBins.length > 50" class="text-center text-sm text-gray-500 mt-4">
                                Showing top 50 bins.
                            </div>
                        </div>
                    </div>
                </transition>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* Transition for sidebar collapse */
.slide-fade-enter-active,
.slide-fade-leave-active {
    transition: all 0.5s cubic-bezier(0.2, 0.8, 0.2, 1);
}
.slide-fade-enter-from,
.slide-fade-leave-to {
    transform: translateX(20px);
    opacity: 0;
}

/* Custom Scrollbar for list */
.custom-scroll::-webkit-scrollbar {
    width: 8px;
}
.custom-scroll::-webkit-scrollbar-thumb {
    background: #d1d5db; /* gray-300 */
    border-radius: 10px;
}
.custom-scroll::-webkit-scrollbar-track {
    background: #f3f4f6; /* gray-100 */
    border-radius: 10px;
}
</style>
