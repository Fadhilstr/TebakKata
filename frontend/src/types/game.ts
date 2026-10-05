export interface TodayGame {
  game_id: string;
  game_date: string;
  total_words: number;
}

export interface Guess {
  word: string;
  ranking: number;
  similarity: number;
  is_correct: boolean;
  created_at?: string;
}

export interface GuessResponse {
  word: string;
  ranking: number;
  similarity: number;
  is_correct: boolean;
  guess_count: number;
  secret_word?: string | null;
}

export interface GameHistoryResponse {
  game_id: string;
  session_id: string;
  total_guesses: number;
  is_solved: boolean;
  best_ranking: number | null;
  secret_word: string | null;
  guesses: Guess[];
}
