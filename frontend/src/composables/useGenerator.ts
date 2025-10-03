import {ref, computed, watch} from 'vue'
import axios from 'axios'

// Backend base URL: prefer env, fall back to local dev server
const backendBase = import.meta.env.VITE_API_BASE;

// Finite letters set and feasible orders helper
const LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('')
const VALID_ORDERS = [2, 3, 4, 5, 7, 8, 9, 13]
const feasibleOrders = (max: number) =>
  VALID_ORDERS.filter(n => n * n + n + 1 <= max)

// Shared types to keep exports tidy and self-documented
type ExportPhase = 'upload' | 'processing' | 'download' | 'done'
type TextSymbolDef = {
  id: string;
  type: 'text';
  text: string;
  font_family?: string;
  font_weight?: number
}
type ImageSymbolDef = { id: string; type: 'image'; src: string }
type SymbolDef = TextSymbolDef | ImageSymbolDef

export function userGenerator() {
  // -------- form state --------
  const mode = ref<'n' | 'k' | 'sc'>('n')
  const notation = ref<'n' | 'l' | 's'>('n')
  const howMany = ref<number | null>(null)

  const howManyPlaceholder = computed(() =>
    mode.value === 'n' ? 'N' : mode.value === 'k' ? 'C' : 'S/C'
  )

  // Reset current validation/result state (used when inputs change)
  function resetValidationState() {
    error.value = null
    valid.value = false
    n.value = null
    symbolsPerCard.value = null
    totalSymbols.value = null
    // keep already picked symbols and cards if you prefer; otherwise uncomment:
    // cards.value = []
    // selectedSymbols.value = []
  }

  // Reset input so placeholder becomes visible + clear messages/results
  watch(mode, () => {
    howMany.value = null
    resetValidationState()
  })
  watch(howMany, resetValidationState)

  // -------- derived / validation --------
  const n = ref<number | null>(null)
  const symbolsPerCard = ref<number | null>(null)
  const totalSymbols = ref<number | null>(null)
  const valid = ref(false)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // -------- results --------
  const cards = ref<string[][]>([])

  // -------- symbols (symbols mode only) --------
  const selectedSymbols = ref<string[]>([]) // v-model with SymbolsPicker

  // Button state / text
  const canGenerate = computed(() => {
    if (!valid.value || !n.value || !totalSymbols.value) return false
    // images: require exact user selection count
    if (notation.value === 's') return selectedSymbols.value.length === totalSymbols.value
    return true
  })

  const generateCtaText = computed(() => {
    if (!n.value) return 'Generate Cards'
    const k = n.value ** 2 + n.value + 1
    return `Generate ${k} cards`
  })

  const generateDisabledReason = computed(() => {
    if (!valid.value) return 'Validate the form first'
    if (!n.value || !totalSymbols.value) return 'Missing derived values'
    if (notation.value === 's' && selectedSymbols.value.length !== totalSymbols.value) {
      return `Pick exactly ${totalSymbols.value} symbols`
    }
    return ''
  })

  // -------- actions --------
  async function validateForm() {
    loading.value = true
    error.value = null
    valid.value = false
    n.value = null
    symbolsPerCard.value = null
    totalSymbols.value = null
    cards.value = []
    selectedSymbols.value = []

    try {
      const {data} = await axios.get(`${backendBase}/dobble/validate`, {
        params: {mode: mode.value, how_many: howMany.value ?? 0},
      })
      if (!data.valid) {
        error.value = data.message
        return
      }

      n.value = data.n
      symbolsPerCard.value = data.symbols_per_card
      totalSymbols.value = data.num_cards

      // letters mode: ensure we have enough letters for the requested deck size
      if (notation.value === 'l') {
        const need = totalSymbols.value ?? 0
        const have = LETTERS.length
        if (need > have) {
          const feas = feasibleOrders(have)
          error.value =
            `Not enough letters: need ${need}, only ${have} available. ` +
            (feas.length
              ? `Try smaller n (∈ { ${feas.join(', ')} }) or switch notation.`
              : `Decrease n or use numbers/symbols.`)
          return
        }
      }

      valid.value = true
    } catch (e: any) {
      error.value = e?.response?.data?.detail || 'Validation failed'
    } finally {
      loading.value = false
    }
  }

  // Build number labels quickly: "0", "1", ..., count-1
  const buildNumbers = (count: number) =>
    Array.from({length: count}, (_, i) => String(i))

  async function generate() {
    if (!n.value || !totalSymbols.value) return

    // Build payload symbols on the fly based on notation
    let payloadSymbols: string[]
    if (notation.value === 'n') {
      payloadSymbols = buildNumbers(totalSymbols.value)
    } else if (notation.value === 'l') {
      payloadSymbols = LETTERS.slice(0, totalSymbols.value)
    } else {
      // symbols: require exact selection count
      if (selectedSymbols.value.length !== totalSymbols.value) return
      payloadSymbols = selectedSymbols.value.slice()
    }

    try {
      const {data} = await axios.post(`${backendBase}/dobble/generate`, {
        n: n.value,
        symbols: payloadSymbols,
      })
      cards.value = data.cards
      return data
    } catch (e: any) {
      error.value = e?.response?.data?.detail || 'Generation failed'
      throw e
    }
  }

  return {
    // state
    mode, notation, howMany, howManyPlaceholder,
    n, symbolsPerCard, totalSymbols,
    valid, loading, error,

    // results & selection
    cards, selectedSymbols,

    // computed
    canGenerate, generateCtaText, generateDisabledReason,

    // actions
    validateForm, generate,
  }
}

