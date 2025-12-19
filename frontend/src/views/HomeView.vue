<script setup>
import {
  ArrowRight, Leaf, Map as MapIcon, Wifi, Users, Github, Linkedin,
  Cpu, TrendingUp, MapPin, Clock, Sparkles, Zap, BarChart3, Menu, X
} from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { onMounted, ref } from 'vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

// Import the Hero Image
import heroBg from '@/assets/images/HeroBg.png'

const router = useRouter()
const navigateToDashboard = () => router.push('/dashboard')

// Mobile Menu State
const isMobileMenuOpen = ref(false)
const toggleMobileMenu = () => isMobileMenuOpen.value = !isMobileMenuOpen.value

// Simple scroll animation observer
onMounted(() => {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-fade-in')
        }
      })
    },
    { threshold: 0.1 }
  )

  document.querySelectorAll('[data-animate]').forEach(el => {
    observer.observe(el)
  })
})

// Team members data
const teamMembers = [
  {
    name: "Mujtaba Abdulmuttalib",
    role: "Lead Developer & Architect",
    image: "/images/team/mujtaba.jpg",
    github: "#",
    linkedin: "#"
  },
  {
    name: "Hussein Ali",
    role: "Hardware & IoT Specialist",
    image: "/images/team/hussein.jpg",
    github: "#",
    linkedin: "#"
  },
  {
    name: "Mustafa Safa",
    role: "Hardware & IoT Specialist",
    image: "/images/team/mustafa.jpg",
    github: "#",
    linkedin: "#"
  },
  {
    name: "Zainab Haidar",
    role: "Project Manager & Research",
    image: "/images/team/zanib.jpg",
    github: "#",
    linkedin: "#"
  }
]

// Features with enhanced icons
const features = [
  {
    icon: Wifi,
    title: 'Real-time Monitoring',
    description: 'Live data from IoT sensors tracking bin fill levels 24/7 with millisecond precision.',
    color: 'text-cyan-400'
  },
  {
    icon: Zap,
    title: 'AI-Powered Routing',
    description: 'Advanced algorithms optimize collection routes, reducing fuel costs by up to 40%.',
    color: 'text-emerald-400'
  },
  {
    icon: TrendingUp,
    title: 'Predictive Analytics',
    description: 'Machine Learning forecasts when bins will be full to prevent overflow before it happens.',
    color: 'text-violet-400'
  },
  {
    icon: Leaf,
    title: 'Eco-Friendly Impact',
    description: 'Reduce carbon emissions and fuel consumption through smart fleet optimization.',
    color: 'text-green-400'
  },
  {
    icon: Clock,
    title: 'Operational Efficiency',
    description: 'Save driver time by automatically filtering out empty bins from the daily route.',
    color: 'text-amber-400'
  },
  {
    icon: BarChart3,
    title: 'Advanced Metrics',
    description: 'Comprehensive dashboard with historical data, cost analysis, and performance reports.',
    color: 'text-blue-400'
  }
]
</script>

