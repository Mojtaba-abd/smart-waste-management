<script setup>
import { ArrowRight, Leaf, Map, Cpu, Wifi, Users, Github, Linkedin } from 'lucide-vue-next';
import { useRouter } from 'vue-router';

const router = useRouter();

const navigateToDashboard = () => {
  router.push('/dashboard');
};

// Mock data for your team. Replace placeholder images with your real selfies!
const teamMembers = [
  {
    name: "Mujtaba", // You
    role: "Lead Developer & Architect",
    image: "https://api.dicebear.com/7.x/avataaars/svg?seed=Hussein&style=circle&top=shortHair",
    github: "#", linkedin: "#"
  },
  {
    name: "Hussein", // Member 2
    role: "Hardware & IoT Specialist",
    image: "https://api.dicebear.com/7.x/avataaars/svg?seed=Ali&style=circle&facialHair=beardLight",
    github: "#", linkedin: "#"
  },
  {
    name: "Mustafa", // Member 2
    role: "Hardware & IoT Specialist",
    image: "https://api.dicebear.com/7.x/avataaars/svg?seed=Ali&style=circle&facialHair=beardLight",
    github: "#", linkedin: "#"
  },
  {
    name: "Zenaib", // Member 5
    role: "Project Manager & Research",
    image: "https://api.dicebear.com/7.x/avataaars/svg?seed=Layla&style=circle&top=bob",
    github: "#", linkedin: "#"
  }
];
</script>