// Build `symbols` array for /export/pdf from notation & selections.
// For numbers/letters, ids are the text itself; for images, ids are the image src (often data URL).
export function buildSymbolDefs(
  notation: 'n' | 'l' | 's',
  totalSymbols: number,
  selectedSymbols: string[]
): SymbolDef[] {
  if (notation === 's') {
    // images: de-duplicate and cap to totalSymbols
    const uniq = Array.from(new Set(selectedSymbols.slice(0, totalSymbols)))
    return uniq.map(src => ({id: src, type: 'image' as const, src}))
  }
  if (notation === 'n') {
    return Array.from({length: totalSymbols}, (_, i) => {
      const t = String(i)
      return {
        id: t,
        type: 'text' as const,
        text: t,
        font_family: 'Helvetica-Bold',
        font_weight: 700,
      }
    })
  }
  // 'l'
  const letters = LETTERS.slice(0, totalSymbols)
  return letters.map(t => ({
    id: t,
    type: 'text' as const,
    text: t,
    font_family: 'Helvetica-Bold',
    font_weight: 700,
  }))
}

// Download the generated PDF. Reports progress via onProgress callback.
export async function exportPdf({
                                  n,
                                  symbolsPerCard,
                                  numCards,
                                  cards,
                                  symbolDefs,
                                  onProgress,
                                }: {
  n: number
  symbolsPerCard: number
  numCards: number
  cards: string[][]
  symbolDefs: SymbolDef[]
  onProgress?: (info: { phase: ExportPhase; percent?: number }) => void
}) {
  // Convert any non-data image src -> data URL, but keep ids as-is
  const {urlToDataUrl} = await import('@/composables/dataUrl')
  const symbolsForApi = await Promise.all(
    symbolDefs.map(async s => {
      if (s.type !== 'image') return s
      if (s.src.startsWith('data:')) return s
      // Resolve to absolute URL (helps when src starts with /src/... in dev)
      const absolute = new URL(s.src, window.location.origin).toString()
      const dataSrc = await urlToDataUrl(absolute)
      return {...s, src: dataSrc}
    })
  )

  const payload = {
    n,
    symbols_per_card: symbolsPerCard,
    num_cards: numCards,
    cards,
    symbols: symbolsForApi,
    page: {size: 'A4', orientation: 'portrait', margin_mm: 10},
    card: {diameter_mm: 110, stroke_mm: 0.4, per_page: 2, cut_marks: true, bleed_mm: 0},
    randomization: {
      seed: null,
      rotation_mode: 'bounded',
      rotation_deg: {min: 0, max: 360},
      scale: {min: 0.5, max: 1.2},
      angular_jitter_deg: 3,
      radial_jitter_mm: 2.5,
      ring_strategy: 'single',
    },
    options: {embed_fonts: true, image_dpi: 300, safe_mode: true},
  }

  try {
    onProgress?.({phase: 'upload', percent: 0})

    let uploadComplete = false
    let emittedProcessing = false
    let downloadStarted = false

    const res = await axios.post(`${backendBase}/dobble/export/pdf`, payload, {
      responseType: 'blob',
      onUploadProgress: e => {
        // Some browsers don't provide total; still report phase
        if (!e.total) {
          onProgress?.({phase: 'upload'})
          return
        }
        const pct = Math.round((e.loaded / e.total) * 100)
        onProgress?.({phase: 'upload', percent: pct})

        if (pct >= 100) {
          uploadComplete = true
          if (!emittedProcessing) {
            onProgress?.({phase: 'processing'})
            emittedProcessing = true
          }
        }
      },
      onDownloadProgress: e => {
        if (!downloadStarted) {
          downloadStarted = true
          // If we never got a 100% upload event, still show processing once before download
          if (!emittedProcessing) {
            onProgress?.({phase: 'processing'})
            emittedProcessing = true
          }
        }
        if (!e.total) {
          onProgress?.({phase: 'download'})
          return
        }
        onProgress?.({
          phase: 'download',
          percent: Math.round((e.loaded / e.total) * 100),
        })
      },
    })

    // Small responses may skip download progress entirely: still show processing once
    if (uploadComplete && !downloadStarted && !emittedProcessing) {
      onProgress?.({phase: 'processing'})
      emittedProcessing = true
    }

    const blob = new Blob([res.data], {type: 'application/pdf'})
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'dobble_cards.pdf'
    a.click()
    window.setTimeout(() => URL.revokeObjectURL(url), 0)

    onProgress?.({phase: 'done', percent: 100})
  } catch (err: any) {
    const blob = err?.response?.data
    if (blob instanceof Blob) {
      const text = await blob.text()
      console.error('Export PDF failed:', text)
    } else {
      console.error('Export PDF failed:', err)
    }
    throw err
  }
}
