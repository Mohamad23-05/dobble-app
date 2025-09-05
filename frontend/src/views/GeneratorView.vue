<!-- GeneratorForm.vue -->
<script setup lang="ts">
import {ref} from 'vue'

/** form state */
const mode = ref<'n' | 'k' | 'sc'>('n')         // n, k, s/c
const howMany = ref<number | null>(null)

const notation = ref<'n' | 'l' | 's'>('n')      // numbers, letters, symbols
const useCustomSymbols = ref(false)

const submit = () => {
  // do what you need here or emit an event
  // e.g., emit('submit', { mode: mode.value, howMany: howMany.value, notation: notation.value, useCustomSymbols: useCustomSymbols.value })
  console.log({
    mode: mode.value,
    howMany: howMany.value,
    notation: notation.value,
    useCustomSymbols: useCustomSymbols.value
  })
}
</script>

<template>
  <h2 class="title">
    The Generator
  </h2>

  <div class="content-section">
    <form class="panel mb-2" @submit.prevent="submit" aria-labelledby="g-title">
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
          :placeholder="mode === 'n' ? 'n' : mode === 'k' ? 'k' : 's/c'"
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

        <label v-if="notation === 's'" class="own-symbols">
          <input type="checkbox" v-model="useCustomSymbols"/>
          <span>with my own symbols</span>
        </label>
      </div>

      <button class="submit" type="submit">submit!</button>
    </form>
    <div v-if="useCustomSymbols" class="content my-2"></div>
    <div v-else class="bg-Auburn py-5 rounded-md my-2"></div>
    <div class="content mt-2"></div>
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
  @apply flex flex-col justify-between items-center gap-x-6 text-2xl text-DarkSlateGray bg-Vanilla py-1.5 px-3 rounded-md;
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
