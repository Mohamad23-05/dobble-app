<script setup lang="ts">
import {buildSymbolDefs, exportPdf, userGenerator} from "@/composables/useGenerator.ts";
import SymbolsPicker from "@/components/SymbolsPicker.vue"
import {ref, computed} from "vue"

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

const hasValidation = computed(() => !loading.value && (valid.value || !!error.value))

const validationTitle = computed(() =>
  valid.value ? 'Form is valid' : !!error.value ? 'Form is not valid' : ''
)

// Allowed n values (kept in sync with backend list)
const ALLOWED_N = [2, 3, 4, 5, 7]
const allowedNText = computed(() => ALLOWED_N.join(', '))
const allowedCText = computed(() => ALLOWED_N.map(x => x * x + x + 1).join(', '))
const allowedSCText = computed(() => ALLOWED_N.map(x => x + 1).join(', '))

// Friendlier message beside the SVG
const validationMessage = computed(() => {
  if (valid.value) {
    // Positive, concise, and actionable
    const k = totalSymbols.value
    return `Looks good: n=${n.value}. Each card has ${symbolsPerCard.value} symbols, total cards ${k}. ${generateCtaText.value}.`
  }

  // Invalid: provide specific guidance by mode, plus server feedback if any.
  const reason = error.value ? String(error.value) : 'Invalid input.'
  if (mode.value === 'n') {
    const hint = `Allowed n values: ${allowedNText.value}.`
    // If user typed a number, show a direct n-specific message.
    return howMany.value != null
      ? `n=${howMany.value} is not supported. ${hint}`
      : `${reason} ${hint}`
  }
  if (mode.value === 'k') {
    const hint = `Enter a cards count C in: ${allowedCText.value}.`
    return `${reason} ${hint}`
  }
  // mode === 'sc'
  const hint = `Enter symbols per card (S/C) in: ${allowedSCText.value}.`
  return `${reason} ${hint}`
})


// --- Export banner state ---
const exporting = ref(false)
const exportPhase = ref<'upload' | 'processing' | 'download' | 'done' | null>(null)
const exportPercent = ref<number | null>(null)
const exportError = ref<string | null>(null)

const exportLabel = computed(() => {
  switch (exportPhase.value) {
    case 'upload':
      return 'Uploading request…'
    case 'processing':
      return 'Rendering PDF…'
    case 'download':
      return 'Downloading PDF…'
    case 'done':
      return 'Done'
    default:
      return 'Preparing…'
  }
})


async function onExport() {
  exporting.value = true
  exportPhase.value = null
  exportPercent.value = null
  exportError.value = null

  const defs = buildSymbolDefs(notation.value, totalSymbols.value!, selectedSymbols.value)
  try {
    await exportPdf({
      n: n.value!,
      symbolsPerCard: symbolsPerCard.value!,
      numCards: totalSymbols.value!,
      cards: cards.value,
      symbolDefs: defs,
      onProgress: ({phase, percent}) => {
        exportPhase.value = phase
        exportPercent.value = percent ?? null
      }
    })
  } catch (e: any) {
    exportError.value = e?.message || 'Export failed'
  } finally {
    // Keep the banner briefly on "done" for UX, then hide
    if (exportPhase.value === 'done' && !exportError.value) {
      setTimeout(() => {
        exporting.value = false
      }, 600)
    } else {
      exporting.value = false
    }
  }
}
</script>

