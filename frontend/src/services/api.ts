import type { TodayGame, GuessResponse, GameHistoryResponse } from '../types/game';

const API_BASE = '/api';

export async function fetchTodayGame(): Promise<TodayGame> {
  const res = await fetch(`${API_BASE}/game/today`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Gagal memuat game hari ini' }));
    throw new Error(err.detail || 'Gagal memuat game hari ini');
  }
  return res.json();
}

export async function fetchRandomGame(): Promise<TodayGame> {
  const res = await fetch(`${API_BASE}/game/random`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Gagal memuat game acak' }));
    throw new Error(err.detail || 'Gagal memuat game acak');
  }
  return res.json();
}

export async function postGuess(gameId: string, word: string, sessionId: string): Promise<GuessResponse> {
  const res = await fetch(`${API_BASE}/game/guess`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      game_id: gameId,
      word,
      session_id: sessionId
    })
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Tebakan gagal diproses' }));
    throw new Error(err.detail || 'Tebakan gagal diproses');
  }
  return res.json();
}

export async function fetchGameHistory(gameId: string, sessionId: string): Promise<GameHistoryResponse> {
  const res = await fetch(`${API_BASE}/game/history?game_id=${encodeURIComponent(gameId)}&session_id=${encodeURIComponent(sessionId)}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Gagal memuat riwayat tebakan' }));
    throw new Error(err.detail || 'Gagal memuat riwayat tebakan');
  }
  return res.json();
}
