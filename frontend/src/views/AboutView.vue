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
        I have implemented this generator to be able to construct a ‘Dobble’ card set.
        The generator is based on the mathematical concept of a projective plane.
      </p>
      <p>
        It is only for educational purposes. If you want to buy the game Dobble, you can visit
        the official website: <a
        href="https://www.dobblegame.com/en/homepage/" target="_blank" rel="noopener">Dobble</a>.
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