<template>
  <!-- Export banner -->
  <transition name="fade">
    <div
      v-if="exporting"
      class="fixed top-0 left-0 right-0 z-50 flex items-center gap-4 px-4 py-2 bg-HunyadiYellow-Dark text-white shadow-md"
      role="status"
      aria-live="polite"
    >
      <div class="flex-1">
        <div class="font-semibold">{{ exportLabel }}</div>
        <div class="h-2 mt-2 w-full bg-white/20 rounded overflow-hidden">
          <div
            class="h-full bg-Vanilla transition-all"
            :style="exportPercent != null ? { width: exportPercent + '%' } : { width: '30%', animation: 'indet 1.2s linear infinite' }"
          />
        </div>
      </div>
      <div v-if="exportPercent != null" class="min-w-[3rem] text-right tabular-nums">
        {{ exportPercent }}%
      </div>
      <button
        type="button"
        class="ml-2 px-3 py-1 rounded bg-white/10 hover:bg-white/20"
        @click="exporting = false"
        aria-label="Hide export status"
      >
        ✕
      </button>
    </div>
  </transition>

  <h1 class="title">
    The Generator
  </h1>

  <div class="content">
    <form class="mb-2" @submit.prevent="validateForm" aria-labelledby="g-title">
      <div class="panel pt-2">
        <h2 class="panel-title" id="g-title">
          Do you want to enter the order of the finite plane (N), number of
          cards (C) or symbol/card (S/C)?
        </h2>
      </div>

      <div class="panel pt-2">
        <!-- Row 1 -->
        <div class="row">
          <!-- Replaced radios: Input mode -->
          <div class="icon-radios" role="radiogroup" aria-label="input mode">
            <button
              type="button"
              class="icon-radio"
              :class="mode === 'n' ? 'is-selected' : ''"
              role="radio"
              :aria-checked="mode === 'n'"
              @click="mode = 'n'"
              title="Enter order n"
            >
              <!-- Grid/N icon -->
              <svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true">
                <rect x="3" y="3" width="7" height="7" rx="1.2"/>
                <rect x="14" y="3" width="7" height="7" rx="1.2"/>
                <rect x="3" y="14" width="7" height="7" rx="1.2"/>
                <rect x="14" y="14" width="7" height="7" rx="1.2"/>
              </svg>
              <span>N</span>
            </button>

            <button
              type="button"
              class="icon-radio"
              :class="mode === 'k' ? 'is-selected' : ''"
              role="radio"
              :aria-checked="mode === 'k'"
              @click="mode = 'k'"
              title="Enter number of cards k"
            >
              <!-- Stack/Cards icon -->
              <svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true">
                <path d="M7 6h10a2 2 0 0 1 2 2v7H9a2 2 0 0 1-2-2V6z"/>
                <path d="M5 9h10a2 2 0 0 1 2 2v7H7a2 2 0 0 1-2-2V9z" opacity=".5"/>
              </svg>
              <span>C</span>
            </button>

            <button
              type="button"
              class="icon-radio"
              :class="mode === 'sc' ? 'is-selected' : ''"
              role="radio"
              :aria-checked="mode === 'sc'"
              @click="mode = 'sc'"
              title="Enter symbols per card s/c"
            >
              <!-- S/C icon -->
              <svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true">
                <circle cx="8" cy="8" r="3"/>
                <circle cx="16" cy="16" r="3"/>
                <path d="M10.5 10.5l3 3" stroke="currentColor" stroke-width="2" fill="none"
                      stroke-linecap="round"/>
              </svg>
              <span>S/C</span>
            </button>
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
            <div class="panel" v-if="mode === 'n'" aria-live="polite">
              <p class="!text-sm">

                Allowed order n of a finite plane: {{ allowedNText }}
              </p>
            </div>
          </div>


        </div>
      </div>

      <!-- Row 2 -->
      <div class="panel pt-2">
        <h2 class="panel-title mt-3">
          Do you want to use numbers, letters or symbols for your cards?
        </h2>
      </div>

      <div class="panel pt-2">
        <div class="row">
          <!-- Replaced radios: Notation -->
          <div class="icon-radios" role="radiogroup" aria-label="notation">
            <button
              type="button"
              class="icon-radio"
              :class="notation === 'n' ? 'is-selected' : ''"
              role="radio"
              :aria-checked="notation === 'n'"
              @click="notation = 'n'"
              title="Numbers"
            >
              <!-- 123 icon -->
              <svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true">
                <path d="M5 17h2V7H5l-2 2v2l2-2v8zM11 17h6v-2h-3.6l3.5-4.2V9h-6v2h3.2L11 15.2V17z"/>
              </svg>
              <span>Numbers</span>
            </button>

            <button
              type="button"
              class="icon-radio"
              :class="notation === 'l' ? 'is-selected' : ''"
              role="radio"
              :aria-checked="notation === 'l'"
              @click="notation = 'l'"
              title="Letters"
            >
              <!-- Letter A icon -->
              <svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true">
                <path d="M12 4l7 16h-2.6l-1.7-4H9.3l-1.7 4H5L12 4zm-1.6 9h3.2L12 7.9 10.4 13z"/>
              </svg>
              <span>Letters</span>
            </button>

            <button
              type="button"
              class="icon-radio"
              :class="notation === 's' ? 'is-selected' : ''"
              role="radio"
              :aria-checked="notation === 's'"
              @click="notation = 's'"
              title="Symbols"
            >
              <!-- Sparkle icon -->
              <svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true">
                <path
                  d="M12 3l2 4 4 2-4 2-2 4-2-4-4-2 4-2 2-4zM18 14l1 2 2 1-2 1-1 2-1-2-2-1 2-1 1-2z"/>
              </svg>
              <span>Symbols</span>
            </button>
          </div>
          <div class="panel pt-1">
            <p v-if="notation === 'l'" class="!text-sm">
              Letters available: {{ 26 }}. Max feasible n: {{
                [2, 3, 4, 5, 7, 8, 9, 13].filter(n => n * n + n + 1 <= 26).join(', ') || 'none'
              }}.
            </p>
          </div>
        </div>
      </div>

      <div class="panel pt-4">
        <button class="submit" type="submit">submit!</button>
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
    <!-- SVG validity indicator with explanation -->
    <div v-if="loading" class="status text-Auburn">Checking…</div>
    <div
      v-if="hasValidation"
      class="inline-flex items-center gap-2 rounded-[12px] px-2 py-1"
      aria-live="polite"
      :title="validationTitle"
    >
      <!-- Valid -->
      <svg v-if="valid" viewBox="0 0 24 24" width="28" height="28" class="text-green-700" role="img"
           aria-label="Valid">
        <circle cx="12" cy="12" r="10" class="fill-green-100 stroke-green-600" stroke-width="1.5"/>
        <path d="M7 12.5l3 3 7-7" class="stroke-green-700" fill="none" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <!-- Invalid -->
      <svg v-else viewBox="0 0 24 24" width="28" height="28" class="text-red-700" role="img"
           aria-label="Invalid">
        <circle cx="12" cy="12" r="10" class="fill-red-100 stroke-red-600" stroke-width="1.5"/>
        <path d="M8.5 8.5l7 7M15.5 8.5l-7 7" class="stroke-red-700" fill="none" stroke-width="2"
              stroke-linecap="round"/>
      </svg>

      <span
        class="text-sm"
        :class="valid ? 'text-green-800' : 'text-red-800'"
      >
        {{ validationMessage }}
      </span>
    </div>

    <!-- Optional helper text showing why it’s disabled -->
    <span v-if="!canGenerate && generateDisabledReason" class="text-sm opacity-80">
      {{ generateDisabledReason }}
    </span>

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
  <!-- Results -->
  <div v-if="cards.length" class="mt-6 gap-2.5 rounded">
    <h3 class="text-xl text-DarkSlateGray font-bold mb-3">Generated Cards</h3>
    <button class="submit mb-4" @click="onExport">Export to PDF</button>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="(card, idx) in cards"
        :key="idx"
        class="border rounded-2xl p-3 bg-HunyadiYellow-Dark shadow text-center"
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

