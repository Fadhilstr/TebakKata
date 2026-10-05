<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm">
    <div class="w-full max-w-md bg-[#16181f] border border-emerald-500/30 rounded-2xl p-6 text-center shadow-2xl relative animate-in fade-in zoom-in-95 duration-200">
      
      <!-- Close button -->
      <button 
        @click="$emit('close')"
        class="absolute top-4 right-4 p-1.5 text-gray-400 hover:text-white rounded-lg transition-colors"
      >
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      <div class="w-14 h-14 mx-auto rounded-2xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 mb-4 shadow-lg shadow-emerald-500/10">
        <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>

      <h2 class="text-xl font-bold text-white tracking-tight mb-1">
        Luar Biasa!
      </h2>
      <p class="text-sm text-gray-400 mb-5">
        Anda berhasil memecahkan teka-teki Konteks hari ini!
      </p>

      <!-- Secret Word Display -->
      <div class="p-4 rounded-xl bg-emerald-950/40 border border-emerald-500/40 mb-5">
        <div class="text-xs uppercase tracking-wider text-emerald-400 font-semibold mb-1">
          Kata Rahasia
        </div>
        <div class="text-2xl font-extrabold text-white capitalize tracking-wide font-mono">
          {{ secretWord }}
        </div>
      </div>

      <!-- Stats Grid -->
      <div class="grid grid-cols-2 gap-3 mb-6">
        <div class="p-3 rounded-xl bg-surface-card border border-surface-border">
          <div class="text-xs text-gray-400">Total Percobaan</div>
          <div class="text-xl font-bold text-white font-mono mt-0.5">{{ totalGuesses }}</div>
        </div>
        <div class="p-3 rounded-xl bg-surface-card border border-surface-border">
          <div class="text-xs text-gray-400">Peringkat Akhir</div>
          <div class="text-xl font-bold text-emerald-400 font-mono mt-0.5">#1</div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex flex-col gap-2">
        <button
          @click="copyShareResult"
          class="w-full py-3 bg-emerald-600 hover:bg-emerald-500 active:scale-[0.98] text-white font-bold rounded-xl transition-all shadow-md flex items-center justify-center gap-2"
        >
          <svg v-if="copied" class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
          </svg>
          <span>{{ copied ? 'Tersalin ke Clipboard!' : 'Bagikan Hasil' }}</span>
        </button>

        <!-- Play New Game -->
        <button
          @click="$emit('play-random')"
          class="w-full py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 active:scale-[0.98] text-white font-bold rounded-xl transition-all shadow-md flex items-center justify-center gap-2"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span>Mainkan Kata Acak Baru</span>
        </button>

        <!-- Replay Today -->
        <button
          @click="$emit('reset-game')"
          class="w-full py-2.5 bg-surface-card hover:bg-surface-border text-gray-300 hover:text-white font-medium text-sm rounded-xl transition-colors border border-surface-border"
        >
          Ulangi Teka-teki Hari Ini
        </button>

        <button
          @click="$emit('close')"
          class="w-full py-2 bg-transparent hover:bg-white/5 text-gray-400 hover:text-white font-medium text-xs rounded-xl transition-colors"
        >
          Tutup
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps<{
  secretWord: string;
  totalGuesses: number;
  gameDate?: string;
}>();

defineEmits<{
  (e: 'close'): void;
  (e: 'play-random'): void;
  (e: 'reset-game'): void;
}>();

const copied = ref(false);

const copyShareResult = async () => {
  const text = `Konteks Indonesia 🇮🇩\nSaya menemukan kata rahasia dalam ${props.totalGuesses} percobaan!\nPeringkat: 🟩 #1\nMainkan: ${window.location.origin}`;
  try {
    await navigator.clipboard.writeText(text);
    copied.value = true;
    setTimeout(() => {
      copied.value = false;
    }, 2500);
  } catch (err) {
    console.error('Failed to copy', err);
  }
};
</script>
