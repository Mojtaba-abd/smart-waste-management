<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  LayoutDashboard, Map as MapIcon, Truck, BarChart3, Bell, Menu,
  Wifi, AlertTriangle, Cpu, LogOut, X, Loader2, Brain, Zap, Clock,
  PieChart, Activity, Eye, EyeOff
} from 'lucide-vue-next'

import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

// Import Firebase
import { db, ref as dbRef, onValue } from '@/firebase'

// Shadcn Components
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Progress } from '@/components/ui/progress'

const router = useRouter()
const isSidebarOpen = ref(false)
const toggleSidebar = () => isSidebarOpen.value = !isSidebarOpen.value

// --- NAVIGATION ---
const currentTab = ref('overview')

// --- DATA STATE ---
const bins = ref([])
const chartHistory = ref([])
const predictions = ref([])
const activeRoute = ref(null)
const mapInstance = ref(null)
const mapMarkers = ref([])
const routePolyline = ref(null)

// --- UI STATE ---
const isOptimizing = ref(false)
const isPredicting = ref(false)
const showRoute = ref(true) // NEW: Controls route visibility

// --- COMPUTED STATS ---
const activeSensors = computed(() => bins.value.length)
const criticalBins = computed(() => bins.value.filter(b => b.status === 'Critical').length)

const systemLoad = computed(() => {
  if (bins.value.length === 0) return 0
  const totalFill = bins.value.reduce((acc, b) => acc + b.fillLevel, 0)
  return Math.round(totalFill / bins.value.length)
})

const statusDist = computed(() => {
  const critical = bins.value.filter(b => b.status === 'Critical').length
  const warning = bins.value.filter(b => b.status === 'Warning').length
  const normal = bins.value.filter(b => b.status === 'Normal').length
  return [critical, warning, normal]
})

const weeklyStats = [
  { day: 'Mon', vol: 45 }, { day: 'Tue', vol: 62 }, { day: 'Wed', vol: 55 },
  { day: 'Thu', vol: 78 }, { day: 'Fri', vol: 90 }, { day: 'Sat', vol: 30 }, { day: 'Sun', vol: 25 }
]

// --- API ACTIONS ---
const handleOptimize = async () => {
  isOptimizing.value = true
  try {
    const response = await fetch('http://127.0.0.1:5000/run-optimization', { method: 'POST' })
    const data = await response.json()
    if (data.status === 'success') {
        alert("✅ Routes Optimized!")
        showRoute.value = true // Auto-show route when updated
    }
    else alert("❌ Error: " + data.message)
  } catch (error) { alert("❌ Is 'python api.py' running?") }
  finally { isOptimizing.value = false }
}

const handlePredict = async () => {
  isPredicting.value = true
  try {
    const response = await fetch('http://127.0.0.1:5000/run-inference', { method: 'POST' })
    const data = await response.json()
    if (data.status === 'success') alert("✅ AI Predictions Updated!")
    else alert("❌ Error: " + data.message)
  } catch (error) { alert("❌ Is 'python api.py' running?") }
  finally { isPredicting.value = false }
}

// --- MAP LOGIC ---
const initMap = () => {
  if (mapInstance.value) return;

  nextTick(() => {
    const mapContainer = document.getElementById('map')
    if (!mapContainer) return

    const startLat = bins.value.length > 0 ? bins.value[0].rawLat : 33.3152
    const startLng = bins.value.length > 0 ? bins.value[0].rawLng : 44.3661

    mapInstance.value = L.map('map').setView([startLat, startLng], 13)

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; CARTO',
      maxZoom: 20
    }).addTo(mapInstance.value)

    setTimeout(() => { mapInstance.value.invalidateSize() }, 200)

    updateMapMarkers()
    drawRoute()
  })
}