/* Simple fade for banner */
.fade-enter-active, .fade-leave-active {
  transition: opacity .15s ease
}

.fade-enter-from, .fade-leave-to {
  opacity: 0
}

/* Indeterminate bar animation */
@keyframes indet {
  0% {
    margin-left: 0%;
    width: 15%
  }
  50% {
    margin-left: 60%;
    width: 30%
  }
  100% {
    margin-left: 100%;
    width: 15%
  }
}

.panel-title {
  @apply !text-xl;
}

.title {
  @apply text-DarkSlateGray
}

/* ===== Layout ===== */
.panel {
  @apply flex justify-start items-center px-5 rounded-2xl gap-2.5 bg-DarkSlateGray text-white;
}

.row {
  @apply grid grid-cols-[auto_auto_1fr] justify-center items-center gap-x-6 gap-y-4 text-xl;
}

/* ===== Icon radios ===== */
.icon-radios {
  display: inline-flex;
  align-items: center;
  gap: 14px;
  /* allow wrapping to prevent overflow on narrow screens */
  flex-wrap: wrap;
  width: 100%;
}

.icon-radio {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 10px;
  color: #0f172a; /* slate-900 */
  background: #faf6e5; /* Vanilla-ish */
  border: 2px solid var(--color-Auburn);
  box-shadow: 0 1px 0 rgba(255, 255, 255, .4) inset, 0 1px 2px rgba(0, 0, 0, .25);
  cursor: pointer;
  transition: transform .12s ease, box-shadow .12s ease, background-color .12s ease;
}

