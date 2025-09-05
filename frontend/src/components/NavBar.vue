<script setup lang="ts">
import { ref } from 'vue'
import DobbleLogo from '@/assets/svgs/dobbleLogo.svg'
import hamMenu from '@/assets/svgs/menu-burger.svg'
const isOpen = ref(false)
const toggle = () => (isOpen.value = !isOpen.value)
const close = () => (isOpen.value = false)
</script>

<template>
  <div class="nav-style">
    <RouterLink to="/" class="flex items-center" @click="close">
      <DobbleLogo />
    </RouterLink>

    <!-- Desktop links: show from md and up -->
    <nav class="nav-pages hidden md:flex gap-2">
      <RouterLink class="nav-link link" to="/generator">Generator</RouterLink>
      <RouterLink class="nav-link link" to="/about">About</RouterLink>
    </nav>

    <!-- Hamburger: only on < md -->
    <button
      class="md:hidden inline-flex items-center justify-center rounded-md px-3 py-2
             text-HunyadiYellow-Dark hover:bg-Vanilla hover:text-DarkSlateGray
             transition-all duration-200 ease-in-out"
      @click="toggle"
      aria-label="Open menu"
      :aria-expanded="isOpen"
    >
      <hamMenu class="w-6 h-6 text-Vanilla"/>
    </button>
  </div>

  <!-- Mobile dropdown -->
  <transition
    enter-active-class="transition duration-200 ease-out"
    enter-from-class="opacity-0 -translate-y-2"
    enter-to-class="opacity-100 translate-y-0"
    leave-active-class="transition duration-150 ease-in"
    leave-from-class="opacity-100 translate-y-0"
    leave-to-class="opacity-0 -translate-y-2"
  >
    <div v-show="isOpen" class="md:hidden px-5 mb-4">
      <nav class="flex flex-col gap-2 bg-DarkSlateGray rounded-md p-3">
        <RouterLink class="nav-link link" to="/generator" @click="close">Generator</RouterLink>
        <RouterLink class="nav-link link" to="/about" @click="close">About</RouterLink>
      </nav>
    </div>
  </transition>
</template>

<style scoped>
/* keep your styles, but don't set display on nav-pages */
  @reference "@/assets/main.css";

.nav-style {
  @apply flex px-5 py-5 mb-9 items-center justify-between bg-DarkSlateGray rounded-b-md;
}
.nav-pages {
  @apply items-center self-stretch; /* removed 'flex' so hidden/md:flex works */
}
.nav-link {
  @apply text-HunyadiYellow-Dark px-3 py-2 rounded-md text-2xl;
}
</style>
