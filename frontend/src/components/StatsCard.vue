<script setup>
defineProps({
    title: { type: String, required: true },
    value: { type: [String, Number], default: 0 },
    color: { type: String, default: 'gray' }, // e.g., 'blue', 'red', 'green'
    icon: { type: String, default: '💡' }, // Emoji icon
    subtitle: { type: String, default: '' },
    loading: { type: Boolean, default: false }
})
</script>

<template>
    <div class="bg-white rounded-2xl shadow-lg p-6 flex items-start gap-4 transition-all duration-300 hover:shadow-xl hover:scale-[1.01] border-t-4"
         :class="[`border-${color}-500`]">

        <div class="flex-shrink-0">
            <div class="w-12 h-12 rounded-full flex items-center justify-center text-2xl shadow-inner"
                 :class="[`bg-${color}-100`]">
                {{ icon }}
            </div>
        </div>

        <div class="flex-grow">
            <h3 class="text-sm font-medium text-gray-500 uppercase tracking-wider mb-1">{{ title }}</h3>

            <div v-if="loading" class="animate-pulse">
                <div class="h-8 bg-gray-200 rounded w-3/4 mb-1"></div>
                <div class="h-3 bg-gray-200 rounded w-1/2"></div>
            </div>

            <div v-else>
                <p class="text-3xl font-extrabold" :class="[`text-${color}-600`]">{{ value }}</p>
                <p v-if="subtitle" class="text-xs text-gray-400 mt-0.5">{{ subtitle }}</p>
            </div>
        </div>
    </div>
</template>