.icon-radio:hover {
  transform: translateY(-1px);
}

.icon-radio:active {
  transform: translateY(0);
}

.icon-radio svg {
  fill: currentColor;
}

.icon-radio.is-selected {
  background: #f3d08d;
  box-shadow: 0 1px 0 rgba(255, 255, 255, .5) inset, 0 2px 0 var(--shadow);
  outline: 2px solid #e3a00833;
}

/* number input */
.qty {
  @apply flex flex-col w-20 justify-between items-center gap-x-3 text-2xl text-DarkSlateGray bg-Vanilla py-1.5 px-3 rounded-2xl;
  border: 4px solid var(--color-Auburn);
  box-shadow: 0 1px 0 rgba(255, 255, 255, .4) inset, 0 1px 2px gray;
}

.status {
  @apply flex items-center justify-center w-auto px-4 py-1 gap-2.5 text-xl bg-Vanilla rounded-2xl;
}

/* submit button */
.submit {
  @apply flex items-center justify-center px-12 py-1 gap-2.5 text-2xl text-DarkSlateGray bg-Vanilla rounded-2xl;
  border: 2px solid var(--color-Auburn);
  box-shadow: 0 1px 0 rgba(255, 255, 255, .5) inset, 0 2px 0 var(--shadow);
  cursor: pointer;
}

.submit:hover {
  transform: translateY(-1px);
  background: #f3d08d;

}

.submit:active {
  transform: translateY(0);
}

/* ===== Responsive (use concrete values equivalent to your vars) ===== */
/* --breakpoint-lg: 976px; --breakpoint-md: 768px; --breakpoint-sm: 360px; */

/* <= 976px: tighten gaps/padding and switch rows to single column earlier */
@media (max-width: 976px) {
  .row {
    grid-template-columns: 1fr;
    justify-items: stretch;
    column-gap: 1rem;
  }

  .panel {
    padding-inline: 1rem;
  }

  .icon-radios {
    justify-content: center;
  }

  .icon-radio {
    /* three per row when space allows */
    flex: 1 1 calc(33.333% - 12px);
    min-width: 150px;
    justify-content: center;
  }

  .qty {
    width: 100%;
    max-width: 360px;
  }

  .submit {
    width: 100%;
    max-width: 420px;
  }

  .status {
    width: 100%;
  }
}

/* <= 768px: two-per-row radios and smaller text to avoid overflow */
@media (max-width: 768px) {
  .icon-radio {
    flex: 1 1 calc(50% - 12px);
    min-width: 140px;
  }

  .panel-title {
    font-size: 1.125rem; /* ~text-lg */
  }
}

/* <= 360px: stack everything vertically, full-width controls */
@media (max-width: 360px) {
  .title {
    font-size: 1.375rem; /* ~text-xl */
    line-height: 1.2;
  }

  .icon-radio {
    flex: 1 1 100%;
    width: 100%;
  }

  .qty {
    max-width: 100%;
    font-size: 1.125rem;
  }

  .submit {
    max-width: 100%;
    padding-inline: 1rem;
    font-size: 1.125rem;
  }

  .panel {
    gap: 0.5rem;
    padding-inline: 0.75rem;
  }
}
</style>