<template>
  <div class="font-sans text-gray-800 bg-white selection:bg-emerald-100">

    <nav class="container mx-auto px-6 py-6 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <div class="w-8 h-8 bg-emerald-500 rounded-full flex items-center justify-center text-white font-bold">E</div>
        <span class="text-xl font-bold tracking-tight">Team Enki</span>
      </div>
      <div class="hidden md:flex gap-8 text-sm font-medium text-gray-600">
        <a href="#features" class="hover:text-emerald-600 transition">Features</a>
        <a href="#technology" class="hover:text-emerald-600 transition">Technology</a>
        <a href="#team" class="hover:text-emerald-600 transition">Our Team</a>
      </div>
      <button @click="navigateToDashboard" class="bg-black text-white px-6 py-2.5 rounded-full text-sm font-medium hover:bg-emerald-600 transition shadow-lg hover:shadow-emerald-500/30">
        Open Dashboard
      </button>
    </nav>

    <header class="container mx-auto px-6 mt-8 mb-20">
      <div class="relative bg-gray-900 rounded-[3rem] overflow-hidden min-h-[500px] flex items-center">
        <div class="absolute inset-0 opacity-60">
            <img src="https://images.unsplash.com/photo-1532996122724-e3c354a0b15b?q=80&w=2070&auto=format&fit=crop" class="w-full h-full object-cover" alt="Clean City" />
        </div>
        <div class="relative z-10 px-10 md:px-20 py-20 max-w-4xl">
          <span class="text-emerald-400 font-bold tracking-wider uppercase text-xs mb-4 block">IoT & AI Solution by Team Enki</span>
          <h1 class="text-5xl md:text-7xl font-bold text-white leading-tight mb-8">
            Smarter Cities Start with <br />
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-300">Intelligent Solutions.</span>
          </h1>
          <p class="text-gray-300 text-lg md:text-xl max-w-2xl mb-10 leading-relaxed">
            Revolutionizing urban cleanliness with IoT sensors and AI-driven route optimization. Save fuel, reduce overflow, and keep cities green.
          </p>
          <div class="flex flex-wrap gap-4">
            <button @click="navigateToDashboard" class="bg-emerald-500 text-white px-8 py-4 rounded-full font-bold text-lg hover:bg-emerald-400 transition flex items-center gap-2">
              Get in Touch <ArrowRight size="20" />
            </button>
            <button @click="navigateToDashboard" class="bg-emerald-500 text-white px-8 py-4 rounded-full font-bold text-lg hover:bg-emerald-400 transition flex items-center gap-2">
              Live Demo <ArrowRight size="20" />
            </button>
          </div>
        </div>
      </div>
    </header>

    <section id="technology" class="container mx-auto px-6 py-12 text-center">
        <p class="text-sm font-bold text-gray-400 uppercase tracking-widest mb-8">Powered by Modern Tech</p>
        <div class="flex flex-wrap justify-center gap-12 opacity-50 grayscale hover:grayscale-0 transition-all duration-500">
            <span class="text-xl font-bold flex items-center gap-2"><Cpu /> ESP32</span>
            <span class="text-xl font-bold flex items-center gap-2">🔥 Firebase</span>
            <span class="text-xl font-bold flex items-center gap-2">🟢 Vue.js</span>
            <span class="text-xl font-bold flex items-center gap-2">🗺️ Leaflet</span>
            <span class="text-xl font-bold flex items-center gap-2">🤖 Scikit-Learn</span>
        </div>
    </section>

    <section id="features" class="bg-gray-50 py-24 rounded-[3rem] my-12 mx-4">
        <div class="container mx-auto px-6">
            <div class="text-center max-w-2xl mx-auto mb-16">
                <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">Smart Solutions, Real Impact</h2>
                <p class="text-gray-500 text-lg">We replace traditional, static waste collection with a dynamic, data-driven approach.</p>
            </div>
            <div class="grid md:grid-cols-3 gap-8">
                <div class="bg-white p-8 rounded-3xl shadow-sm hover:shadow-xl transition duration-300">
                    <div class="w-12 h-12 bg-emerald-100 text-emerald-600 rounded-2xl flex items-center justify-center mb-6"><Wifi size="24" /></div>
                    <h3 class="text-xl font-bold mb-3">IoT Monitoring</h3>
                    <p class="text-gray-500 leading-relaxed">Ultrasonic sensors measure fill levels in real-time, sending data instantly to the cloud.</p>
                </div>
                <div class="bg-white p-8 rounded-3xl shadow-sm hover:shadow-xl transition duration-300">
                    <div class="w-12 h-12 bg-blue-100 text-blue-600 rounded-2xl flex items-center justify-center mb-6"><Map size="24" /></div>
                    <h3 class="text-xl font-bold mb-3">Smart Routing</h3>
                    <p class="text-gray-500 leading-relaxed">Algorithms calculate the most efficient path to collect only the full bins.</p>
                </div>
                <div class="bg-white p-8 rounded-3xl shadow-sm hover:shadow-xl transition duration-300">
                    <div class="w-12 h-12 bg-orange-100 text-orange-600 rounded-2xl flex items-center justify-center mb-6"><Leaf size="24" /></div>
                    <h3 class="text-xl font-bold mb-3">Eco Impact</h3>
                    <p class="text-gray-500 leading-relaxed">Reduce carbon emissions by eliminating unnecessary trips and optimizing fuel usage.</p>
                </div>
            </div>
        </div>
    </section>

    <section id="team" class="container mx-auto px-6 py-24 text-center">
        <div class="max-w-2xl mx-auto mb-16">
            <div class="flex items-center justify-center gap-2 text-emerald-600 font-bold uppercase tracking-wider text-sm mb-4">
                <Users size="18" /> Our People
            </div>
            <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">Meet Team Enki</h2>
            <p class="text-gray-500 text-lg">We are a group of passionate engineering students dedicated to using technology for a cleaner, smarter future. Here are the faces behind the code!</p>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-8">
            <div v-for="member in teamMembers" :key="member.name" class="group">
                <div class="relative w-40 h-40 mx-auto mb-6">
                    <div class="absolute inset-0 rounded-full bg-emerald-100 scale-95 group-hover:scale-110 transition-transform duration-500 -z-10"></div>
                    <img :src="member.image" :alt="member.name" class="w-full h-full rounded-full object-cover border-4 border-white shadow-lg group-hover:shadow-xl transition duration-500" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-1">{{ member.name }}</h3>
                <p class="text-emerald-600 text-sm font-medium mb-4">{{ member.role }}</p>

                <div class="flex justify-center gap-4 opacity-0 group-hover:opacity-100 transition duration-300">
                    <a :href="member.github" class="text-gray-400 hover:text-gray-900 transition"><Github size="20" /></a>
                    <a :href="member.linkedin" class="text-gray-400 hover:text-blue-700 transition"><Linkedin size="20" /></a>
                </div>
            </div>
        </div>
    </section>

    <footer class="bg-black text-white py-12 rounded-t-[3rem]">
        <div class="container mx-auto px-6 flex flex-col md:flex-row justify-between items-center">
            <div class="mb-6 md:mb-0">
                <div class="text-2xl font-bold flex items-center gap-2">
                    <div class="w-6 h-6 bg-emerald-500 rounded-full"></div>
                    Smart Waste
                </div>
                <p class="text-gray-500 text-sm mt-2">© 2024 Team Enki. Engineering Project.</p>
            </div>
            <div class="flex gap-6 text-sm text-gray-400">
                <a href="#" class="hover:text-white transition">Privacy</a>
                <a href="#" class="hover:text-white transition">Documentation</a>
                <a href="#" class="hover:text-white transition">GitHub</a>
            </div>
        </div>
    </footer>

  </div>
</template>
