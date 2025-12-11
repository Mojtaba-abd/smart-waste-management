// src/composables/useAnimateOnScroll.js
import { ref, onMounted, onUnmounted } from 'vue'

export function useAnimateOnScroll() {
  const elements = ref([])

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible')
          observer.unobserve(entry.target)
        }
      })
    },
    { threshold: 0.1 },
  ) // Trigger when 10% of element is visible

  onMounted(() => {
    // Select all elements marked with the data-animate attribute
    elements.value = document.querySelectorAll('[data-animate]')
    elements.value.forEach((el) => observer.observe(el))
  })

  onUnmounted(() => {
    observer.disconnect()
  })
}
