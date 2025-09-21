<script setup lang="ts">
import breakLine from '@/assets/svgs/break-line.svg';
import FanoPlane from '@/assets/svgs/Fano-Ebene-farbig.svg';
import DobblePair from '@/assets/img/Dobble-Pair.png'
import KartenDeckPlaneten from '@/assets/img/KartenDeckPlaneten.png'

</script>

<template>
  <!-- HERO (single h1 on page) -->
  <section class="bg-DarkSlateGray rounded-2xl mb-6 p-6 md:p-8">
    <h1 class="text-2xl md:text-3xl font-semibold mb-3">
      Build your own Dobble card set
    </h1>
    <p class="mb-4">
      Dobble works because of a neat bit of math: in a <strong>finite projective plane</strong>,
      any two lines meet in exactly one point — so any two cards share exactly one symbol.
      Want details? See below. Prefer to play? Generate a deck now.
    </p>
    <div class="flex flex-wrap gap-3">
      <RouterLink
        to="/generator"
        class="inline-flex items-center rounded-2xl px-4 py-2 bg-Vanilla text-black hover:opacity-90 transition"
        aria-label="Open the Dobble card generator"
      >
        Generate cards
      </RouterLink>
      <a
        href="https://www.dobblegame.com/en/homepage/"
        target="_blank" rel="noopener"
        class="inline-flex items-center rounded-2xl px-4 py-2 border border-Vanilla text-Vanilla hover:bg-Vanilla hover:text-black transition"
      >
        What is Dobble?
      </a>
    </div>
  </section>

  <!-- TWO COLUMNS -->
  <section class="flex flex-col md:flex-row gap-6">
    <!-- LEFT: why it works + Fano -->
    <div class="md:flex-1 bg-DarkSlateGray rounded-2xl p-6 space-y-4">
      <h1 class="text-xl md:text-2xl font-semibold">Why Dobble ↔ projective plane?</h1>

      <p class="text-sm opacity-90">
        Map <strong>cards → lines</strong> and <strong>symbols → points</strong>:
      </p>
      <ul class="list-disc pl-6 text-sm opacity-90 space-y-1">
        <li>Each line/card has <code>n + 1</code> points/symbols.</li>
        <li>Each point/symbol lies on <code>n + 1</code> lines/cards.</li>
        <li>Any two lines/cards meet in exactly one point/symbol.</li>
      </ul>

      <figure class="mt-2">
        <img
          :src="DobblePair"
          alt="Two Dobble cards illustrating the one-shared-symbol property"
          class="mx-auto w-full max-w-md rounded-xl shadow"
        />
        <figcaption class="mt-2 text-center text-xs text-Vanilla/70">
          Pick any two cards — there’s exactly one symbol in common.
        </figcaption>
      </figure>

      <h2 class="text-lg font-medium">The Fano plane (n = 2)</h2>
      <div class="w-full flex justify-center">
        <FanoPlane class="w-4/5 md:w-full max-w-md h-auto"/>
      </div>
    </div>

    <!-- DIVIDER -->
    <div class="w-full h-px bg-Auburn md:w-px md:h-auto md:self-stretch"></div>

    <!-- RIGHT: example deck + formal definition -->
    <div class="md:flex-1 bg-DarkSlateGray rounded-2xl p-6 space-y-4">
      <h1 class="text-xl md:text-2xl font-semibold">Example deck (planets, n = 2)</h1>
      <p class="text-sm opacity-90">
        Seven planet names (Jupiter, Venus, Uranus, Merkur, Neptun, Mars, Saturn) form a tiny set:
        <strong>7 cards</strong>, <strong>3 symbols per card</strong>, and any two cards share
        exactly one symbol.
      </p>
      <figure>
        <img
          :src="KartenDeckPlaneten"
          alt="Seven Dobble-style cards with planet names; any two cards share exactly one planet"
          class="mx-auto w-full max-w-xl rounded-xl shadow"
          loading="lazy"
        />
        <figcaption class="mt-2 text-center text-xs text-Vanilla/70">
          Try it: pick any two squares — find the single shared planet.
        </figcaption>
      </figure>

      <hr class="text-Vanilla my-2"/>

      <h1 class="text-lg font-medium">Formal definition</h1>
      <p class="text-sm opacity-90">A projective plane of order <em>n</em> has:</p>
      <ul class="list-disc pl-6 text-sm opacity-90">
        <li>exactly <code>n² + n + 1</code> lines, each containing <code>n + 1</code> points,</li>
        <li>each point lies on exactly <code>n + 1</code> lines, and</li>
        <li>any two distinct lines intersect in exactly one point.</li>
      </ul>
    </div>
  </section>
</template>


<style scoped>
@reference "@/assets/main.css";

.plane-def {
  @apply flex flex-col gap-2 sm:gap-9;
  @apply px-8 md:px-1.5;
}

.plane-prop {
  @apply flex flex-col  md:gap-7  list-disc list-inside;
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
