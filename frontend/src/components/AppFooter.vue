<script setup lang="ts">
import DobbleLogo from '@/assets/svgs/dobbleLogo.svg'

const year = new Date().getFullYear()
</script>

<template>
  <div
    class="footer-style flex flex-col items-center justify-center gap-3
           bg-DarkSlateGray rounded-t-md mt-3 px-4 py-4
           md:flex-row md:justify-between md:px-6 md:py-5
           lg:px-8 lg:py-6"
  >
    <DobbleLogo class="w-40 md:w-40 lg:w-52"/>
    <div class="my-info">
      <p class="text-base md:text-lg lg:text-xl">
        Mohamad Kadabashi - media informatics student
      </p>
      <p class="mx-auto md:mx-0 text-base md:text-lg lg:text-xl">
        {{ year }} - Dobble Generator
      </p>
    </div>
  </div>
</template>

<style scoped>
@reference "@/assets/main.css";

.my-info {
  @apply flex flex-col items-center md:items-start text-center md:text-left;
}
</style>