<template>
  <div class="min-h-screen bg-gradient-to-b from-gray-950 via-gray-900 to-black text-white font-sans overflow-x-hidden">

    <nav class="fixed top-0 left-0 right-0 z-50 bg-gray-950/80 backdrop-blur-xl border-b border-white/10 transition-all duration-300">
      <div class="container mx-auto px-6 py-2">
        <div class="flex items-center justify-between">

          <div class="flex items-center gap-3 cursor-pointer group" @click="router.push('/')">
            <span class="text-5xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent font-kihim inline-block py-4 px-1 leading-normal">
              Enki
            </span>
          </div>

          <div class="hidden md:flex items-center gap-8">
            <a href="#" class="text-white font-medium hover:text-emerald-400 transition-colors text-sm uppercase tracking-wide">Home</a>
            <a href="#features" class="text-gray-400 hover:text-emerald-400 transition-colors text-sm uppercase tracking-wide">Features</a>
            <a href="#team" class="text-gray-400 hover:text-emerald-400 transition-colors text-sm uppercase tracking-wide">Team</a>
          </div>

          <div class="hidden md:flex items-center gap-3">
            <Button @click="navigateToDashboard" class="bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-600 hover:to-cyan-600 text-white shadow-lg shadow-emerald-500/20 border-0 rounded-full px-6 transition-all hover:scale-105">
              Launch App
            </Button>
          </div>

          <button @click="toggleMobileMenu" class="md:hidden text-gray-300 hover:text-white transition-colors">
            <Menu v-if="!isMobileMenuOpen" class="w-7 h-7" />
            <X v-else class="w-7 h-7" />
          </button>
        </div>
      </div>

      <div v-if="isMobileMenuOpen" class="md:hidden absolute top-full left-0 w-full bg-gray-950 border-b border-gray-800 p-6 flex flex-col gap-4 animate-in slide-in-from-top-5 shadow-2xl">
        <a href="#" @click="isMobileMenuOpen = false" class="text-lg font-medium hover:text-emerald-400 py-2 border-b border-gray-800">Home</a>
        <a href="#features" @click="isMobileMenuOpen = false" class="text-lg font-medium hover:text-emerald-400 py-2 border-b border-gray-800">Features</a>
        <a href="#team" @click="isMobileMenuOpen = false" class="text-lg font-medium hover:text-emerald-400 py-2 border-b border-gray-800">Team</a>
        <Button @click="navigateToDashboard" class="w-full bg-emerald-600 mt-4 h-12 text-lg">Launch Dashboard</Button>
      </div>
    </nav>

    <section class="relative pt-32 pb-20 overflow-hidden min-h-[90vh] flex items-center">

      <div class="absolute inset-0 bg-[linear-gradient(to_right,#10b98110_1px,transparent_1px),linear-gradient(to_bottom,#10b98110_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]"></div>
      <div class="absolute top-20 left-1/4 w-96 h-96 bg-emerald-500/20 rounded-full blur-[128px] animate-pulse"></div>
      <div class="absolute bottom-20 right-1/4 w-96 h-96 bg-cyan-500/20 rounded-full blur-[128px] animate-pulse" style="animation-delay: 2s;"></div>

      <div class="container mx-auto px-6 relative z-10">
        <div class="grid lg:grid-cols-2 gap-16 items-center">

          <div class="space-y-8 text-center lg:text-left" data-animate>
            <Badge variant="outline" class="border-emerald-500/30 bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 px-4 py-1.5 text-sm rounded-full backdrop-blur-md">
              <Sparkles class="w-3.5 h-3.5 mr-2 inline" /> #1 Smart City Solution
            </Badge>

            <h1 class="text-5xl md:text-7xl font-bold leading-tight tracking-tight">
              <span class="text-white">Smart Waste</span> <br />
              <span class="bg-gradient-to-r from-emerald-400 via-cyan-400 to-blue-500 bg-clip-text text-transparent drop-shadow-sm">Management</span>
            </h1>

            <p class="text-lg md:text-xl text-gray-400 leading-relaxed max-w-2xl mx-auto lg:mx-0 font-light">
              Revolutionizing urban cleanliness with AI-powered sensors and dynamic route optimization. Reduce costs by 40% and create cleaner cities today.
            </p>

            <div class="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start pt-6">
              <Button @click="navigateToDashboard" size="lg" class="bg-emerald-500 hover:bg-emerald-600 text-white shadow-xl shadow-emerald-500/20 text-lg px-8 h-14 rounded-full transition-all hover:scale-105">
                Live Demo <ArrowRight class="w-5 h-5 ml-2" />
              </Button>
              <Button size="lg" variant="outline" class="border-gray-700 bg-white/5 text-gray-300 hover:bg-white/10 hover:text-white hover:border-white/20 text-lg px-8 h-14 rounded-full backdrop-blur-sm">
                Contact Sales
              </Button>
            </div>

            <div class="flex flex-wrap justify-center lg:justify-start gap-8 pt-8 border-t border-white/10">
              <div><p class="text-3xl font-bold text-white">40%</p><p class="text-xs uppercase tracking-wider text-gray-500 font-semibold">Cost Reduced</p></div>
              <div class="w-px h-10 bg-white/10 hidden sm:block"></div>
              <div><p class="text-3xl font-bold text-white">95%</p><p class="text-xs uppercase tracking-wider text-gray-500 font-semibold">Accuracy</p></div>
              <div class="w-px h-10 bg-white/10 hidden sm:block"></div>
              <div><p class="text-3xl font-bold text-white">24/7</p><p class="text-xs uppercase tracking-wider text-gray-500 font-semibold">Monitoring</p></div>
            </div>
          </div>

          <div class="relative hidden lg:block group perspective-1000" data-animate>
            <div class="relative rounded-2xl border border-gray-700 bg-gray-800/50 backdrop-blur-sm p-3 shadow-2xl transform rotate-y-6 rotate-x-6 group-hover:rotate-0 transition-all duration-700 ease-out">
               <img :src="heroBg" alt="Smart Waste Dashboard Visualization" class="w-full h-auto object-cover rounded-xl shadow-inner border border-white/5" />

               <div class="absolute bottom-6 left-6 bg-gray-900/90 backdrop-blur-xl p-4 rounded-xl border border-gray-700 shadow-2xl flex items-center gap-4 animate-bounce-slow">
                  <div class="w-12 h-12 bg-emerald-500/20 rounded-full flex items-center justify-center border border-emerald-500/30">
                    <Wifi class="w-6 h-6 text-emerald-400 animate-pulse" />
                  </div>
                  <div>
                    <h3 class="font-bold text-white text-sm">System Active</h3>
                    <p class="text-xs text-emerald-400 font-mono">Connected to 26 Nodes</p>
                  </div>
               </div>
            </div>
            <div class="absolute -inset-4 bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 blur-3xl -z-10 opacity-60 group-hover:opacity-100 transition duration-700"></div>
          </div>

        </div>
      </div>
    </section>

    <section class="py-10 border-y border-white/5 bg-black/40 backdrop-blur-sm">
      <div class="container mx-auto px-6 text-center">
        <p class="text-xs font-bold text-gray-500 uppercase tracking-[0.2em] mb-8">Powered by Modern Technology</p>
        <div class="flex flex-wrap justify-center items-center gap-10 md:gap-20 opacity-60 grayscale hover:grayscale-0 transition-all duration-700">
             <div class="flex items-center gap-2 text-xl font-bold text-white"><Cpu class="text-emerald-500 w-6 h-6"/> ESP32</div>
             <div class="flex items-center gap-2 text-xl font-bold text-white"><span class="text-orange-400">🔥</span> Firebase</div>
             <div class="flex items-center gap-2 text-xl font-bold text-white"><span class="text-emerald-400">V</span> Vue.js</div>
             <div class="flex items-center gap-2 text-xl font-bold text-white"><MapIcon class="text-cyan-500 w-6 h-6"/> Leaflet</div>
             <div class="flex items-center gap-2 text-xl font-bold text-white"><Brain class="text-violet-500 w-6 h-6"/> Python AI</div>
        </div>
      </div>
    </section>

    <section id="features" class="py-24 relative bg-gray-950">
      <div class="container mx-auto px-6">
        <div class="text-center mb-16 space-y-4" data-animate>
          <Badge variant="outline" class="border-emerald-500/50 bg-emerald-500/10 text-emerald-400">
            POWERFUL FEATURES
          </Badge>
          <h2 class="text-4xl md:text-5xl font-bold">
            <span class="text-white">Everything you need, </span>
            <span class="bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">in one platform</span>
          </h2>
          <p class="text-gray-400 text-lg max-w-2xl mx-auto">
            We combined advanced AI algorithms with robust IoT hardware to create the most efficient waste management system in Iraq.
          </p>
        </div>

        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card
            v-for="(feature, index) in features"
            :key="index"
            class="group border-gray-800 bg-gray-900/50 backdrop-blur-xl hover:border-emerald-500/50 transition-all duration-300 hover:shadow-2xl hover:shadow-emerald-500/10 hover:-translate-y-1"
            data-animate
            :style="{ transitionDelay: `${index * 100}ms` }"
          >
            <CardHeader>
              <div class="w-14 h-14 bg-gray-800/80 rounded-2xl flex items-center justify-center mb-4 group-hover:bg-gray-800 transition-colors border border-gray-700 group-hover:border-emerald-500/30">
                <component :is="feature.icon" :class="feature.color" class="w-7 h-7 group-hover:scale-110 transition-transform duration-300" />
              </div>
              <CardTitle class="text-xl text-white font-bold">{{ feature.title }}</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription class="text-gray-400 text-base leading-relaxed">{{ feature.description }}</CardDescription>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>

    <section class="py-24 relative overflow-hidden">
      <div class="absolute inset-0 bg-emerald-900/10"></div>
      <div class="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-emerald-500/10 rounded-full blur-[100px]"></div>

      <div class="container mx-auto px-6 relative z-10">
        <div class="bg-gradient-to-br from-gray-900 to-black border border-gray-800 rounded-3xl p-8 md:p-16 text-center shadow-2xl relative overflow-hidden group">

          <div class="absolute top-0 right-0 w-64 h-64 bg-cyan-500/10 rounded-full blur-[80px] group-hover:bg-cyan-500/20 transition duration-1000"></div>

          <div class="relative z-10 max-w-3xl mx-auto space-y-8" data-animate>
             <h2 class="text-4xl md:text-5xl font-bold text-white tracking-tight">
               Ready to optimize your fleet?
             </h2>
             <p class="text-xl text-gray-400">
               Join the smart city revolution today. Access our powerful dashboard to monitor bins, view analytics, and optimize routes instantly.
             </p>
             <div class="flex justify-center pt-4">
                <Button
                  @click="navigateToDashboard"
                  size="lg"
                  class="bg-white text-gray-900 hover:bg-gray-100 hover:scale-105 transition-all shadow-xl h-14 px-10 rounded-full text-lg font-bold"
                >
                  View Live Dashboard <ArrowRight class="w-5 h-5 ml-2" />
                </Button>
             </div>
          </div>
        </div>
      </div>
    </section>

    <section id="team" class="py-24 relative bg-gray-950">
      <div class="container mx-auto px-6">
        <div class="text-center mb-16 space-y-4" data-animate>
          <Badge variant="outline" class="border-emerald-500/50 bg-emerald-500/10 text-emerald-400">
            <Users class="w-3 h-3 mr-1" /> OUR TEAM
          </Badge>
          <h2 class="text-4xl font-bold text-white">Meet Team Enki</h2>
          <p class="text-gray-400 text-lg max-w-2xl mx-auto">
            A passionate group of engineers and researchers from the University of Babylon, dedicated to making our cities cleaner and smarter.
          </p>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
          <Card
            v-for="(member, index) in teamMembers"
            :key="member.name"
            class="group border-gray-800 bg-gray-900/50 backdrop-blur-xl hover:border-emerald-500/50 transition-all hover:-translate-y-2 duration-300"
            data-animate
            :style="{ transitionDelay: `${index * 100}ms` }"
          >
            <CardContent class="p-6 text-center">
              <div class="relative w-32 h-32 mx-auto mb-6">
                <div class="w-full h-full rounded-full bg-gradient-to-br from-gray-800 to-gray-900 flex items-center justify-center border-2 border-gray-700 group-hover:border-emerald-500/50 transition-colors shadow-xl overflow-hidden">
                    <span class="text-3xl font-bold text-gray-500 group-hover:text-white transition-colors">{{ member.name.charAt(0) }}</span>
                </div>
                <div class="absolute bottom-1 right-1 w-6 h-6 bg-gray-900 rounded-full flex items-center justify-center">
                    <div class="w-4 h-4 bg-emerald-500 rounded-full border-2 border-gray-900"></div>
                </div>
              </div>

              <h3 class="text-lg font-bold text-white mb-1 group-hover:text-emerald-400 transition-colors">{{ member.name }}</h3>
              <p class="text-gray-500 text-sm font-medium mb-6 min-h-[40px]">{{ member.role }}</p>

              <div class="flex justify-center gap-4 opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-2 group-hover:translate-y-0">
                <a href="#" class="text-gray-400 hover:text-white transition-colors"><Github class="w-5 h-5"/></a>
                <a href="#" class="text-gray-400 hover:text-blue-400 transition-colors"><Linkedin class="w-5 h-5"/></a>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>

    <footer class="border-t border-gray-800 py-12 bg-black text-sm">
      <div class="container mx-auto px-6">
        <div class="flex flex-col md:flex-row justify-between items-center mb-8 gap-6">
          <div class="text-center md:text-left">
            <div class="flex items-center justify-center md:justify-start gap-2 mb-2">
               <span class="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent font-kihim inline-block py-4 px-1 leading-normal">
                 Enki
               </span>
            </div>
            <p class="text-gray-500">© 2026 Team Enki. All rights reserved.</p>
          </div>

          <div class="flex gap-8 font-medium">
            <a href="#" class="text-gray-500 hover:text-emerald-400 transition">Home</a>
            <a href="#features" class="text-gray-500 hover:text-emerald-400 transition">Features</a>
            <a href="#team" class="text-gray-500 hover:text-emerald-400 transition">Team</a>
            <a href="/dashboard" class="text-gray-500 hover:text-emerald-400 transition">Dashboard</a>
          </div>
        </div>

        <div class="pt-8 border-t border-gray-900 flex flex-col md:flex-row justify-between items-center text-gray-600">
          <p class="flex items-center gap-2"><span class="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span> System Status: Online</p>
          <div class="flex gap-6 mt-4 md:mt-0">
            <a href="#" class="hover:text-white transition">Terms</a>
            <a href="#" class="hover:text-white transition">Privacy</a>
          </div>
        </div>
      </div>
    </footer>

  </div>
</template>

<style scoped>
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

[data-animate] {
  opacity: 0;
}

[data-animate].animate-fade-in {
  animation: fadeIn 0.8s ease-out forwards;
}

html {
  scroll-behavior: smooth;
}

/* Perspective for 3D Tilt Effect */
.perspective-1000 {
  perspective: 1000px;
}
.rotate-y-6 { transform: rotateY(-5deg) rotateX(2deg); }
.rotate-x-6 { transform: rotateY(-5deg) rotateX(2deg); }

.animate-bounce-slow {
  animation: bounce 3s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}
</style>
