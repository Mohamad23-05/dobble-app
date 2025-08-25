<script setup lang="ts">
import Nav from '@/components/NavBar.vue'
import Footer from '@/components/AppFooter.vue'
import GeneratorView from "@/views/GeneratorView.vue";
import dobbleLogo from '@/assets/svgs/dobbleLogo.svg'
</script>

<template>
    <div class="nav-style">
      <RouterLink to="/">
        <dobbleLogo></dobbleLogo>
      </RouterLink>

      <div class="nav-pages">
        <RouterLink class="nav-link" to="/generator">Generator</RouterLink>
        <RouterLink class="nav-link" to="/about">About</RouterLink>
      </div>
    </div>
</template>

<style scoped>
    @reference "@/assets/main.css";

    .nav-style {
      @apply flex px-5 py-5 mb-9 items-center justify-between bg-DarkSlateGray rounded-b-md;
    }

    .nav-pages {
      @apply flex items-center self-stretch;

    }

    .nav-link{
      @apply text-HunyadiYellow-Dark px-3 py-2 rounded-md text-2xl;
      @apply hover:underline hover:text-DarkSlateGray hover:bg-Vanilla transition-all duration-300 ease-in-out;

    }
</style>

