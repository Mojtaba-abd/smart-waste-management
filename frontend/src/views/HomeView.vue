<script setup>
import { ArrowRight, Leaf, Map, Wifi, Users, Github, Linkedin, Cpu, TrendingUp, MapPin, Clock, Sparkles, Zap, BarChart3 } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { onMounted ,ref} from 'vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import heroBg from '@/assets/images/Litterbin-04-2560x1440.jpg'
const router = useRouter()
const navigateToDashboard = () => router.push('/dashboard')
// Mobile Menu State
const isMobileMenuOpen = ref(false)
const toggleMobileMenu = () => isMobileMenuOpen.value = !isMobileMenuOpen.value

// Simple scroll animation
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

// Team members
// Team members data
const teamMembers = [
  {
    name: "Mujtaba Abdulmuttalib",
    role: "Lead Developer & Architect",
    image: "/images/team/mujtaba.jpg", // <--- Add your image path here
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
    description: 'Live data from IoT sensors tracking bin fill levels 24/7 with millisecond precision',
    color: 'text-cyan-400'
  },
  {
    icon: Zap,
    title: 'AI-Powered Routing',
    description: 'Advanced ML algorithms optimize collection routes, reducing costs by 40%',
    color: 'text-emerald-400'
  },
  {
    icon: TrendingUp,
    title: 'Predictive Analytics',
    description: 'Forecast when bins will be full with 95% accuracy to prevent overflow',
    color: 'text-violet-400'
  },
  {
    icon: Leaf,
    title: 'Eco-Friendly Impact',
    description: 'Reduce carbon emissions and fuel consumption through smart optimization',
    color: 'text-green-400'
  },
  {
    icon: Clock,
    title: 'Time Efficiency',
    description: 'Save operational time by collecting only bins that actually need service',
    color: 'text-amber-400'
  },
  {
    icon: BarChart3,
    title: 'Advanced Analytics',
    description: 'Comprehensive dashboards with real-time metrics and historical insights',
    color: 'text-blue-400'
  }
]
</script>

