<script setup lang="ts">
import breakLine from '@/assets/svgs/break-line.svg';
import FanoPlane from '@/assets/svgs/Fano-Ebene-farbig.svg';
import DobblePair from '@/assets/img/Dobble-Pair.png'
import KartenDeckPlaneten from '@/assets/img/Kartenset_PlanetenV2.png'

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
    <!-- LEFT: Intro + why it works + Fano -->
    <div class="md:flex-1 bg-DarkSlateGray rounded-2xl p-6 space-y-4">
      <h1 class="text-xl md:text-2xl font-semibold">What is a projective plane?</h1>
      <p class="text-sm opacity-90">
        A projective plane is a special <em>incidence structure</em> that plays a central role
        in geometry and combinatorics. Formally, it consists of a set of
        <strong>points</strong> <code>P</code>, a set of <strong>lines</strong> <code>L</code>,
        and an incidence relation <code>I ⊆ P × L</code> that specifies which points lie on which
        lines. The points and lines are represent <strong>symbols</strong> and
        <strong>cards</strong>
        in Dobble.
        A projective plane satisfies the following axioms:
      </p>
      <ul class="list-disc pl-6 text-sm opacity-90 space-y-1">
        <li>Any two distinct points lie on exactly one common line.</li>
        <li>Any two distinct lines meet in exactly one point (no parallels).</li>
        <li>There are at least four points, with no three on a single line (to avoid a degenerate
          case).
        </li>
      </ul>
      <p class="text-sm opacity-90">
        You can model this with drawings (like the Fano figure below) or with combinatorial sets.
        Dobble uses the same structure: treat symbols like points, cards like lines and plane like
        whole dobble card-set.
      </p>
      <h2 class="text-lg font-medium">The Fano plane (n = 2)</h2>
      <div class="w-full flex justify-center">
        <FanoPlane class="w-4/5 md:w-full max-w-md h-auto"/>
      </div>
      <p class="text-sm opacity-90 mt-2">
        Finite case (order <em>n</em>):
      </p>
      <ul class="list-disc pl-6 text-sm opacity-90">
        <li>Exactly <code>n² + n + 1</code> points and <code>n² + n + 1</code> lines.</li>
        <li>Each line contains <code>n + 1</code> points; each point lies on <code>n + 1</code>
          lines.
        </li>
        <li>Any two distinct lines intersect in exactly one point; any two distinct points determine
          exactly one line.
        </li>
      </ul>
    </div>

    <!-- DIVIDER -->
    <div class="w-full h-px bg-Auburn md:w-px md:h-auto md:self-stretch"></div>

    <!-- RIGHT: example deck + definitions -->
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

      <h2 class="text-lg my-3 font-medium">Why Dobble ↔ projective plane?</h2>
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
