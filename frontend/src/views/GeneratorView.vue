<!-- GeneratorForm.vue -->
<script setup lang="ts">
import {userGenerator} from "@/composables/useGenerator.ts";
import SymbolsPicker from "@/components/SymbolsPicker.vue"

// add all available PNGs
const defaultSymbols = Object
  .entries(import.meta.glob('@/assets/symbols/*.{png,jpg,jpeg,webp,svg}', {
    eager: true,
    import: 'default',   // returns URL string for each asset
  }))
  .sort(([a], [b]) => a.localeCompare(b))
  .map(([, url]) => url as string);

const {
  mode, howMany, notation, howManyPlaceholder,
  n, symbolsPerCard, totalSymbols,
  valid, loading, error,
  cards, selectedSymbols,
  canGenerate, generateCtaText, generateDisabledReason,
  validateForm, generate,
} = userGenerator()

</script>

<template>
  <h1 class="title">
    The Generator
  </h1>

  <div class="content">
    <form class="mb-2" @submit.prevent="validateForm" aria-labelledby="g-title">
      <div class="panel pt-2">
        <h2 class="panel-title" id="g-title">
          Do you want to enter the order of the finite plane (n), symbol/card (s/c) or number of
          cards
          (k)?
        </h2>

        <!-- Row 1 -->
        <div class="row">
          <fieldset class="radios" role="radiogroup" aria-label="input mode">
            <legend class="sr-only">Input mode</legend>

            <label class="radio">
              <input class="sr-only peer" type="radio" name="mode" value="n" v-model="mode"/>
              <span class="dot" aria-hidden="true"></span>
              <span>n</span>
            </label>

            <label class="radio">
              <input class="sr-only peer" type="radio" name="mode" value="k" v-model="mode"/>
              <span class="dot" aria-hidden="true"></span>
              <span>k</span>
            </label>

            <label class="radio">
              <input class="sr-only peer" type="radio" name="mode" value="sc" v-model="mode"/>
              <span class="dot" aria-hidden="true"></span>
              <span>s/c</span>
            </label>
          </fieldset>

          <span>and how many?</span>

          <input
            class="qty"
            type="number"
            min="0"
            required
            :placeholder="howManyPlaceholder"
            v-model.number="howMany"
            aria-label="how many"
          />
        </div>
      </div>

      <!-- Row 2 -->
      <div class="panel pt-2">

        <h2 class="panel-title mt-3">
          Do you want to use numbers (n), letters (l) or symbols (s) for your cards?
        </h2>

        <div class="row">
          <fieldset class="radios" role="radiogroup" aria-label="notation">
            <legend class="sr-only">Notation</legend>

            <label class="radio">
              <input class="sr-only peer" type="radio" name="notation" value="n"
                     v-model="notation"/>
              <span class="dot" aria-hidden="true"></span>
              <span>n</span>
            </label>

            <label class="radio">
              <input class="sr-only peer" type="radio" name="notation" value="l"
                     v-model="notation"/>
              <span class="dot" aria-hidden="true"></span>
              <span>l</span>
            </label>

            <label class="radio">
              <input class="sr-only peer" type="radio" name="notation" value="s"
                     v-model="notation"/>
              <span class="dot" aria-hidden="true"></span>
              <span>s</span>
            </label>
          </fieldset>
        </div>
      </div>

      <div class="panel py-4">
        <button class="submit" type="submit">submit!</button>
      </div>
      <div class="panel pt-1">
        <!-- status -->
        <p v-if="notation === 'l'" class="!text-sm mt-1">
          Letters available: {{ 26 }}. Max feasible n: {{
            [2, 3, 4, 5, 7, 8, 9, 13].filter(n => n * n + n + 1 <= 26).join(', ') || 'none'
          }}.
        </p>
      </div>

      <div class="flex justify-start px-5 pt-2">
        <div v-if="loading" class="status text-Auburn">Checking…</div>
        <div
          v-if="error"
          class="status text-red-700"
        >
          {{ error }}
        </div>
        <div v-if="valid"
             class="status text-DarkSlateGray">
          the order n {{ n }} of the finite plane with symbols {{ symbolsPerCard }} each card with
          {{ totalSymbols }} cards totally and symbols: {{ totalSymbols }} is a valid cards-set.
        </div>
      </div>

    </form>
  </div>

  <!-- show picker for symbols mode -->
  <div v-if="valid && notation === 's'" class="panel mt-4">
    <SymbolsPicker
      v-model="selectedSymbols"
      :totalSymbols="totalSymbols || 0"
      :defaultSymbols="defaultSymbols"
      :allowUpload="true"
      :maxFileSizeMB="2"
      @error="msg => (/* show nicely or log */ console.warn(msg))"
    />
  </div>

  <!-- Generate button -->
  <div class="mt-3 flex items-center gap-3">
    <button
      class="submit disabled:opacity-50"
      :disabled="!canGenerate || loading"
      @click="generate"
      :title="generateDisabledReason"
    >
      {{ generateCtaText }}
    </button>

    <!-- Optional helper text showing why it’s disabled -->
    <span v-if="!canGenerate && generateDisabledReason" class="text-sm opacity-80">
    {{ generateDisabledReason }}
  </span>
  </div>

  <!-- Results -->
  <div v-if="cards.length" class="mt-6">
    <h3 class="text-xl text-DarkSlateGray font-bold mb-3">Generated Cards</h3>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="(card, idx) in cards"
        :key="idx"
        class="border rounded-lg p-3 bg-HunyadiYellow-Dark shadow text-center"
      >
        <h4 class="font-semibold mb-2">Card {{ idx + 1 }}</h4>
        <div class="flex flex-wrap justify-center gap-2">
        <span
          v-for="symbol in card"
          :key="symbol"
          class="px-2 py-1 rounded bg-gray-100 border"
        >
          <template v-if="symbol.startsWith('data:') || symbol.endsWith('.png')">
            <img :src="symbol" alt="" class="h-8 w-8 object-contain"/>
          </template>
          <template v-else>{{ symbol }}</template>
        </span>
        </div>
      </div>
    </div>
  </div>

