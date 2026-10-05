<template>
  <header class="w-full max-w-xl mx-auto flex items-center justify-between py-4 px-4 border-b border-surface-border">
    <div class="flex items-center gap-2">
      <div class="w-7 h-7 rounded-lg bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center font-bold text-emerald-400 text-sm">
        K
      </div>
      <div>
        <h1 class="text-lg font-bold tracking-tight text-white flex items-center gap-2">
          KONTEKS
          <span class="text-xs px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-mono font-medium border border-emerald-500/20">
            ID
          </span>
        </h1>
      </div>
    </div>

    <div class="flex items-center gap-2">
      <!-- New Game Button -->
      <button 
        @click="$emit('new-game')"
        class="px-2.5 py-1.5 text-xs font-semibold text-gray-300 hover:text-white bg-surface-card hover:bg-surface-border rounded-lg transition-colors border border-surface-border flex items-center gap-1.5"
        title="Main Game Baru (Kata Acak)"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        <span>Game Baru</span>
      </button>

      <button 
        @click="$emit('open-help')"
        class="p-2 text-gray-400 hover:text-white hover:bg-surface-card rounded-lg transition-colors border border-transparent hover:border-surface-border"
        title="Cara Bermain"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </button>

      <button 
        v-if="isSolved"
        @click="$emit('open-solved')"
        class="p-2 text-emerald-400 hover:bg-emerald-500/10 rounded-lg transition-colors border border-emerald-500/30"
        title="Hasil Permainan"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
        </svg>
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
defineProps<{
  isSolved?: boolean;
}>();

defineEmits<{
  (e: 'open-help'): void;
  (e: 'open-solved'): void;
  (e: 'new-game'): void;
}>();
</script>
