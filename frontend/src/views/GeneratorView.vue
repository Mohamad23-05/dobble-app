<!-- GeneratorForm.vue -->
<script setup lang="ts">
import {userGenerator} from "@/composables/useGenerator.ts";

const {
  // state
  mode, howMany, notation, howManyPlaceholder,
  n, symbolsPerCard, totalSymbols,
  valid, loading, error,

  // cards & symbols
  cards, universe, availableSymbols, selectedSymbols,

  // computed
  canGenerate, generateCtaText, generateDisabledReason,

  // actions
  validateForm, toggleSymbol, generate,

} = userGenerator();
</script>

<template>
  <h2 class="title">
    The Generator
  </h2>

  <div class="content-section">
    <form class="panel mb-2" @submit.prevent="validateForm" aria-labelledby="g-title">
      <h2 id="g-title">
        Do you want to enter the order of the finite plane (n), symbol/card (s/c) or number of cards
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
          :placeholder="howManyPlaceholder"
          v-model.number="howMany"
          aria-label="how many"
        />
      </div>

      <!-- Row 2 -->
      <h2 class="panel-title mt-3">
        Do you want to use numbers (n), letters (l) or symbols (s) for your cards?
      </h2>

      <div class="row">
        <fieldset class="radios" role="radiogroup" aria-label="notation">
          <legend class="sr-only">Notation</legend>

          <label class="radio">
            <input class="sr-only peer" type="radio" name="notation" value="n" v-model="notation"/>
            <span class="dot" aria-hidden="true"></span>
            <span>n</span>
          </label>

          <label class="radio">
            <input class="sr-only peer" type="radio" name="notation" value="l" v-model="notation"/>
            <span class="dot" aria-hidden="true"></span>
            <span>l</span>
          </label>

          <label class="radio">
            <input class="sr-only peer" type="radio" name="notation" value="s" v-model="notation"/>
            <span class="dot" aria-hidden="true"></span>
            <span>s</span>
          </label>
        </fieldset>
      </div>

      <button class="submit" type="submit">submit!</button>

      <!-- status -->
      <p v-if="notation === 'l'" class="text-sm opacity-75 mt-1">
        Letters available: {{ 26 }}. Max feasible n: {{
          [2, 3, 4, 5, 7, 8, 9, 13].filter(n => n * n + n + 1 <= 26).join(', ') || 'none'
        }}.
      </p>

      <div v-if="loading" class="mt-2  text-Auburn">Checking…</div>
      <div v-if="error" class="mt-2 px-3 py-2 rounded-md bg-Vanilla text-red-700">{{ error }}</div>
      <div v-if="valid"
           class="mt-2 px-3 py-2 rounded-md text-sm bg-Vanilla text-DarkSlateGray">
        n: {{ n }} of the finite plane with symbols {{ symbolsPerCard }} each card with total
        symbols: {{ totalSymbols }}
      </div>
    </form>
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
    <h3 class="text-xl font-bold mb-3">Generated Cards</h3>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="(card, idx) in cards"
        :key="idx"
        class="border rounded-lg p-3 bg-white shadow text-center"
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

.content-section {
}

.title {
  @apply text-DarkSlateGray
}

/* ===== Layout ===== */
.panel {
  @apply flex flex-col justify-between items-center p-7 rounded-md gap-2.5 bg-DarkSlateGray text-white;
}

.row {
  @apply grid grid-cols-[auto_auto_1fr] justify-center items-center gap-x-6 gap-y-4 text-2xl;
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
