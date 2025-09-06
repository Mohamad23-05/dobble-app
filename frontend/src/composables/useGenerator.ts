import {ref, computed, watch} from 'vue';
import axios from 'axios'

const backendLink = "http://127.0.0.1:8000"

export function userGenerator() {
  /** form (always visible) **/
  const mode = ref<"n" | "k" | "sc">("n");
  const notation = ref<"n" | "l" | "s">("n");
  const howMany = ref<number | null>(null);

  // placeholder that reacts to mode
  const howManyPlaceholder = computed(() => {
    return mode.value === 'n' ? 'n' : mode.value === 'k' ? 'k' : 's/c'
  })

  // when mode changes, clear the input so the new placeholder is visible
  watch(mode, () => {
    howMany.value = null
  })


  /** form validate **/
  const n = ref<number | null>(null);
  const symbolsPerCard = ref<number | null>(null);
  const totalSymbols = ref<number | null>(null);
  const valid = ref(false);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const cards = ref<string[][]>([]) // <- store cards from backend

  /** universe that will be sent to the backend **/
  const universe = ref<string[]>([]) // final list

  /** only for notation === 's' **/
  const availableSymbols = ref<string[]>([])
  const selectedSymbols = ref<string[]>([])

  const canGenerate = computed(() => {
    if (!valid.value || !n.value || !totalSymbols.value) return false;
    if (notation.value === "s") return selectedSymbols.value.length === totalSymbols.value;
    return universe.value.length === totalSymbols.value;
  })

  // inside userGenerator()
  const generateCtaText = computed(() => {
    // nice CTA text, shows how many cards we’ll make when we know n
    if (!n.value) return "Generate Cards"
    const k = n.value ** 2 + n.value + 1
    return `Generate ${k} cards`
  })

  const generateDisabledReason = computed(() => {
    if (!valid.value) return "Validate the form first"
    if (!n.value || !totalSymbols.value) return "Missing derived values"
    if (notation.value === "s" && selectedSymbols.value.length !== totalSymbols.value) {
      return `Pick exactly ${totalSymbols.value} symbols`
    }
    if (notation.value !== "s" && universe.value.length !== totalSymbols.value) {
      return "Universe not ready"
    }
    return ""
  })

  // inside userGenerator()

// Choose the exact letters you allow:
  const LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("")        // 26

// (optional) if you want to show which n are possible with this LETTERS size:
  const VALID_ORDERS = [2, 3, 4, 5, 7, 8, 9, 13]

  function feasibleOrders(maxSymbols: number) {
    return VALID_ORDERS.filter(n => n * n + n + 1 <= maxSymbols)
  }


  /** helpers **/
  function indexToLetter(idx: number): string {
    let res = '', x = idx;
    while (x >= 0) {
      res = String.fromCharCode(65 + (x % 26)) + res;
      x = Math.floor(x / 26) - 1;
    }
    return res
  }

  function buildLetter(count: number) {
    return Array.from({length: count}, (_, i) => indexToLetter(i))
  }

  function buildNumbers(count: number) {
    return Array.from({length: count}, (_, i) => String(i))
  }

  const defaultEmojis = ["⭐", "🌙", "🔥", "💧", "🍀", "🎯", "⚡", "🍎", "🚀", "🎵", "🧩",
    "🎈", "🎁", "🪙", "💎", "⚽", "🏀", "🎱", "🧸", "🦄", "🐝", "🐞", "🦋", "🌸", "🌻", "🌈",
    "🚗", "🚲", "🧭", "📚", "✏️", "🔑", "🔧", "🔗", "⌛", "🧪", "🔬", "🧲", "📷", "🎬", "🎮", "🕹️"];


  /** actions **/
  async function validateForm() {
    loading.value = true;
    error.value = null;
    valid.value = false;
    n.value = null;
    symbolsPerCard.value = null;
    totalSymbols.value = null;
    universe.value = [];
    availableSymbols.value = [];
    selectedSymbols.value = [];

    try {
      const {data} = await axios.get(backendLink + "/dobble/validate", {
        params: {mode: mode.value, how_many: howMany.value ?? 0} // ✅ snake_case
      })
      if (!data.valid) {
        error.value = data.message;
        return;
      }

      n.value = data.n;
      symbolsPerCard.value = data.symbols_per_card      // ✅ correct field
      totalSymbols.value = data.num_cards;
      valid.value = true;

      if (notation.value === "n") {
        universe.value = buildNumbers(totalSymbols.value!)
      } else if (notation.value === "l") {
        const need = totalSymbols.value!
        const have = LETTERS.length
        if (need > have) {
          const feasible = feasibleOrders(have) // e.g., [2,3,4] for 26 letters
          valid.value = false
          error.value = `Not enough letters: need ${need}, but only ${have} available. `
            + (feasible.length
              ? `Pick a smaller order (n ∈ { ${feasible.join(", ")} }) or switch to numbers/symbols.`
              : `Decrease n or choose another notation.`)
          return
        }
        // OK: use the first 'need' letters
        universe.value = LETTERS.slice(0, need)
      } else {
        // symbols mode: show picker; user selects exactly totalSymbols items
        // availableSymbols.value = [your PNG URLs repeated to length ...]
      }

    } catch (e: any) {
      error.value = e?.response?.data?.detail || "Validation failed";
      throw e;
    } finally {
      loading.value = false;
    }
  }


  function toggleSymbol(sym: string) {
    const i = selectedSymbols.value.indexOf(sym);
    if (i >= 0) selectedSymbols.value.splice(i, 1);
    else if (selectedSymbols.value.length < (totalSymbols.value ?? 0)) selectedSymbols.value.push(sym);
  }

  //TODO: UploadSymbols


  async function generate() {
    if (!n.value || !totalSymbols.value) return
    let payloadSymbols = universe.value
    if (notation.value === "s") {
      if (selectedSymbols.value.length !== totalSymbols.value) return
      payloadSymbols = selectedSymbols.value.slice()
    }
    try {
      const {data} = await axios.post(backendLink + "/dobble/generate", {
        n: n.value,
        symbols: payloadSymbols,
      })
      cards.value = data.cards // ✅ save response
      return data
    } catch (e: any) {
      error.value = e?.response?.data?.detail || "Generation failed"
      throw e
    }
  }

  return {
    //state
    mode, howMany, notation, howManyPlaceholder,
    n, symbolsPerCard, totalSymbols,
    valid, loading, error,

    //universe / symbols
    cards, universe, availableSymbols, selectedSymbols,

    //computed
    canGenerate, generateCtaText, generateDisabledReason,

    //actions
    validateForm, toggleSymbol, generate
  }
}
