<template>
  <div class="w-full max-w-xl mx-auto px-4 mt-6">
    <form @submit.prevent="handleSubmit" class="relative flex items-center">
      <input
        ref="inputRef"
        v-model="word"
        type="text"
        placeholder="Ketik kata bahasa Indonesia..."
        :disabled="disabled"
        autocomplete="off"
        autocorrect="off"
        autocapitalize="none"
        spellcheck="false"
        class="w-full bg-surface-card border border-surface-border text-white text-base font-medium rounded-xl px-4 py-3.5 pr-28 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all placeholder:text-gray-500 disabled:opacity-50"
      />
      <button
        type="submit"
        :disabled="disabled || isSubmitting || !word.trim()"
        class="absolute right-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:bg-gray-800 disabled:text-gray-500 text-white font-semibold text-sm rounded-lg transition-all flex items-center gap-1.5 shadow-sm active:scale-95 disabled:pointer-events-none"
      >
        <span v-if="isSubmitting" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
        <span>{{ isSubmitting ? 'Mengecek...' : 'Tebak' }}</span>
      </button>
    </form>

    <!-- Error / Alert Banners -->
    <div v-if="errorMessage" class="mt-3 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-xs flex items-center gap-2 animate-in fade-in duration-200">
      <svg class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
      <span>{{ errorMessage }}</span>
    </div>

    <div v-if="duplicateNotice" class="mt-3 p-3 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs flex items-center gap-2 animate-in fade-in duration-200">
      <svg class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span>{{ duplicateNotice }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue';

const props = defineProps<{
  disabled?: boolean;
  isSubmitting?: boolean;
  errorMessage?: string | null;
  duplicateNotice?: string | null;
}>();

const emit = defineEmits<{
  (e: 'submit', word: string): void;
}>();

const word = ref('');
const inputRef = ref<HTMLInputElement | null>(null);

const handleSubmit = () => {
  const clean = word.value.trim();
  if (clean && !props.isSubmitting && !props.disabled) {
    emit('submit', clean);
    word.value = '';
    // Retain focus immediately
    inputRef.value?.focus();
  }
};

// Ensure input never loses focus when submitting state toggles
watch(() => props.isSubmitting, (submitting) => {
  if (!submitting && !props.disabled) {
    nextTick(() => {
      inputRef.value?.focus();
    });
  }
});

onMounted(() => {
  inputRef.value?.focus();
});
</script>
