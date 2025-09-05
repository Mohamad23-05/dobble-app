<script setup lang="ts">
import DobbleLogo from '@/assets/svgs/dobbleLogo.svg'

const year = new Date().getFullYear()

</script>

<template>
<div class="footer-style">
  <DobbleLogo />
  <div class="my-info">
      <p>Mohamad Kadabashi - Medieniformatikstudent</p>
      <p class="mx-auto">{{year}} - Dobble Generator</p>
  </div>
</div>
</template>

<style scoped>
    @reference "@/assets/main.css";

    .footer-style {
      @apply flex bg-DarkSlateGray px-5 py-5 mt-3 justify-between items-center rounded-t-md;
    }

    .my-info{
      @apply flex flex-col items-start;
    }

    p{
      @apply !text-lg;
    }


</style>
