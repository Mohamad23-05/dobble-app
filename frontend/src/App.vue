<script setup>
import {RouterLink, RouterView} from 'vue-router'
import {computed} from 'vue'
import {useRoute} from 'vue-router'
import NavBar from "@/components/NavBar.vue";
import AppFooter from "@/components/AppFooter.vue";

const route = useRoute()
</script>

<template>
  <NavBar/>
  <div class="flex flex-col">
    <main class="main-container-styler">
      <RouterView/>
    </main>
    <AppFooter/>
  </div>
</template>

<style scoped>
@reference "@/assets/main.css";

</style>

