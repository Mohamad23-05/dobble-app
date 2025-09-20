<!-- src/components/SymbolsPicker.vue -->
<script setup lang="ts">
import {computed, ref} from 'vue'

type SymbolItem = string // URL (PNG) or data URL from uploads

const props = defineProps<{
  totalSymbols: number
  defaultSymbols: SymbolItem[]
  modelValue: SymbolItem[]
  allowUpload?: boolean
  maxFileSizeMB?: number
}>()

const emit = defineEmits<{ 'update:modelValue': [SymbolItem[]]; error: [string] }>()

const selected = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v)
})

const palette = computed<string[]>(() => {
  // unique list; no repetition
  return Array.from(new Set(props.defaultSymbols))
})


function toggle(sym: SymbolItem) {
  const i = selected.value.indexOf(sym)
  if (i >= 0) selected.value = [...selected.value.slice(0, i), ...selected.value.slice(i + 1)]
  else if (selected.value.length < props.totalSymbols) selected.value = [...selected.value, sym]
}

const dragOver = ref(false)

async function onUploadFiles(e: Event) {
  const files = (e.target as HTMLInputElement).files
  if (!files) return
  await handleFiles(Array.from(files))
  ;(e.target as HTMLInputElement).value = ''
}

async function onDrop(ev: DragEvent) {
  ev.preventDefault();
  dragOver.value = false
  if (!ev.dataTransfer) return
  await handleFiles(Array.from(ev.dataTransfer.files || []))
}

function onDragOver(ev: DragEvent) {
  ev.preventDefault();
  dragOver.value = true
}

function onDragLeave() {
  dragOver.value = false
}

async function handleFiles(files: File[]) {
  const maxBytes = (props.maxFileSizeMB ?? 2) * 1024 * 1024
  for (const f of files) {
    const ok = /^image\/(png|jpeg|webp|svg\+xml)$/.test(f.type)
    if (!ok) {
      emit('error', `Unsupported file: ${f.name}`);
      continue
    }
    if (f.size > maxBytes) {
      emit('error', `Too large: ${f.name}`);
      continue
    }
    const dataUrl = await toDataURL(f)
    if (!selected.value.includes(dataUrl) && selected.value.length < props.totalSymbols) {
      selected.value = [...selected.value, dataUrl]
    }
  }
}

function toDataURL(f: File) {
  return new Promise<string>((resolve, reject) => {
    const r = new FileReader()
    r.onload = () => resolve(String(r.result))
    r.onerror = reject
    r.readAsDataURL(f)
  })
}
</script>


<template>
  <section class="w-full px-4 py-5">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h3 class="text-xl font-bold">Choose exactly {{ totalSymbols }} symbols</h3>
      <span class="text-sm opacity-75">Selected: {{ selected.length }} / {{ totalSymbols }}</span>
    </div>

    <!-- Two-column layout -->
    <div class="grid grid-cols-1 md:grid-cols-[1fr_auto_1fr] md:items-start gap-4">
      <!-- LEFT: default palette -->
      <div>
        <h4 class="mb-2 font-semibold opacity-80">From site symbols</h4>
        <div class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-9 gap-3">
          <button
            v-for="sym in palette"
            :key="sym"
            type="button"
            @click="toggle(sym)"
            class="border rounded p-2 h-[90px] flex items-center justify-center overflow-hidden transition"
            :class="selected.includes(sym) ? 'border-yellow-500 bg-yellow-100' : 'border-gray-300 bg-white hover:border-gray-400'"
            :aria-pressed="selected.includes(sym)"
          >
            <img :src="sym" alt="" class="max-h-full max-w-full object-contain"/>
          </button>
        </div>
      </div>


      <!-- VERTICAL DIVIDER -->
      <div class="hidden md:block h-full mx-2 border-l border-Vanilla"></div>

      <!-- RIGHT: uploads -->
      <div v-if="allowUpload !== false">
        <h4 class="mb-2 font-semibold opacity-80">Upload your own</h4>

        <!-- Upload box -->
        <div
          class="border-2 border-dashed rounded-md p-6 text-center cursor-pointer transition"
          :class="dragOver ? 'border-amber-500 bg-amber-50' : 'border-white/40 hover:border-white/60'"
          @dragover="onDragOver"
          @dragleave="onDragLeave"
          @drop="onDrop"
        >
          <p class="text-sm opacity-80">Drag & drop images here, or</p>
          <label
            class="inline-block mt-2 px-3 py-1 rounded bg-gray-100 border text-DarkSlateGray cursor-pointer"
          >
            Browse files
            <input type="file" accept="image/*" multiple class="hidden" @change="onUploadFiles"/>
          </label>
          <p class="mt-2 text-xs opacity-60">
            PNG/JPG/WebP, up to {{ maxFileSizeMB ?? 2 }} MB each.
          </p>
        </div>

        <!-- Preview of uploaded images -->
        <div v-if="selected.length" class="mt-4">
          <h5 class="mb-2 text-sm font-medium opacity-80">Uploaded images</h5>
          <div class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3">
            <div
              v-for="(sym, i) in selected"
              :key="i"
              class="relative border rounded overflow-hidden group"
            >
              <img
                :src="sym"
                alt=""
                class="w-full h-24 object-contain py-2 bg-gray-100"
              />
              <!-- Delete button -->
              <button
                type="button"
                @click="selected.splice(i, 1)"
                class="absolute top-1 right-1 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center
                  shadow-md hover:bg-red-600 transition-opacity opacity-0 group-hover:opacity-100 text-xs"
                title="Remove"
              >
                ✕
              </button>

            </div>
          </div>
        </div>

      </div>

    </div>
  </section>
</template>


<style scoped>

</style>