</template>


<style scoped>
@reference "@/assets/main.css";

.panel-title {
  @apply !text-xl;
}

.title {
  @apply text-DarkSlateGray
}

/* ===== Layout ===== */
.panel {
  @apply flex justify-start items-center px-5 rounded-md gap-2.5 bg-DarkSlateGray text-white;
}

.row {
  @apply grid grid-cols-[auto_auto_1fr] justify-center items-center gap-x-6 gap-y-4 text-xl;
}


@media (max-width: 780px) {
  .row {
    grid-template-columns: 1fr;
    justify-items: center;
  }
}

/* ===== Radios ===== */
.radios {
  display: inline-flex;
  align-items: center;
  gap: 22px;
}

.radio {
  @apply inline-flex items-center cursor-pointer gap-2 select-none;
}

.sr-only {
  @apply !absolute w-0.5 h-0.5 p-0 m-[-1px] overflow-hidden whitespace-nowrap border-0;
}

/* coin circle */
.dot {
  @apply w-6 h-6 rounded-full bg-Vanilla border-2 border-solid;
  box-shadow: inset 0 0 0 2px gray;
  transition: transform .12s ease, box-shadow .12s ease;
}

/* checked = golden coin fill */
.peer:checked + .dot {
  @apply bg-Auburn;
  border: 3px solid gray;
  box-shadow: inset 0 0 0 2px rgba(255, 255, 255, .25);
  transition: transform .12s ease, box-shadow .12s ease;
}

.radio:hover .dot {
  transform: scale(1.05);
}

.peer:focus-visible + .dot {
  outline: 2px solid #60a5fa;
  outline-offset: 2px;
}


/* number input */
.qty {
  @apply flex flex-col w-20 justify-between items-center gap-x-3 text-2xl text-DarkSlateGray bg-Vanilla py-1.5 px-3 rounded-md;
  border: 4px solid var(--color-Auburn);
  box-shadow: 0 1px 0 rgba(255, 255, 255, .4) inset, 0 1px 2px gray;
}

/* custom symbols checkbox */
.own-symbols {
  @apply inline-flex items-center gap-2.5 whitespace-nowrap;
}

.own-symbols input {
  @apply w-6 h-6 accent-Auburn bg-Vanilla;
  box-shadow: inset 0 0 0 2px var(--color-Auburn);
  border: 3px solid var(--color-Auburn);
}


.status {
  @apply flex items-center justify-center w-auto px-4 py-1 gap-2.5
  text-xl bg-Vanilla rounded-md;
}

/* submit button */
.submit {
  @apply flex items-center justify-center px-12 py-1 gap-2.5 text-2xl  text-DarkSlateGray bg-Vanilla rounded-md;
  border: 4px solid var(--color-Auburn);
  box-shadow: 0 1px 0 rgba(255, 255, 255, .5) inset, 0 2px 0 var(--shadow);
  cursor: pointer;
}

.submit:hover {
  transform: translateY(-1px);
}

.submit:active {
  transform: translateY(0);
}
</style>
