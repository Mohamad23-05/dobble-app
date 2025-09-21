<script setup lang="ts">
import breakLine from '@/assets/svgs/break-line.svg';
import FanoPlane from '@/assets/svgs/Fano-Ebene-farbig.svg';
</script>

<template>

  <div class="generate-und-rules bg-DarkSlateGray rounded-2xl mb-4 py-5">
    <p>
      If you are interested in the theory behind <strong> the projective plane</strong>, you can
      read more about it down below.
      <br>
      if Not, you can generate your own card sets of
      <a href="https://www.dobblegame.com/en/homepage/" target="_blank">Dobble</a> >
      <RouterLink to="/generator" class="link"> here</RouterLink>
    </p>
  </div>

  <div class="flex flex-col md:flex-row gap-4">

    <!-- left block -->
    <div class="md:flex-1 bg-DarkSlateGray rounded-2xl space-y-4 px-3 py-10">
      <div class="lex flex-col items-center">
        <h1 class="px-4">The finite projective plane</h1>
      </div>

      <div class="plane-def px-5">
        <h2 class="">A projective plane of order n has the following properties:</h2>
        <ul class="plane-prop">
          <li>exactly n^2 + n + 1 lines, each line containing n + 1 points,</li>
          <li>each point lies on exactly n + 1 lines, and</li>
          <li>any two distinct lines intersect in exactly one point.</li>
        </ul>
      </div>
    </div>

    <!-- divider: horizontal on mobile, vertical on md+ -->
    <div class="w-full h-px bg-Vanilla md:w-px md:h-auto md:self-stretch"></div>

    <!-- right block -->
    <div class="md:flex-1 bg-DarkSlateGray rounded-2xl space-y-4">
      <div class="fano-plane">
        <div class="w-full flex justify-center">
          <FanoPlane class="w-2/4 h-auto"/>
        </div>
        <h2>A very popular example of the projective plane is the Fano plane:</h2>
      </div>
    </div>
  </div>
</template>

<style scoped>
@reference "@/assets/main.css";

.plane-def {
  @apply flex flex-col gap-2 sm:gap-9;
  @apply px-8 md:px-1.5;
}

.plane-prop {
  @apply flex flex-col gap-1 md:gap-7  list-disc list-inside;
}

li {
  @apply text-white font-light leading-normal text-2xl;
  @apply text-xl md:text-2xl;
}

.fano-plane {
  @apply flex flex-col items-center gap-6 py-4 ;
}

.generate-und-rules {
  @apply flex flex-col items-start gap-2 px-6;
}


</style>
