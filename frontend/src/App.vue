<script setup lang="ts">
import {RouterLink, RouterView} from 'vue-router'
import {computed} from 'vue'
import {useRoute} from 'vue-router'
import NavBar from "@/components/NavBar.vue";
import AppFooter from "@/components/AppFooter.vue";

const route = useRoute()
</script>
<!-- App.vue -->
<template>
  <div class="min-h-screen flex flex-col">   <!-- full height container -->
    <NavBar/>

    <main class="flex-1">                     <!-- takes remaining space -->
      <RouterView/>
    </main>

    <AppFooter/>                             <!-- sits at bottom -->
  </div>
</template>


<style scoped>
@reference "@/assets/main.css";

</style>

