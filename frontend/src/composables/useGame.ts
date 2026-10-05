import { ref, computed, onMounted } from 'vue';
import type { TodayGame, Guess } from '../types/game';
import { fetchTodayGame, fetchRandomGame, postGuess, fetchGameHistory } from '../services/api';
import confetti from 'canvas-confetti';

export function useGame() {
  const game = ref<TodayGame | null>(null);
  const guesses = ref<Guess[]>([]);
  const isSolved = ref(false);
  const secretWord = ref<string | null>(null);
  const isLoading = ref(true);
  const isSubmitting = ref(false);
  const errorMessage = ref<string | null>(null);
  const duplicateNotice = ref<string | null>(null);
  const sortMode = ref<'recent' | 'rank'>('recent');
  const showHelpModal = ref(false);
  const showSolvedModal = ref(false);

  // Persistent Session ID
  const sessionId = computed(() => {
    let sid = localStorage.getItem('konteks_session_id');
    if (!sid) {
      sid = 'usr_' + Math.random().toString(36).substring(2, 15) + Date.now().toString(36);
      localStorage.setItem('konteks_session_id', sid);
    }
    return sid;
  });

  // Best ranking achieved
  const bestRanking = computed(() => {
    if (guesses.value.length === 0) return null;
    return Math.min(...guesses.value.map(g => g.ranking));
  });

  // Display sorted guesses
  const displayGuesses = computed(() => {
    const list = [...guesses.value];
    if (sortMode.value === 'rank') {
      return list.sort((a, b) => a.ranking - b.ranking);
    }
    // 'recent': most recent first
    return list;
  });

  const loadGame = async () => {
    isLoading.value = true;
    errorMessage.value = null;
    try {
      const today = await fetchTodayGame();
      game.value = today;

      // Load history from backend
      try {
        const history = await fetchGameHistory(today.game_id, sessionId.value);
        if (history.guesses && history.guesses.length > 0) {
          guesses.value = history.guesses;
        }
        if (history.is_solved) {
          isSolved.value = true;
          secretWord.value = history.secret_word;
        }
      } catch (e) {
        // Fallback to local storage if history sync fails
        const saved = localStorage.getItem(`konteks_guesses_${today.game_id}`);
        if (saved) {
          try {
            guesses.value = JSON.parse(saved);
            const foundSecret = guesses.value.find(g => g.ranking === 1);
            if (foundSecret) {
              isSolved.value = true;
              secretWord.value = foundSecret.word;
            }
          } catch (_) {}
        }
      }
    } catch (err: any) {
      errorMessage.value = err.message || 'Gagal terhubung ke server.';
    } finally {
      isLoading.value = false;
    }
  };

  const submitGuess = async (rawWord: string) => {
    if (!game.value || isSubmitting.value) return;
    const word = rawWord.trim().toLowerCase();
    if (!word) return;

    errorMessage.value = null;
    duplicateNotice.value = null;

    // Check duplicate
    const existing = guesses.value.find(g => g.word === word);
    if (existing) {
      duplicateNotice.value = `Kata "${word}" sudah pernah Anda tebak (Peringkat #${existing.ranking})`;
      return;
    }

    isSubmitting.value = true;
    try {
      const result = await postGuess(game.value.game_id, word, sessionId.value);
      
      const newGuess: Guess = {
        word: result.word,
        ranking: result.ranking,
        similarity: result.similarity,
        is_correct: result.is_correct,
        created_at: new Date().toISOString()
      };

      // Add to front of recent guesses
      guesses.value = [newGuess, ...guesses.value];

      // Save to local storage
      localStorage.setItem(`konteks_guesses_${game.value.game_id}`, JSON.stringify(guesses.value));

      if (result.is_correct) {
        isSolved.value = true;
        secretWord.value = result.secret_word || result.word;
        showSolvedModal.value = true;
        triggerCelebration();
      }
    } catch (err: any) {
      errorMessage.value = err.message || 'Terjadi kesalahan saat memproses tebakan.';
    } finally {
      isSubmitting.value = false;
    }
  };

  const triggerCelebration = () => {
    confetti({
      particleCount: 120,
      spread: 70,
      origin: { y: 0.6 }
    });
  };

  const playRandomGame = async () => {
    isLoading.value = true;
    errorMessage.value = null;
    duplicateNotice.value = null;
    isSolved.value = false;
    secretWord.value = null;
    guesses.value = [];
    showSolvedModal.value = false;
    try {
      const randomGame = await fetchRandomGame();
      game.value = randomGame;
      localStorage.removeItem(`konteks_guesses_${randomGame.game_id}`);
    } catch (err: any) {
      errorMessage.value = err.message || 'Gagal memuat game acak.';
    } finally {
      isLoading.value = false;
    }
  };

  const resetGame = () => {
    if (!game.value) return;
    localStorage.removeItem(`konteks_guesses_${game.value.game_id}`);
    guesses.value = [];
    isSolved.value = false;
    secretWord.value = null;
    showSolvedModal.value = false;
    errorMessage.value = null;
    duplicateNotice.value = null;
  };

  onMounted(() => {
    loadGame();
  });

  return {
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
    loadGame,
    playRandomGame,
    resetGame
  };
}
