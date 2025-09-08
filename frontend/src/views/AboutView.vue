<script setup lang="ts">

</script>

<template>
  <div class="content">
    <div class="about-me">
      <h1>
        This is the bachelor’s thesis of Mohamad Kadabashi.
      </h1>
      <h2>
        I'm Mohamad Kadabashi and studying media informatics at HTWD.
      </h2>
      <p>
        I have implemented a generator here to be able to construct a ‘Dobble’ card set.
      </p>
    </div>
  </div>
</template>

<style scoped>

.about-me {
  @reference "@/assets/main.css";

  @apply flex flex-col py-4 justify-center items-center text-center sm:px-4 gap-2.5;
}

</style>
