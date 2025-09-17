import {ref, computed, watch} from 'vue'
import axios from 'axios'

const backendLink = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8000/dobble'

// finite letters set (you said you only allow A..Z)
const LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('')
const VALID_ORDERS = [2, 3, 4, 5, 7, 8, 9, 13]
const feasibleOrders = (max: number) =>
  VALID_ORDERS.filter(n => n * n + n + 1 <= max)

export function userGenerator() {
  // -------- form state --------
  const mode = ref<'n' | 'k' | 'sc'>('n')
  const notation = ref<'n' | 'l' | 's'>('n')
  const howMany = ref<number | null>(null)

  const howManyPlaceholder = computed(() =>
    mode.value === 'n' ? 'n' : mode.value === 'k' ? 'k' : 's/c'
  )
  // reset input so placeholder becomes visible
  watch(mode, () => {
    howMany.value = null
  })

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
    // symbols require exact user selection count
    if (notation.value === 's') return selectedSymbols.value.length === totalSymbols.value
    // numbers/letters are auto-built in generate()
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
      const {data} = await axios.get(`${backendLink}/validate`, {
        params: {mode: mode.value, how_many: howMany.value ?? 0},
      })
      if (!data.valid) {
        error.value = data.message;
        return
      }

      n.value = data.n
      symbolsPerCard.value = data.symbols_per_card
      totalSymbols.value = data.num_cards

      // if letters are finite, ensure we have enough
      if (notation.value === 'l') {
        const need = totalSymbols.value!
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

  // helper: build numbers quickly
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
      // symbols
      if (selectedSymbols.value.length !== totalSymbols.value) return
      payloadSymbols = selectedSymbols.value.slice()
    }

    try {
      const {data} = await axios.post(`${backendLink}/generate`, {
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


// Build `symbols` array for /export/pdf from your notation & selections.
// For numbers/letters, ids are the text itself; for images, ids are the data URL.
export function buildSymbolDefs(notation: 'n' | 'l' | 's', totalSymbols: number, selectedSymbols: string[]) {
  if (notation === 's') {
    // images: data URLs (or file URLs) the user picked
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
        font_weight: 700
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
    font_weight: 700
  }))
}

// Call this from your component to download the PDF.
export async function exportPdf({
                                  n,
                                  symbolsPerCard,
                                  numCards,
                                  cards,
                                  symbolDefs,
                                }: {
  n: number
  symbolsPerCard: number
  numCards: number
  cards: string[][]
  symbolDefs: Array<
    | { id: string; type: 'text'; text: string; font_family?: string; font_weight?: number }
    | { id: string; type: 'image'; src: string }
  >
}) {
  const payload = {
    n,
    symbols_per_card: symbolsPerCard,
    num_cards: numCards,
    cards,
    symbols: symbolDefs,
    page: {size: 'A4', orientation: 'portrait', margin_mm: 10},
    card: {diameter_mm: 80, stroke_mm: 0.4, per_page: 6, cut_marks: true, bleed_mm: 0},
    randomization: {
      seed: null,
      rotation_mode: 'steps90',                 // <- use your new modes: 'any' | 'bounded' | 'steps90' | 'steps'
      rotation_deg: {min: 0, max: 360},       // used by 'any'/'bounded'
      scale: {min: 0.8, max: 1.1},
      angular_jitter_deg: 6,
      radial_jitter_mm: 1.5,
      ring_strategy: 'auto',
    },
    options: {embed_fonts: true, image_dpi: 300, safe_mode: true},
  }

  try {
    // ✅ request the PDF
    const res = await axios.post(`${backendLink}/export/pdf`, payload, {
      responseType: 'blob',
    })

    // ✅ success: download the PDF
    const blob = new Blob([res.data], {type: 'application/pdf'})
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'dobble_cards.pdf'
    a.click()
    URL.revokeObjectURL(url)

  } catch (err: any) {
    // ❌ error: try to read JSON text returned by FastAPI
    const blob = err?.response?.data
    if (blob instanceof Blob) {
      const text = await blob.text()
      console.error("Export PDF failed:", text)
    } else {
      console.error("Export PDF failed:", err)
    }
  }

}
