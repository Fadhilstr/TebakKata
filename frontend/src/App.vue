<template>
  <div class="min-h-screen bg-[#0f1117] text-[#e6e8ee] flex flex-col">
    <!-- Header -->
    <Header
      :is-solved="isSolved"
      @open-help="showHelpModal = true"
      @open-solved="showSolvedModal = true"
      @new-game="playRandomGame"
    />

    <!-- Main Content -->
    <main class="flex-1 w-full max-w-xl mx-auto px-4 py-6 flex flex-col">
      <!-- Loading State -->
      <div v-if="isLoading" class="flex-1 flex flex-col items-center justify-center py-20 text-gray-400 gap-3">
        <div class="w-8 h-8 border-2 border-emerald-500/20 border-t-emerald-500 rounded-full animate-spin"></div>
        <span class="text-sm font-medium">Memuat kata rahasia...</span>
      </div>

      <!-- Main Game Flow -->
      <div v-else class="flex-1 flex flex-col">
        <!-- Hero / Instructions -->
        <div class="text-center mb-2">
          <p class="text-sm text-gray-400">
            Ketik kata apa saja untuk melihat seberapa dekat maknanya dengan kata rahasia.
          </p>
        </div>

        <!-- Input Component (Never locked out, user can test any word) -->
        <GuessInput
          :disabled="false"
          :is-submitting="isSubmitting"
          :error-message="errorMessage"
          :duplicate-notice="duplicateNotice"
          @submit="submitGuess"
        />

        <!-- Game Solved Banner with Replay Options -->
        <div 
          v-if="isSolved"
          class="mt-6 p-4 rounded-xl bg-emerald-950/40 border border-emerald-500/40 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 animate-in fade-in duration-300"
        >
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-emerald-500/20 flex items-center justify-center text-emerald-400 font-bold shrink-0">
              ✓
            </div>
            <div>
              <div class="text-xs font-semibold text-emerald-400 uppercase tracking-wider">Teka-teki Terpecahkan!</div>
              <div class="text-sm text-white font-medium">
                Kata rahasia: <span class="font-bold capitalize font-mono text-emerald-300">{{ secretWord }}</span>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <button
              @click="playRandomGame"
              class="px-3 py-1.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-bold rounded-lg transition-all shadow-sm flex items-center gap-1.5"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <span>Main Game Acak</span>
            </button>

            <button
              @click="resetGame"
              class="px-2.5 py-1.5 bg-surface-card hover:bg-surface-border text-gray-300 hover:text-white text-xs font-medium rounded-lg transition-colors border border-surface-border"
            >
              Ulangi
            </button>

            <button
              @click="showSolvedModal = true"
              class="px-2.5 py-1.5 bg-surface-card hover:bg-surface-border text-gray-300 hover:text-white text-xs font-medium rounded-lg transition-colors border border-surface-border"
            >
              Statistik
            </button>
          </div>
        </div>

        <!-- Progress Sub-bar & Sort Toggle -->
        <div v-if="guesses.length > 0" class="mt-8 mb-4 flex items-center justify-between text-xs text-gray-400 border-b border-surface-border pb-3">
          <div class="flex items-center gap-3">
            <span>
              Tebakan: <strong class="text-white font-mono">{{ guesses.length }}</strong>
            </span>
            <span v-if="bestRanking" class="flex items-center gap-1">
              Terdekat: <strong class="text-emerald-400 font-mono">#{{ bestRanking.toLocaleString('id-ID') }}</strong>
            </span>
          </div>

          <!-- Sort Filter -->
          <div class="flex items-center bg-surface-card p-0.5 rounded-lg border border-surface-border">
            <button
              @click="sortMode = 'recent'"
              :class="sortMode === 'recent' ? 'bg-surface-border text-white shadow-sm' : 'text-gray-400 hover:text-white'"
              class="px-2.5 py-1 rounded-md transition-all font-medium"
            >
              Terbaru
            </button>
            <button
              @click="sortMode = 'rank'"
              :class="sortMode === 'rank' ? 'bg-surface-border text-white shadow-sm' : 'text-gray-400 hover:text-white'"
              class="px-2.5 py-1 rounded-md transition-all font-medium"
            >
              Terdekat
            </button>
          </div>
        </div>

        <!-- Guess List -->
        <div v-if="displayGuesses.length > 0" class="space-y-2.5 mt-2 mb-8">
          <GuessCard
            v-for="guess in displayGuesses"
            :key="guess.word"
            :guess="guess"
          />
        </div>

        <!-- Empty State -->
        <div 
          v-else-if="!isLoading" 
          class="flex-1 flex flex-col items-center justify-center py-16 text-center text-gray-500"
        >
          <div class="w-12 h-12 rounded-2xl bg-surface-card border border-surface-border flex items-center justify-center text-gray-400 mb-3">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
          <div class="text-sm font-medium text-gray-300 mb-1">Belum Ada Tebakan</div>
          <p class="text-xs max-w-xs text-gray-400">
            Coba masukkan kata awal apa saja, seperti <span class="text-emerald-400 font-mono">air</span>, <span class="text-emerald-400 font-mono">rumah</span>, atau <span class="text-emerald-400 font-mono">hewan</span> untuk memetakan arah.
          </p>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="py-4 text-center text-xs text-gray-400 border-t border-surface-border">
      <p>Konteks Indonesia &copy; 2026 — Ditenagai oleh AI Semantic Similarity</p>
    </footer>

    <!-- Modals -->
    <HelpModal 
      v-if="showHelpModal"
      @close="showHelpModal = false"
    />

    <SolvedModal
      v-if="showSolvedModal && secretWord"
      :secret-word="secretWord"
      :total-guesses="guesses.length"
      :game-date="game?.game_date"
      @play-random="playRandomGame"
      @reset-game="resetGame"
      @close="showSolvedModal = false"
    />
  </div>
</template>

<script setup lang="ts">
import Header from './components/Header.vue';
import GuessInput from './components/GuessInput.vue';
import GuessCard from './components/GuessCard.vue';
import HelpModal from './components/HelpModal.vue';
import SolvedModal from './components/SolvedModal.vue';
import { useGame } from './composables/useGame';

const {
  game,
  guesses,
  displayGuesses,
  isSolved,
  secretWord,
  isLoading,
  isSubmitting,
  errorMessage,
  duplicateNotice,
  sortMode,
  bestRanking,
  showHelpModal,
  showSolvedModal,
  submitGuess,
  playRandomGame,
  resetGame
} = useGame();
</script>
