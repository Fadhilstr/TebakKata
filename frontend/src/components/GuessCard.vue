<template>
  <div 
    class="relative overflow-hidden rounded-xl border transition-all duration-300 group"
    :class="cardBorderClass"
  >
    <!-- Background Proximity Bar -->
    <div 
      class="absolute top-0 bottom-0 left-0 transition-all duration-700 ease-out opacity-25"
      :class="barBgClass"
      :style="{ width: `${progressPercent}%` }"
    ></div>

    <!-- Card Content -->
    <div class="relative z-10 px-4 py-3 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <span class="text-base font-semibold tracking-wide text-white capitalize">
          {{ guess.word }}
        </span>
        <!-- Milestone pill (only shown for meaningful proximity, avoiding negative/confusing labels) -->
        <span 
          v-if="statusLabel"
          class="text-[11px] font-medium px-2.5 py-0.5 rounded-full border transition-all"
          :class="pillClass"
        >
          {{ statusLabel }}
        </span>
      </div>

      <div class="flex items-center gap-3">
        <!-- Ranking Number -->
        <span 
          class="font-mono font-bold text-base tracking-tight"
          :class="rankTextClass"
        >
          #{{ guess.ranking.toLocaleString('id-ID') }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { Guess } from '../types/game';

const props = defineProps<{
  guess: Guess;
}>();

const progressPercent = computed(() => {
  const r = props.guess.ranking;
  if (r === 1) return 100;
  if (r <= 10) return 96 - (r * 1.2);
  if (r <= 50) return 85 - ((r - 10) * 0.35);
  if (r <= 300) return 70 - ((r - 50) * 0.08);
  if (r <= 1000) return 50 - ((r - 300) * 0.025);
  if (r <= 3000) return 30 - ((r - 1000) * 0.007);
  return Math.max(8, 16 - ((r - 3000) * 0.001));
});

// Avoid negative/demoralizing labels like "Jauh" or "Cukup Jauh"
const statusLabel = computed(() => {
  const r = props.guess.ranking;
  if (r === 1) return 'Kata Rahasia!';
  if (r <= 30) return 'Hampir Benar';
  if (r <= 300) return 'Sangat Dekat';
  if (r <= 1500) return 'Mendekat';
  return null; // Clean display without negative "Jauh" badges
});

const cardBorderClass = computed(() => {
  const r = props.guess.ranking;
  if (r === 1) return 'border-emerald-500 bg-emerald-950/40 shadow-lg shadow-emerald-500/20';
  if (r <= 30) return 'border-emerald-500/60 bg-surface-card hover:border-emerald-400';
  if (r <= 300) return 'border-teal-500/40 bg-surface-card hover:border-teal-400';
  if (r <= 1500) return 'border-amber-500/30 bg-surface-card hover:border-amber-400';
  return 'border-surface-border bg-surface-card/60 hover:border-gray-600';
});

const barBgClass = computed(() => {
  const r = props.guess.ranking;
  if (r === 1) return 'bg-emerald-400 opacity-40';
  if (r <= 30) return 'bg-emerald-500';
  if (r <= 300) return 'bg-teal-500';
  if (r <= 1500) return 'bg-amber-500';
  return 'bg-gray-600';
});

const pillClass = computed(() => {
  const r = props.guess.ranking;
  if (r === 1) return 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300 font-semibold';
  if (r <= 30) return 'bg-emerald-500/15 border-emerald-500/30 text-emerald-400 font-medium';
  if (r <= 300) return 'bg-teal-500/15 border-teal-500/30 text-teal-400 font-medium';
  if (r <= 1500) return 'bg-amber-500/15 border-amber-500/30 text-amber-400 font-medium';
  return 'bg-gray-800/80 border-gray-700 text-gray-400';
});

const rankTextClass = computed(() => {
  const r = props.guess.ranking;
  if (r === 1) return 'text-emerald-300 font-extrabold text-lg';
  if (r <= 30) return 'text-emerald-400';
  if (r <= 300) return 'text-teal-400';
  if (r <= 1500) return 'text-amber-400';
  return 'text-gray-400';
});
</script>
