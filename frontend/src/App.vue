<script setup>
import {RouterLink, RouterView} from 'vue-router'
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import NavBar from "@/components/NavBar.vue";
import AppFooter from "@/components/AppFooter.vue";

const route = useRoute()
</script>

<template>
    <NavBar />
  <div class="flex items-center justify-center">
    <div class="finite-plane">
      <RouterView />
    </div>
  </div>
    <AppFooter />
</template>

<style scoped>
    @reference "@/assets/main.css";
  .finite-plane {
    @apply inline-flex py-9 px-10 flex-col items-center gap-12 bg-DarkSlateGray rounded-md mx-auto;
  }
</style>

