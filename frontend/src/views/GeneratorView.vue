<script setup lang="ts">
import {buildSymbolDefs, exportPdf, userGenerator} from "@/composables/useGenerator.ts";
import SymbolsPicker from "@/components/SymbolsPicker.vue"
import {ref, computed, onUnmounted} from 'vue'


// track the post-"done" delay to avoid races/unmounted updates
let exportDoneTimer: ReturnType<typeof window.setTimeout> | null = null

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
    const hint = `Allowed order n of a finite plane: ${allowedNText.value}.`
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

// Lightweight global banner (errors/info)
type Banner = { kind: 'error' | 'info', message: string }
const banner = ref<Banner | null>(null)
let bannerTimer: number | null = null

function showErrorBanner(message: string, autoHideMs = 6000) {
  banner.value = {kind: 'error', message}
  if (bannerTimer) {
    window.clearTimeout(bannerTimer)
    bannerTimer = null
  }
  bannerTimer = window.setTimeout(() => {
    banner.value = null
    bannerTimer = null
  }, autoHideMs)
}

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
  // clear any pending "done" timeout from a previous export
  if (exportDoneTimer) {
    window.clearTimeout(exportDoneTimer)
    exportDoneTimer = null
  }

  exporting.value = true
  exportPhase.value = null
  exportPercent.value = null
  exportError.value = null

  // Guard required inputs instead of using non-null assertions
  if (!n.value || !symbolsPerCard.value || !totalSymbols.value || !Array.isArray(cards.value) || cards.value.length === 0) {
    exportError.value = 'Missing required values. Validate and generate cards first.'
    showErrorBanner(exportError.value)
    exporting.value = false
    return
  }

  const defs = buildSymbolDefs(notation.value, totalSymbols.value, selectedSymbols.value)

  // If using symbol images, ensure selection count matches and cards reference only known ids
  if (notation.value === 's') {
    if (selectedSymbols.value.length !== totalSymbols.value) {
      exportError.value = `Pick exactly ${totalSymbols.value} symbols before exporting.`
      showErrorBanner(exportError.value)
      exporting.value = false
      return
    }
    const idSet = new Set(defs.map(d => d.id))
    const unknown = cards.value.flat().find(id => !idSet.has(id))
    if (unknown) {
      exportError.value = `A card references a symbol that wasn't provided. Please regenerate and try again.`
      showErrorBanner(exportError.value)
      exporting.value = false
      return
    }
  }

  try {
    await exportPdf({
      n: n.value,
      symbolsPerCard: symbolsPerCard.value,
      numCards: totalSymbols.value,
      cards: cards.value,
      symbolDefs: defs,
      onProgress: ({phase, percent}) => {
        // ensure "processing" appears between upload and download (handled inside exportPdf),
        // here we just reflect the reported state
        exportPhase.value = phase
        exportPercent.value = percent ?? null
      }
    })
  } catch (e: any) {
    exportError.value = e?.message || 'Export failed'
    showErrorBanner(exportError.value ?? 'Export failed')
  } finally {
    // Keep the banner briefly on "done" for UX, then hide
    if (exportPhase.value === 'done' && !exportError.value) {
      exportDoneTimer = window.setTimeout(() => {
        exporting.value = false
        exportDoneTimer = null
      }, 600)
    } else {
      exporting.value = false
    }
  }
}