<template>
  <div class="min-h-screen bg-gradient-to-b from-gray-950 via-gray-900 to-black text-white">

    <!-- Navigation -->
    <nav class="fixed top-0 left-0 right-0 z-50 bg-gray-950/80 backdrop-blur-xl border-b border-white/10">
      <div class="container mx-auto px-6 py-4">
        <div class="flex items-center justify-between">

          <div class="flex items-center gap-3 cursor-pointer" @click="router.push('/')">
            <span class="text-6xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400
              bg-clip-text text-transparent font-kihim inline-block py-4 pr-6 pl-2 leading-relaxed -my-4">
              Enki
            </span>
          </div>          <div class="hidden md:flex items-center gap-8">
            <a href="#" class="text-white font-medium hover:text-emerald-400 transition">Home</a>
            <a href="#features" class="text-gray-400 hover:text-emerald-400 transition">Features</a>
            <a href="#team" class="text-gray-400 hover:text-emerald-400 transition">Team</a>
          </div>

          <div class="hidden md:flex items-center gap-3">
            <Button @click="navigateToDashboard" class="bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-600 hover:to-cyan-600 text-white shadow-lg shadow-emerald-500/20 border-0">
              Get started
            </Button>
          </div>

          <button @click="toggleMobileMenu" class="md:hidden text-gray-300 hover:text-white">
            <Menu v-if="!isMobileMenuOpen" class="w-7 h-7" />
            <X v-else class="w-7 h-7" />
          </button>
        </div>
      </div>

      <div v-if="isMobileMenuOpen" class="md:hidden absolute top-full left-0 w-full bg-gray-950 border-b border-gray-800 p-6 flex flex-col gap-4 animate-in slide-in-from-top-5">
        <a href="#" @click="isMobileMenuOpen = false" class="text-lg font-medium hover:text-emerald-400">Home</a>
        <a href="#features" @click="isMobileMenuOpen = false" class="text-lg font-medium hover:text-emerald-400">Features</a>
        <a href="#team" @click="isMobileMenuOpen = false" class="text-lg font-medium hover:text-emerald-400">Team</a>
        <Button @click="navigateToDashboard" class="w-full bg-emerald-600 mt-2">Get Started</Button>
      </div>
    </nav>

    <!-- Hero Section with Grid Background -->
    <section class="relative pt-32 pb-20 overflow-hidden">

      <div class="absolute inset-0 bg-[linear-gradient(to_right,#10b98110_1px,transparent_1px),linear-gradient(to_bottom,#10b98110_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]"></div>

      <div class="absolute top-20 left-1/4 w-96 h-96 bg-emerald-500/20 rounded-full blur-[128px]"></div>
      <div class="absolute bottom-20 right-1/4 w-96 h-96 bg-cyan-500/20 rounded-full blur-[128px]"></div>

      <div class="container mx-auto px-6 relative z-10">
        <div class="grid lg:grid-cols-2 gap-16 items-center">

          <div class="space-y-8 text-center lg:text-left" data-animate>
            <badge variant="outline" class="border-emerald-500/30 bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 px-4 py-1">
              <sparkles class="w-3 h-3 mr-2" /> #1 smart city solution
            </badge>

            <h1 class="text-5xl md:text-7xl font-bold leading-tight tracking-tight">
              <span class="text-white">smart waste</span> <br />
              <span class="bg-gradient-to-r from-emerald-400 via-cyan-400 to-blue-500 bg-clip-text text-transparent">management system</span>
            </h1>

            <p class="text-lg md:text-xl text-gray-400 leading-relaxed max-w-2xl mx-auto lg:mx-0">
              revolutionary ai-powered solution using iot sensors to optimize routes, reduce costs by 40%, and create cleaner cities.
            </p>

            <div class="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start pt-4">
              <button @click="navigatetodashboard" size="lg" class="bg-emerald-500 hover:bg-emerald-600 text-white shadow-xl shadow-emerald-500/20 text-lg px-8 h-12 rounded-full">
                live demo <arrowright class="w-5 h-5 ml-2" />
              </button>
              <button size="lg" variant="outline" class="border-gray-700 text-gray-300 hover:bg-white/5 hover:text-white text-lg px-8 h-12 rounded-full">
                contact us
              </button>
            </div>

            <div class="flex flex-wrap justify-center lg:justify-start gap-6 pt-6 border-t border-white/5">
              <div><p class="text-2xl font-bold text-white">40%</p><p class="text-sm text-gray-500">cost reduced</p></div>
              <div><p class="text-2xl font-bold text-white">95%</p><p class="text-sm text-gray-500">accuracy</p></div>
              <div><p class="text-2xl font-bold text-white">24/7</p><p class="text-sm text-gray-500">monitoring</p></div>
            </div>
          </div>

          <div class="relative hidden lg:block" data-animate>
            <div class="relative rounded-2xl border border-gray-700 bg-gray-800/50 backdrop-blur-sm p-2 shadow-2xl transform rotate-1 hover:rotate-0 transition duration-500">
               <img :src="heroBg" alt="smart waste dashboard" class="w-full h-[500px] object-cover rounded-xl shadow-inner" />

               <div class="absolute bottom-8 left-8 right-8 bg-gray-900/90 backdrop-blur-md p-4 rounded-xl border border-gray-700 shadow-xl flex items-center gap-4">
                  <div class="w-12 h-12 bg-emerald-500/20 rounded-full flex items-center justify-center">
                    <wifi class="w-6 h-6 text-emerald-400 animate-pulse" />
                  </div>
                  <div>
                    <h3 class="font-bold text-white">system active</h3>
                    <p class="text-sm text-emerald-400">collecting real-time data...</p>
                  </div>
               </div>
            </div>
          </div>

        </div>
      </div>
    </section>
    <!-- Tech Stack Section -->
    <section class="py-10 border-y border-white/5 bg-black/20">
      <div class="container mx-auto px-6 text-center">
        <p class="text-sm font-semibold text-gray-500 uppercase tracking-widest mb-8">Powered by Modern Technology</p>
        <div class="flex flex-wrap justify-center gap-8 md:gap-16 opacity-50 grayscale hover:grayscale-0 transition-all duration-500">
             <div class="flex items-center gap-2 text-xl font-bold text-white"><Cpu class="text-emerald-500"/> ESP32</div>
             <div class="flex items-center gap-2 text-xl font-bold text-white">Firebase</div>
             <div class="flex items-center gap-2 text-xl font-bold text-white">Vue.js</div>
             <div class="flex items-center gap-2 text-xl font-bold text-white">Leaflet</div>
             <div class="flex items-center gap-2 text-xl font-bold text-white">AI/ML</div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="py-20 relative">
      <div class="container mx-auto px-6">
        <div class="text-center mb-16" data-animate="fade-up">
          <Badge variant="outline" class="border-emerald-500/50 bg-emerald-500/10 text-emerald-400 mb-4">
            POWERFUL FEATURES
          </Badge>
          <h2 class="text-4xl md:text-5xl font-bold mb-4">
            <span class="text-white">Everything you need, </span>
            <span class="bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">in one platform</span>
          </h2>
          <p class="text-gray-400 text-lg max-w-2xl mx-auto">
            Advanced AI algorithms combined with IoT sensors to create the most efficient waste management system
          </p>
        </div>

        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card
            v-for="(feature, index) in features"
            :key="index"
            class="group border-gray-800 bg-gray-900/50 backdrop-blur-xl hover:border-emerald-500/50 transition-all duration-300 hover:shadow-2xl hover:shadow-emerald-500/20"
            data-animate="fade-up"
          >
            <CardHeader>
              <div class="w-12 h-12 bg-gray-800/50 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <component :is="feature.icon" :class="feature.color" class="w-6 h-6" />
              </div>
              <CardTitle class="text-white">{{ feature.title }}</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription class="text-gray-400">{{ feature.description }}</CardDescription>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>

    <!-- Demo Section -->
    <section class="py-20 relative">
      <div class="container mx-auto px-6">
        <div class="grid lg:grid-cols-2 gap-12 items-center">
          <div data-animate="fade-up">
            <Badge variant="outline" class="border-emerald-500/50 bg-emerald-500/10 text-emerald-400 mb-6">
              REAL-TIME DASHBOARD
            </Badge>
            <h2 class="text-4xl font-bold text-white mb-6">
              Monitor everything
              <br />
              <span class="bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">in real-time</span>
            </h2>
            <p class="text-gray-400 text-lg mb-8">
              Access our powerful dashboard to monitor all bins, view analytics, optimize routes, and make data-driven decisions instantly.
            </p>
            <Button
              @click="navigateToDashboard"
              size="lg"
              class="bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-600 hover:to-cyan-600 shadow-lg shadow-emerald-500/50"
            >
              View Dashboard
              <ArrowRight class="w-5 h-5 ml-2" />
            </Button>
          </div>

          <div class="relative" data-animate="fade-up">
            <Card class="border-gray-800 bg-gray-900/50 backdrop-blur-xl overflow-hidden">
              <img
                src="/src/assets/images/Litterbin-04-2560x1440.jpg"
                alt="Dashboard Preview"
                class="w-full h-[400px] object-cover"
              />
            </Card>
            <div class="absolute -inset-4 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 blur-3xl -z-10"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- Team Section -->
    <section id="team" class="py-20 relative">
      <div class="container mx-auto px-6">
        <div class="text-center mb-16" data-animate="fade-up">
          <Badge variant="outline" class="border-emerald-500/50 bg-emerald-500/10 text-emerald-400 mb-4">
            <Users class="w-3 h-3 mr-1" /> OUR TEAM
          </Badge>
          <h2 class="text-4xl font-bold text-white mb-4">Meet Team Enki</h2>
          <p class="text-gray-400 text-lg max-w-2xl mx-auto">
            A passionate group of engineers and researchers making cities cleaner and smarter
          </p>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-4 gap-8">
          <Card
            v-for="member in teamMembers"
            :key="member.name"
            class="group border-gray-800 bg-gray-900/50 backdrop-blur-xl hover:border-emerald-500/50 transition-all text-center"
            data-animate="fade-up"
          >
            <CardContent class="p-6">
              <div class="relative w-24 h-24 mx-auto mb-4">
                <div class="w-full h-full rounded-2xl bg-gradient-to-br from-emerald-400 to-cyan-500 flex items-center justify-center text-gray-900 text-3xl font-bold shadow-lg shadow-emerald-500/50 group-hover:scale-105 transition">
                  {{ member.name.charAt(0) }}
                </div>
              </div>
              <h3 class="text-lg font-bold text-white mb-1">{{ member.name }}</h3>
              <p class="text-emerald-400 text-sm font-medium mb-4">{{ member.role }}</p>
              <div class="flex justify-center gap-2 opacity-0 group-hover:opacity-100 transition">
                <Button size="sm" variant="ghost" class="w-8 h-8 p-0">
                  <Github :size="16" />
                </Button>
                <Button size="sm" variant="ghost" class="w-8 h-8 p-0">
                  <Linkedin :size="16" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="border-t border-gray-800 py-12 bg-gray-950">
      <div class="container mx-auto px-6">
        <div class="flex flex-col md:flex-row justify-between items-center mb-8">
          <div class="mb-6 md:mb-0">
            <div class="flex items-center gap-3 mb-3">
            <span class="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400
              bg-clip-text text-transparent font-kihim inline-block py-4 pr-6 pl-2 leading-relaxed -my-4">
              Enki
            </span>
            </div>
            <p class="text-gray-500 text-sm">© 2026 Team Enki. All rights reserved.</p>
          </div>

          <div class="flex gap-8">
            <a href="#" class="text-gray-400 hover:text-emerald-400 transition text-sm">Home</a>
            <a href="#features" class="text-gray-400 hover:text-emerald-400 transition text-sm">Features</a>
            <a href="#team" class="text-gray-400 hover:text-emerald-400 transition text-sm">Team</a>
            <a href="/dashboard" class="text-gray-400 hover:text-emerald-400 transition text-sm">Dashboard</a>
          </div>
        </div>

        <div class="pt-8 border-t border-gray-800 flex flex-col md:flex-row justify-between items-center text-sm text-gray-500">
          <p>🔒 100% Secure & Encrypted</p>
          <div class="flex gap-6 mt-4 md:mt-0">
            <a href="#" class="hover:text-emerald-400 transition">Terms</a>
            <a href="#" class="hover:text-emerald-400 transition">Privacy</a>
          </div>
        </div>
      </div>
    </footer>

  </div>
</template>

<style scoped>
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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
</style>
