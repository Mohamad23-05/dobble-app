<script setup lang="ts">
import breakLine from '@/assets/svgs/break-line.svg';
// import FanoPlane from '@/assets/svgs/Fano-Ebene-farbig.svg';
const FanoPlane = "@/assets/svgs/Fano-Ebene-mono.png";
</script>

<template>
  <div class="content">
    <div class="title">
      <h1>
        The finite projective plane
      </h1>
    </div>

    <div class="plane-def">
      <h2>
        A projective plane of order n has the following properties:
      </h2>
      <ul class="plane-prop">
        <li>exactly n^2 + n + 1 lines, each line containing n + 1 points,</li>
        <li>each point lies on exactly n + 1 lines, and</li>
        <li>any two distinct lines intersect in exactly one point.</li>
      </ul>
    </div>

    <breakLine class="mx-auto h-auto my-4 lg:w-4xl sm:w-48"/>

    <div class="fano-plane">
      <h2>
        A very popular example of the projective plane is the Fano plane:
      </h2>
      <div class="py-5">
        <img src="@/assets/svgs/Fano-Ebene-mono.png" alt="">
      </div>
    </div>

    <breakLine class="mx-auto h-auto my-4 lg:w-4xl sm:w-48"/>

    <div class="generate-und-rules">
      <h2>
        With this knowledge, we have the possibility to generate the game
        <a href="https://www.dobblegame.com/en/homepage/" target="_blank">Dobble</a>.
      </h2>
      <p>
        <RouterLink to="/generator" class="link"> Generate</RouterLink>
        and create your own card sets.
      </p>
    </div>

  </div>
</template>

<style scoped>
@reference "@/assets/main.css";

.plane-def {
  @apply flex flex-col items-center gap-2 sm:gap-9;
}

.plane-prop {
  @apply flex flex-col items-start gap-3 sm:gap-7  list-disc list-inside;
}

li {
  @apply text-white font-light leading-normal text-2xl;
}

.fano-plane {
  @apply flex flex-col items-center gap-6 ;
}

.generate-und-rules {
  @apply flex flex-col items-center gap-2 px-6;
}


</style>
