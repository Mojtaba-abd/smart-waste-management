<script setup>
import { ArrowRight, Leaf, Map, Wifi, Users, Github, Linkedin, Cpu, TrendingUp, MapPin, Clock, Sparkles, Zap, BarChart3 } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { onMounted } from 'vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

const router = useRouter()
const navigateToDashboard = () => router.push('/dashboard')

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
const teamMembers = [
  { name: "Mujtaba", role: "Lead Developer & Architect", github: "#", linkedin: "#" },
  { name: "Hussein", role: "Hardware & IoT Specialist", github: "#", linkedin: "#" },
  { name: "Mustafa", role: "Hardware & IoT Specialist", github: "#", linkedin: "#" },
  { name: "Zanib", role: "Project Manager & Research", github: "#", linkedin: "#" }
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
    <nav class="fixed top-0 left-0 right-0 z-50 bg-gray-950/80 backdrop-blur-xl border-b border-emerald-500/20">
      <div class="container mx-auto px-6 py-4">
        <div class="flex items-center justify-between">
          <!-- Logo -->
          <div class="flex items-center gap-3">
            <div class="relative">
              <div class="w-10 h-10 bg-gradient-to-br from-emerald-400 to-cyan-500 rounded-xl flex items-center justify-center text-gray-900 font-bold text-lg shadow-lg shadow-emerald-500/50">
                E
              </div>
              <div class="absolute inset-0 bg-emerald-400/20 blur-xl rounded-xl"></div>
            </div>
            <span class="text-2xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">Enki</span>
          </div>

          <!-- Navigation Links -->
          <div class="hidden md:flex items-center gap-8">
            <a href="#" class="text-white font-medium hover:text-emerald-400 transition">Home</a>
            <a href="#features" class="text-gray-400 hover:text-emerald-400 transition">Features</a>
            <a href="#team" class="text-gray-400 hover:text-emerald-400 transition">Team</a>
            <a href="#" class="text-gray-400 hover:text-emerald-400 transition">Contact</a>
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-3">
            <Button variant="ghost" class="hidden md:block text-gray-400 hover:text-white">
              Log in
            </Button>
            <Button
              @click="navigateToDashboard"
              class="bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-600 hover:to-cyan-600 text-white shadow-lg shadow-emerald-500/50"
            >
              Get started
            </Button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Hero Section with Grid Background -->
    <section class="relative pt-32 pb-20 overflow-hidden">
      <!-- Animated Grid Background -->
      <div class="absolute inset-0 bg-[linear-gradient(to_right,#10b98120_1px,transparent_1px),linear-gradient(to_bottom,#10b98120_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_0%,#000_70%,transparent_110%)]"></div>

      <!-- Glowing Orbs -->
      <div class="absolute top-40 left-20 w-96 h-96 bg-emerald-500/30 rounded-full blur-[128px]"></div>
      <div class="absolute top-60 right-20 w-96 h-96 bg-cyan-500/20 rounded-full blur-[128px]"></div>

      <div class="container mx-auto px-6 relative z-10">
        <div class="grid lg:grid-cols-2 gap-12 items-center min-h-[600px]">

          <!-- Left Content -->
          <div class="space-y-8" data-animate="fade-up">
            <Badge variant="outline" class="border-emerald-500/50 bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20">
              <Sparkles class="w-3 h-3 mr-1" />
              AI-Powered Waste Management
            </Badge>

            <h1 class="text-6xl md:text-7xl font-bold leading-tight">
              <span class="bg-gradient-to-r from-white via-gray-200 to-gray-400 bg-clip-text text-transparent">
                Smart Waste
              </span>
              <br />
              <span class="bg-gradient-to-r from-emerald-400 via-cyan-400 to-blue-400 bg-clip-text text-transparent">
                Management System
              </span>
            </h1>

            <p class="text-xl text-gray-400 max-w-xl leading-relaxed">
              Revolutionary AI-powered solution using IoT sensors and predictive analytics to optimize collection routes, reduce costs by 40%, and minimize environmental impact.
            </p>

            <!-- CTA Buttons -->
            <div class="flex flex-col sm:flex-row gap-4 pt-4">
              <Button
                @click="navigateToDashboard"
                size="lg"
                class="group bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-600 hover:to-cyan-600 text-white shadow-2xl shadow-emerald-500/50 text-lg"
              >
                Live Demo
                <ArrowRight class="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
              </Button>

              <Button
                size="lg"
                variant="outline"
                class="border-emerald-500/50 text-emerald-400 hover:bg-emerald-500/10 text-lg"
              >
                Get in Touch
              </Button>
            </div>

            <!-- Stats Pills -->
            <div class="flex flex-wrap gap-4 pt-4">
              <div class="px-4 py-2 bg-gray-800/50 border border-gray-700/50 rounded-full backdrop-blur-sm">
                <span class="text-emerald-400 font-bold">25+</span>
                <span class="text-gray-400 ml-2 text-sm">Active Bins</span>
              </div>
              <div class="px-4 py-2 bg-gray-800/50 border border-gray-700/50 rounded-full backdrop-blur-sm">
                <span class="text-cyan-400 font-bold">40%</span>
                <span class="text-gray-400 ml-2 text-sm">Cost Reduction</span>
              </div>
              <div class="px-4 py-2 bg-gray-800/50 border border-gray-700/50 rounded-full backdrop-blur-sm">
                <span class="text-violet-400 font-bold">95%</span>
                <span class="text-gray-400 ml-2 text-sm">Accuracy</span>
              </div>
            </div>
          </div>

          <!-- Right Side - Hero Image Card -->
          <div class="relative" data-animate="fade-up">
            <Card class="overflow-hidden border-gray-800 bg-gray-900/50 backdrop-blur-xl shadow-2xl">
              <div class="relative">
                <img
                  src="/src/assets/images/Litterbin-04-2560x1440.jpg"
                  alt="Smart Waste Bins"
                  class="w-full h-[500px] object-cover"
                />
                <div class="absolute inset-0 bg-gradient-to-t from-gray-900 via-gray-900/50 to-transparent"></div>

                <!-- Floating Info Card -->
                <Card class="absolute bottom-6 left-6 right-6 border-gray-800 bg-gray-950/90 backdrop-blur-xl">
                  <CardContent class="p-4">
                    <p class="text-xs font-semibold text-emerald-400 mb-2">LIVE STATUS</p>
                    <div class="flex items-center gap-3">
                      <div class="w-12 h-12 bg-gradient-to-br from-emerald-500 to-cyan-500 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-500/50">
                        <Map class="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h3 class="font-bold text-white">Smart Collection Route</h3>
                        <p class="text-sm text-gray-400">Optimized in real-time</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </Card>

            <!-- Decorative Glow -->
            <div class="absolute -inset-4 bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 blur-3xl -z-10"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- Tech Stack Section -->
    <section class="py-16 relative">
      <div class="container mx-auto px-6">
        <Card class="border-gray-800 bg-gray-900/50 backdrop-blur-xl" data-animate="fade-up">
          <CardContent class="p-12">
            <div class="text-center mb-8">
              <Badge variant="outline" class="border-gray-700 text-gray-400 mb-4">
                POWERED BY CUTTING-EDGE TECHNOLOGY
              </Badge>
              <h2 class="text-3xl font-bold">
                <span class="text-white">Built with </span>
                <span class="bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">modern tech stack</span>
              </h2>
            </div>

            <div class="flex flex-wrap justify-center items-center gap-12 opacity-60 hover:opacity-100 transition-opacity duration-500">
              <div class="flex items-center gap-2 text-xl font-bold text-gray-300">
                <Cpu class="w-7 h-7 text-emerald-400" /> ESP32
              </div>
              <div class="text-xl font-bold text-gray-300">🔥 Firebase</div>
              <div class="text-xl font-bold text-gray-300">🟢 Vue.js</div>
              <div class="text-xl font-bold text-gray-300">🗺️ Leaflet</div>
              <div class="text-xl font-bold text-gray-300">🤖 Python ML</div>
            </div>
          </CardContent>
        </Card>
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

    <!-- CTA Section -->
    <section class="py-20 relative overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-r from-emerald-500/10 to-cyan-500/10"></div>
      <div class="container mx-auto px-6 relative z-10">
        <Card class="border-emerald-500/50 bg-gradient-to-br from-gray-900 to-gray-950 backdrop-blur-xl" data-animate="fade-up">
          <CardContent class="p-12 text-center">
            <h2 class="text-4xl md:text-5xl font-bold text-white mb-6">
              Ready to revolutionize
              <br />
              <span class="bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">waste management?</span>
            </h2>

            <p class="text-gray-400 text-lg mb-8 max-w-2xl mx-auto">
              Join the smart cities revolution. Reduce costs, minimize environmental impact, and optimize operations with AI-powered insights.
            </p>

            <Button
              @click="navigateToDashboard"
              size="lg"
              class="bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-600 hover:to-cyan-600 text-white shadow-2xl shadow-emerald-500/50"
            >
              Start now
              <ArrowRight class="w-5 h-5 ml-2" />
            </Button>
          </CardContent>
        </Card>
      </div>
    </section>

    <!-- Footer -->
    <footer class="border-t border-gray-800 py-12 bg-gray-950">
      <div class="container mx-auto px-6">
        <div class="flex flex-col md:flex-row justify-between items-center mb-8">
          <div class="mb-6 md:mb-0">
            <div class="flex items-center gap-3 mb-3">
              <div class="w-10 h-10 bg-gradient-to-br from-emerald-400 to-cyan-500 rounded-xl flex items-center justify-center text-gray-900 font-bold shadow-lg shadow-emerald-500/50">
                E
              </div>
              <span class="text-2xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">Enki</span>
            </div>
            <p class="text-gray-500 text-sm">© 2024 Team Enki. All rights reserved.</p>
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