onUnmounted(() => {
  if (exportDoneTimer) {
    window.clearTimeout(exportDoneTimer)
    exportDoneTimer = null
  }
})
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

  <!-- Error/info banner (upload or export issues) -->
  <transition name="fade">
    <div
      v-if="banner"
      :class="['fixed left-0 right-0 z-50 flex items-start gap-3 px-4 py-2 shadow-md', exporting ? 'top-12' : 'top-0', banner.kind === 'error' ? 'bg-red-600 text-white' : 'bg-blue-600 text-white']"
      role="alert"
      aria-live="assertive"
    >
      <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" class="min-w-[22px]">
        <circle cx="12" cy="12" r="10" fill="currentColor" opacity=".15"/>
        <path d="M12 7v7m0 3h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"
              fill="none"/>
      </svg>
      <div class="flex-1">
        <div class="font-semibold">
          {{ banner.kind === 'error' ? 'Something went wrong' : 'Notice' }}
        </div>
        <p class="text-sm opacity-95">
          {{ banner.message }}
        </p>
      </div>
      <button
        type="button"
        class="ml-2 px-3 py-1 rounded bg-white/10 hover:bg-white/20"
        @click="banner = null"
        aria-label="Dismiss message"
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
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor"
                   class="bi bi-123" viewBox="0 0 16 16">
                <path
                  d="M2.873 11.297V4.142H1.699L0 5.379v1.137l1.64-1.18h.06v5.961zm3.213-5.09v-.063c0-.618.44-1.169 1.196-1.169.676 0 1.174.44 1.174 1.106 0 .624-.42 1.101-.807 1.526L4.99 10.553v.744h4.78v-.99H6.643v-.069L8.41 8.252c.65-.724 1.237-1.332 1.237-2.27C9.646 4.849 8.723 4 7.308 4c-1.573 0-2.36 1.064-2.36 2.15v.057zm6.559 1.883h.786c.823 0 1.374.481 1.379 1.179.01.707-.55 1.216-1.421 1.21-.77-.005-1.326-.419-1.379-.953h-1.095c.042 1.053.938 1.918 2.464 1.918 1.478 0 2.642-.839 2.62-2.144-.02-1.143-.922-1.651-1.551-1.714v-.063c.535-.09 1.347-.66 1.326-1.678-.026-1.053-.933-1.855-2.359-1.845-1.5.005-2.317.88-2.348 1.898h1.116c.032-.498.498-.944 1.206-.944.703 0 1.206.435 1.206 1.07.005.64-.504 1.106-1.2 1.106h-.75z"/>
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
              <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="currentColor"
                   class="bi bi-alphabet" viewBox="0 0 16 16">
                <path
                  d="M2.204 11.078c.767 0 1.201-.356 1.406-.737h.059V11h1.216V7.519c0-1.314-.947-1.783-2.11-1.783C1.355 5.736.75 6.42.69 7.27h1.216c.064-.323.313-.552.84-.552s.864.249.864.771v.464H2.346C1.145 7.953.5 8.568.5 9.496c0 .977.693 1.582 1.704 1.582m.42-.947c-.44 0-.845-.235-.845-.718 0-.395.269-.684.84-.684h.991v.538c0 .503-.444.864-.986.864m5.593.937c1.216 0 1.948-.869 1.948-2.31v-.702c0-1.44-.727-2.305-1.929-2.305-.742 0-1.328.347-1.499.889h-.063V3.983h-1.29V11h1.27v-.791h.064c.21.532.776.86 1.499.86Zm-.43-1.025c-.66 0-1.113-.518-1.113-1.28V8.12c0-.825.42-1.343 1.098-1.343.684 0 1.075.518 1.075 1.416v.45c0 .888-.386 1.401-1.06 1.401Zm2.834-1.328c0 1.47.87 2.378 2.305 2.378 1.416 0 2.139-.777 2.158-1.763h-1.186c-.06.425-.313.732-.933.732-.66 0-1.05-.512-1.05-1.352v-.625c0-.81.371-1.328 1.045-1.328.635 0 .879.425.918.776h1.187c-.02-.986-.787-1.806-2.14-1.806-1.41 0-2.304.918-2.304 2.338z"/>
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

  <!-- Validation row (separate, responsive) -->
  <div class="mt-2 w-full">
    <!-- Loading -->
    <div v-if="loading"
         class="status text-Auburn items-start gap-2 rounded-[12px] text-sm px-3 py-2 bg-Vanilla/70 border border-[color:var(--color-Auburn)] md:max-w-3xl">
      Checking…
    </div>

    <!-- Result -->
    <div
      v-else-if="hasValidation"
      class="inline-flex items-start gap-2 rounded-[12px] px-3 py-2 bg-Vanilla/70 border border-[color:var(--color-Auburn)] md:max-w-3xl"
      role="status"
      aria-live="polite"
      :title="validationTitle"
    >
      <!-- Valid -->
      <svg v-if="valid" viewBox="0 0 24 24" width="24" height="24" class="min-w-6 text-green-700"
           role="img" aria-label="Valid">
        <circle cx="12" cy="12" r="10" class="fill-green-100 stroke-green-600" stroke-width="1.5"/>
        <path d="M7 12.5l3 3 7-7" class="stroke-green-700" fill="none" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <!-- Invalid -->
      <svg v-else viewBox="0 0 24 24" width="24" height="24" class="min-w-6 text-red-700" role="img"
           aria-label="Invalid">
        <circle cx="12" cy="12" r="10" class="fill-red-100 stroke-red-600" stroke-width="1.5"/>
        <path d="M8.5 8.5l7 7M15.5 8.5l-7 7" class="stroke-red-700" fill="none" stroke-width="2"
              stroke-linecap="round"/>
      </svg>

      <span
        class="text-sm leading-6"
        :class="valid ? 'text-green-800' : 'text-red-800'"
      >
        {{ validationMessage }}
      </span>
    </div>
  </div>

  <!-- show picker for symbols mode -->
  <div v-if="valid && notation === 's' && !cards.length" class="panel mt-4">
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
  border-radius: 12px;
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
  border: 2px solid var(--color-Auburn);
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
