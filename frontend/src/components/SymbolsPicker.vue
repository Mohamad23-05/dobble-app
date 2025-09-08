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
  <section class="space-y-3">
    <div class="flex items-center justify-between">
      <h3 class="text-xl font-bold">Choose exactly {{ totalSymbols }} symbols</h3>
      <span class="text-sm opacity-75">Selected: {{ selected.length }} / {{ totalSymbols }}</span>
    </div>

    <!-- default palette -->
    <div class="grid grid-cols-[repeat(auto-fill,minmax(72px,1fr))] gap-2">
      <button
        v-for="sym in palette"
        :key="sym"
        type="button"
        @click="toggle(sym)"
        class="border rounded p-2 h-[72px] flex items-center justify-center overflow-hidden"
        :class="selected.includes(sym) ? 'border-yellow-500 bg-yellow-100' : 'border-gray-300 bg-white'"
        :aria-pressed="selected.includes(sym)"
      >
        <img :src="sym" alt="" class="max-h-full max-w-full object-contain"/>
      </button>
    </div>

    <!-- uploads -->
    <div v-if="allowUpload !== false" class="space-y-2">
      <div
        class="border-2 border-dashed rounded-md p-4 text-center cursor-pointer"
        :class="dragOver ? 'border-amber-500 bg-amber-50' : 'border-gray-300'"
        @dragover="onDragOver"
        @dragleave="onDragLeave"
        @drop="onDrop"
      >
        <p class="text-sm opacity-80">Drag & drop images here, or</p>
        <label class="inline-block mt-1 px-3 py-1 rounded bg-gray-100 border cursor-pointer">
          Browse files
          <input type="file" accept="image/*" multiple class="hidden" @change="onUploadFiles"/>
        </label>
      </div>
      <p class="text-xs opacity-60">PNG/JPG/WebP/SVG, up to {{ maxFileSizeMB ?? 2 }} MB each.</p>
    </div>
  </section>
</template>


<style scoped>

</style>
