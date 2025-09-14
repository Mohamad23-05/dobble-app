import {ref, computed, watch} from 'vue'
import axios from 'axios'

const backendLink = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8000'

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
      const {data} = await axios.get(`${backendLink}/dobble/validate`, {
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
      const {data} = await axios.post(`${backendLink}/dobble/generate`, {
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