// 1. Draw Bin Dots
const updateMapMarkers = () => {
  if (!mapInstance.value) return

  mapMarkers.value.forEach(marker => marker.remove())
  mapMarkers.value = []

  const getIcon = (fill) => {
    const color = fill >= 90 ? '#ef4444' : (fill >= 70 ? '#f59e0b' : '#10b981')
    return L.divIcon({
      className: 'custom-div-icon',
      html: `<div style="background-color: ${color}; width: 12px; height: 12px; border-radius: 50%; box-shadow: 0 0 10px ${color}; border: 2px solid white;"></div>`,
      iconSize: [12, 12],
      iconAnchor: [6, 6]
    })
  }

  const bounds = L.latLngBounds()

  bins.value.forEach(bin => {
    if (bin.rawLat && bin.rawLng) {
      const marker = L.marker([bin.rawLat, bin.rawLng], { icon: getIcon(bin.fillLevel) })
        .bindPopup(`<b>${bin.id}</b><br>Fill: ${bin.fillLevel}%`)
        .addTo(mapInstance.value)
      mapMarkers.value.push(marker)
      bounds.extend([bin.rawLat, bin.rawLng])
    }
  })

  if (!activeRoute.value && mapMarkers.value.length > 0) {
    mapInstance.value.fitBounds(bounds, { padding: [50, 50] })
  }
}

// 2. Draw Route (Controlled by showRoute)
const drawRoute = () => {
  if (!mapInstance.value) return

  // Always remove old line first
  if (routePolyline.value) {
    routePolyline.value.remove()
    routePolyline.value = null
  }

  // If hidden or no route, stop here
  if (!showRoute.value || !activeRoute.value) return

  const path = activeRoute.value.map(stop => [stop.latitude, stop.longitude])

  if (path.length > 0) {
    routePolyline.value = L.polyline(path, { color: '#0ea5e9', weight: 4, opacity: 0.8 }).addTo(mapInstance.value)
    mapInstance.value.fitBounds(routePolyline.value.getBounds(), { padding: [50, 50] })
  }
}

// Watchers
watch(currentTab, (newTab) => {
  if (newTab === 'map') setTimeout(initMap, 100)
  else if (mapInstance.value) {
      mapInstance.value.remove()
      mapInstance.value = null
  }
})

watch(bins, () => { if (currentTab.value === 'map') updateMapMarkers() }, { deep: true })
watch(activeRoute, () => { if (currentTab.value === 'map') drawRoute() }, { deep: true })
watch(showRoute, () => { if (currentTab.value === 'map') drawRoute() }) // Redraw when toggled


// --- HELPERS (Placed at bottom to keep logic clean) ---
const getStatus = (fill) => {
  if (fill >= 90) return 'Critical'
  if (fill >= 70) return 'Warning'
  return 'Normal'
}
const timeAgo = (timestamp) => {
  if (!timestamp) return 'Offline'
  const seconds = Math.floor((new Date() - new Date(timestamp * 1000)) / 1000)
  if (seconds < 60) return Math.floor(seconds) + "s ago"
  return Math.floor(seconds / 60) + "m ago"
}
const getBatteryLevel = (idStr) => {
  let hash = 0;
  for (let i = 0; i < idStr.length; i++) hash = idStr.charCodeAt(i) + ((hash << 5) - hash);
  return Math.abs(hash % 80) + 20;
}
const getPoints = (type, height = 100, width = 100) => {
  if (chartHistory.value.length === 0) return ""
  const maxVal = 100
  const stepX = width / (chartHistory.value.length - 1)
  return chartHistory.value.map((d, i) => {
    const val = type === 'actual' ? d.actual : (d.actual + (Math.random() * 10 - 5))
    const x = i * stepX
    const y = height - (val / maxVal) * height
    return `${x},${y}`
  }).join(' ')
}
const getDonutPath = (index, total, counts, radius = 40) => {
  if (total === 0) return ""
  const center = 50
  let startAngle = 0
  for(let i=0; i<index; i++) startAngle += (counts[i]/total) * 360
  const sliceAngle = (counts[index]/total) * 360
  const endAngle = startAngle + sliceAngle
  const startRad = (startAngle - 90) * Math.PI / 180
  const endRad = (endAngle - 90) * Math.PI / 180
  const x1 = center + radius * Math.cos(startRad)
  const y1 = center + radius * Math.sin(startRad)
  const x2 = center + radius * Math.cos(endRad)
  const y2 = center + radius * Math.sin(endRad)
  const largeArcFlag = sliceAngle > 180 ? 1 : 0
  return `M ${center} ${center} L ${x1} ${y1} A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2} Z`
}
const setTab = (tab) => {
  currentTab.value = tab
  if (window.innerWidth < 1024) isSidebarOpen.value = false
}

// --- FIREBASE LISTENERS ---
onMounted(() => {
  onValue(dbRef(db, 'bins'), (snapshot) => {
    const data = snapshot.val()
    if (data) {
      bins.value = Object.keys(data).map(key => ({
        id: key,
        rawLat: data[key].latitude || 0,
        rawLng: data[key].longitude || 0,
        location: `Lat: ${data[key].latitude?.toFixed(4)}, Lng: ${data[key].longitude?.toFixed(4)}`,
        fillLevel: Math.round(data[key].fill_level || 0),
        battery: getBatteryLevel(key),
        status: getStatus(data[key].fill_level || 0),
        lastUpdate: timeAgo(data[key].timestamp),
        timestamp: data[key].timestamp
      })).sort((a, b) => b.fillLevel - a.fillLevel)
    }
  })
  onValue(dbRef(db, 'predictions'), (snapshot) => {
    const data = snapshot.val()
    if (data) {
      predictions.value = Object.keys(data).map(key => ({
        id: key,
        timeToFull: parseFloat(data[key].time_to_full_h).toFixed(1),
        currentFill: Math.round(data[key].fill_level),
        fillRate: parseFloat(data[key].fill_rate).toFixed(2),
        updatedAt: timeAgo(data[key].predicted_at),
        status: getStatus(data[key].fill_level)
      })).sort((a, b) => a.timeToFull - b.timeToFull)
    }
  })
  onValue(dbRef(db, 'routes'), (snapshot) => {
    const allRoutes = snapshot.val()
    if (allRoutes) {
      const routeList = Object.values(allRoutes).filter(route => route.stops && route.stops.length > 0).sort((a, b) => b.created_at - a.created_at)
      if (routeList.length > 0) {
        const latestRoute = routeList[0]
        activeRoute.value = Array.isArray(latestRoute.stops) ? latestRoute.stops : Object.values(latestRoute.stops)
      } else { activeRoute.value = null }
    }
  })
  onValue(dbRef(db, 'history'), (snapshot) => {
    const data = snapshot.val()
    if (data) {
      const dates = Object.keys(data).sort((a, b) => Number(a) - Number(b))
      const latestDate = dates[dates.length - 1]
      if (latestDate && data[latestDate]) {
        const binIds = Object.keys(data[latestDate])
        const firstBin = binIds[0]
        if (firstBin) {
          const historyData = data[latestDate][firstBin]
          const entries = Object.entries(historyData).sort((a, b) => a[0] - b[0]).slice(-10)
          chartHistory.value = entries.map(([ts, val]) => ({
            time: new Date(ts * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            actual: typeof val === 'object' ? (val.fill_level || 0) : val
          }))
        }
      }
    }
  })
})
</script>

<template>
  <div class="min-h-screen bg-gray-950 text-white font-sans flex overflow-hidden">

    <aside class="fixed inset-y-0 left-0 z-50 w-64 bg-black border-r border-gray-800 transition-transform duration-300 flex flex-col lg:static lg:translate-x-0" :class="isSidebarOpen ? 'translate-x-0' : '-translate-x-full'">
      <div class="h-20 flex items-center px-6 border-b border-gray-800 justify-between">
        <div class="flex items-center gap-3">
           <div class="w-8 h-8 bg-gradient-to-br from-emerald-500 to-cyan-500 rounded-lg flex items-center justify-center text-gray-900 font-bold shadow-lg shadow-emerald-500/20">E</div>
           <span class="text-xl font-bold text-white tracking-wide">Enki <span class="text-xs text-emerald-500 font-normal">v1.0</span></span>
        </div>
        <button @click="toggleSidebar" class="lg:hidden text-gray-400 hover:text-white"><X class="w-6 h-6" /></button>
      </div>
      <nav class="flex-1 px-4 py-6 space-y-2">
        <div class="px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Overview</div>
        <button @click="setTab('overview')" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition" :class="currentTab === 'overview' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'text-gray-400 hover:bg-gray-900 hover:text-white'"><LayoutDashboard class="w-5 h-5" /> Dashboard</button>
        <button @click="setTab('map')" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition" :class="currentTab === 'map' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'text-gray-400 hover:bg-gray-900 hover:text-white'"><MapIcon class="w-5 h-5" /> Live Map</button>
        <div class="px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2 mt-6">Hardware & AI</div>
        <button @click="setTab('fleet')" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition" :class="currentTab === 'fleet' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'text-gray-400 hover:bg-gray-900 hover:text-white'"><Truck class="w-5 h-5" /> Fleet & Routes</button>
        <button @click="setTab('ml')" class="w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition" :class="currentTab === 'ml' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'text-gray-400 hover:bg-gray-900 hover:text-white'"><BarChart3 class="w-5 h-5" /> ML Predictions</button>
      </nav>
      <div class="p-4 border-t border-gray-800">
        <div class="flex items-center gap-3 px-2 cursor-pointer hover:bg-gray-900 p-2 rounded-lg transition" @click="router.push('/')">
          <Avatar class="h-9 w-9 border border-gray-700"><AvatarImage src="/images/team/hussein.jpg" /><AvatarFallback>M</AvatarFallback></Avatar>
          <div class="flex-1 min-w-0"><p class="text-sm font-medium text-white truncate">Mujtaba</p><p class="text-xs text-gray-500 truncate">Lead Architect</p></div>
          <LogOut class="w-5 h-5 text-gray-500 hover:text-white" />
        </div>
      </div>
    </aside>

    <main class="flex-1 flex flex-col h-screen overflow-hidden relative bg-gray-950">
      <header class="h-20 border-b border-gray-800 bg-gray-950/80 backdrop-blur-md flex items-center justify-between px-6 lg:px-10 z-40">
        <div class="flex items-center gap-4">
          <button @click="toggleSidebar" class="lg:hidden text-gray-400 hover:text-white"><Menu class="w-6 h-6" /></button>
          <h1 class="text-xl font-bold text-white hidden sm:block">{{ currentTab === 'overview' ? 'Command Center' : currentTab === 'map' ? 'Live Map View' : currentTab === 'ml' ? 'AI Analytics' : 'Fleet Management' }}</h1>
        </div>
        <div class="flex items-center gap-4">
          <div class="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
            <span class="relative flex h-2 w-2"><span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span><span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span></span><span class="text-xs font-medium text-emerald-400">Firebase Connected</span>
          </div>
        </div>
      </header>

      <div class="flex-1 overflow-y-auto p-6 lg:p-10 space-y-8">

        <div v-if="currentTab === 'overview'" class="space-y-8 animate-in fade-in duration-500">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card class="bg-gray-900 border-gray-800"><CardHeader class="flex flex-row items-center justify-between pb-2"><CardTitle class="text-sm font-medium text-gray-400">Active Sensors</CardTitle><Cpu class="w-4 h-4 text-emerald-500" /></CardHeader><CardContent><div class="text-2xl font-bold text-white">{{ activeSensors }}</div><p class="text-xs text-gray-500 mt-1">Live from /bins</p></CardContent></Card>
                <Card class="bg-gray-900 border-gray-800"><CardHeader class="flex flex-row items-center justify-between pb-2"><CardTitle class="text-sm font-medium text-gray-400">Critical (>90%)</CardTitle><AlertTriangle class="w-4 h-4 text-red-500" /></CardHeader><CardContent><div class="text-2xl font-bold text-white">{{ criticalBins }}</div><p class="text-xs text-red-400 mt-1">Attention Required</p></CardContent></Card>
                <Card class="bg-gray-900 border-gray-800"><CardHeader class="flex flex-row items-center justify-between pb-2"><CardTitle class="text-sm font-medium text-gray-400">Next Optimization</CardTitle><Brain class="w-4 h-4 text-cyan-500" /></CardHeader><CardContent><div class="text-2xl font-bold text-white">Manual</div><p class="text-xs text-cyan-400 mt-1">AI Ready</p></CardContent></Card>
                <Card class="bg-gray-900 border-gray-800"><CardHeader class="flex flex-row items-center justify-between pb-2"><CardTitle class="text-sm font-medium text-gray-400">System Load</CardTitle><Activity class="w-4 h-4 text-violet-500" /></CardHeader><CardContent><div class="text-2xl font-bold text-white">{{ systemLoad }}%</div><Progress :model-value="systemLoad" class="h-1 mt-2 bg-gray-800" indicator-class="bg-violet-500" /></CardContent></Card>
            </div>
            <div class="grid lg:grid-cols-3 gap-6">
                <Card class="lg:col-span-2 bg-gray-900 border-gray-800">
                    <CardHeader><div class="flex items-center justify-between"><div><CardTitle class="text-white text-lg">Live Fill Trends</CardTitle><CardDescription>Real-time History vs AI Prediction</CardDescription></div><div class="flex gap-4 text-xs"><div class="flex items-center gap-2"><div class="w-3 h-3 rounded-full bg-emerald-500"></div> Actual</div><div class="flex items-center gap-2"><div class="w-3 h-3 rounded-full bg-gray-600 border border-white/50"></div> Predicted</div></div></div></CardHeader>
                    <CardContent><div class="relative w-full h-64 mt-4"><div v-if="chartHistory.length === 0" class="flex flex-col items-center justify-center h-full text-gray-500"><Loader2 class="w-8 h-8 animate-spin mb-2" /><span>Reading history...</span></div><svg v-else viewBox="0 0 100 100" class="w-full h-full overflow-visible" preserveAspectRatio="none"><line x1="0" y1="25" x2="100" y2="25" stroke="#374151" stroke-width="0.5" stroke-dasharray="2" /><line x1="0" y1="50" x2="100" y2="50" stroke="#374151" stroke-width="0.5" stroke-dasharray="2" /><line x1="0" y1="75" x2="100" y2="75" stroke="#374151" stroke-width="0.5" stroke-dasharray="2" /><polyline fill="none" stroke="#6b7280" stroke-width="2" stroke-dasharray="4" :points="getPoints('predicted')" vector-effect="non-scaling-stroke" opacity="0.5" /><polyline fill="none" stroke="#10b981" stroke-width="3" :points="getPoints('actual')" vector-effect="non-scaling-stroke" /></svg></div></CardContent>
                </Card>
                <Card class="bg-gray-900 border-gray-800 flex flex-col h-full">
                    <CardHeader><CardTitle class="text-white text-lg">Status Breakdown</CardTitle><CardDescription>Current Bin States</CardDescription></CardHeader>
                    <CardContent class="flex-1 flex flex-col items-center justify-center"><div class="relative w-48 h-48"><svg viewBox="0 0 100 100" class="transform -rotate-90"><path :d="getDonutPath(2, activeSensors, statusDist)" fill="#10b981" /><path :d="getDonutPath(1, activeSensors, statusDist)" fill="#f59e0b" /><path :d="getDonutPath(0, activeSensors, statusDist)" fill="#ef4444" /></svg><div class="absolute inset-0 flex flex-col items-center justify-center"><span class="text-3xl font-bold text-white">{{ activeSensors }}</span><span class="text-xs text-gray-500">Total Bins</span></div></div><div class="flex gap-4 mt-6 text-xs"><div class="flex items-center gap-1"><div class="w-3 h-3 bg-red-500 rounded-full"></div> Crit</div><div class="flex items-center gap-1"><div class="w-3 h-3 bg-amber-500 rounded-full"></div> Warn</div><div class="flex items-center gap-1"><div class="w-3 h-3 bg-emerald-500 rounded-full"></div> OK</div></div></CardContent>
                </Card>
            </div>
            <div class="grid lg:grid-cols-3 gap-6">
                <Card class="lg:col-span-2 bg-gray-900 border-gray-800"><CardHeader><CardTitle class="text-white text-lg">Weekly Collection Volume</CardTitle><CardDescription>Total waste collected (Mock Data)</CardDescription></CardHeader><CardContent><div class="h-48 w-full flex items-end justify-between gap-2 pt-4"><div v-for="(d, i) in weeklyStats" :key="i" class="flex-1 flex flex-col items-center gap-2 group"><div class="w-full bg-gray-800 rounded-t-sm relative group-hover:bg-gray-700 transition-all h-full flex items-end"><div class="w-full bg-emerald-600/80 rounded-t-sm transition-all duration-500" :style="{ height: d.vol + '%' }"></div></div><span class="text-xs text-gray-500 font-mono">{{ d.day }}</span></div></div></CardContent></Card>
                <Card class="bg-gray-900 border-gray-800 flex flex-col h-[300px]"><CardHeader><CardTitle class="text-white text-lg">Live Feed</CardTitle><CardDescription>Real-time updates</CardDescription></CardHeader><CardContent class="flex-1 overflow-y-auto pr-2 custom-scrollbar"><div v-if="bins.length === 0" class="text-gray-500 text-center py-4">Waiting...</div><div class="space-y-3"><div v-for="bin in bins" :key="bin.id" class="p-3 rounded-lg border bg-black/40 flex items-center justify-between" :class="bin.fillLevel >= 90 ? 'border-red-500/30' : 'border-gray-800'"><div class="flex items-center gap-3"><div class="w-10 h-10 rounded-lg flex items-center justify-center bg-gray-800"><Wifi class="w-5 h-5" :class="bin.status === 'Critical' ? 'text-red-500' : 'text-emerald-500'" /></div><div><p class="text-sm font-bold text-white">{{ bin.id }}</p><p class="text-xs text-gray-500 truncate w-24">Lat: {{ bin.rawLat }}</p></div></div><div class="text-right"><p class="text-sm font-bold" :class="bin.fillLevel >= 90 ? 'text-red-400' : 'text-white'">{{ bin.fillLevel }}%</p><span class="text-xs text-gray-500">{{ bin.status }}</span></div></div></div></CardContent></Card>
            </div>
        </div>

        <div v-if="currentTab === 'map'" class="h-full flex flex-col animate-in fade-in zoom-in-95 duration-300">
            <Card class="bg-gray-900 border-gray-800 flex-1 flex flex-col overflow-hidden">
                <CardHeader class="bg-gray-900 z-10 p-4 border-b border-gray-800 flex flex-row justify-between items-center">
                   <div><CardTitle class="text-white">Live Sensor Map</CardTitle><CardDescription>{{ activeSensors }} nodes | Route Overlay</CardDescription></div>
                   <div class="flex gap-2">
                      <Button size="sm" variant="outline" class="border-gray-700" @click="showRoute = !showRoute">
                         <Eye v-if="showRoute" class="w-4 h-4 mr-2" />
                         <EyeOff v-else class="w-4 h-4 mr-2" />
                         {{ showRoute ? 'Hide Route' : 'Show Route' }}
                      </Button>
                      <Badge variant="outline" class="text-emerald-400 border-emerald-500/30">Live</Badge>
                   </div>
                </CardHeader>
                <div class="flex-1 bg-gray-800 relative group overflow-hidden">
                    <div id="map" class="w-full h-full z-10"></div>
                </div>
            </Card>
        </div>

        <div v-if="currentTab === 'fleet'" class="animate-in fade-in slide-in-from-right-10 duration-500 space-y-6">
            <Card class="bg-gray-900 border-gray-800">
                <CardHeader><CardTitle class="text-white">Fleet Optimization</CardTitle><CardDescription>Manual AI Triggers</CardDescription></CardHeader>
                <CardContent class="grid gap-4 md:grid-cols-2">
                    <div class="p-4 bg-black/40 border border-gray-800 rounded-xl flex justify-between items-center"><div><p class="text-white font-bold">Route Optimization</p><p class="text-gray-500 text-sm">Run TSP Algorithm</p></div><Button @click="handleOptimize" :disabled="isOptimizing" class="bg-emerald-600 hover:bg-emerald-700 text-white min-w-[140px]"><Loader2 v-if="isOptimizing" class="w-4 h-4 mr-2 animate-spin" /><Zap v-else class="w-4 h-4 mr-2" />{{ isOptimizing ? 'Running...' : 'Optimize' }}</Button></div>
                </CardContent>
            </Card>
        </div>

        <div v-if="currentTab === 'ml'" class="animate-in fade-in slide-in-from-right-10 duration-500 space-y-6">
            <Card class="bg-gray-900 border-gray-800">
                <CardHeader class="flex flex-row items-center justify-between"><div><CardTitle class="text-white">Predictive Analytics</CardTitle><CardDescription>Forecasts based on historical data</CardDescription></div><Button @click="handlePredict" :disabled="isPredicting" class="bg-cyan-600 hover:bg-cyan-700 text-white"><Loader2 v-if="isPredicting" class="w-4 h-4 mr-2 animate-spin" /><Brain v-else class="w-4 h-4 mr-2" />{{ isPredicting ? 'Calculating...' : 'Run Inference' }}</Button></CardHeader>
                <CardContent><div class="rounded-xl border border-gray-800 overflow-hidden"><table class="w-full text-left text-sm"><thead class="bg-gray-800 text-gray-400 uppercase font-medium"><tr><th class="p-4">Bin ID</th><th class="p-4">Current Fill</th><th class="p-4">Fill Rate</th><th class="p-4">Time to Full</th><th class="p-4">Status</th></tr></thead><tbody class="divide-y divide-gray-800 bg-gray-900/50"><tr v-for="pred in predictions" :key="pred.id" class="hover:bg-white/5 transition"><td class="p-4 font-bold text-white">{{ pred.id }}</td><td class="p-4">{{ pred.currentFill }}%</td><td class="p-4 text-gray-400">{{ pred.fillRate }}/hr</td><td class="p-4 text-cyan-400 font-bold flex items-center"><Clock class="w-3 h-3 mr-2"/> {{ pred.timeToFull }} hrs</td><td class="p-4"><Badge :class="pred.status === 'Critical' ? 'bg-red-500/20 text-red-400' : 'bg-emerald-500/20 text-emerald-400'">{{ pred.status }}</Badge></td></tr><tr v-if="predictions.length === 0"><td colspan="5" class="p-8 text-center text-gray-500">No predictions yet. Run inference.</td></tr></tbody></table></div></CardContent>
            </Card>
        </div>

      </div>
    </main>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { bg: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #374151; border-radius: 4px; }
:deep(.leaflet-popup-content-wrapper) { background-color: #111827; color: white; border-radius: 0.5rem; border: 1px solid #374151; }
:deep(.leaflet-popup-tip) { background-color: #111827; }
</style>
