<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm">
    <div class="w-full max-w-md bg-[#16181f] border border-surface-border rounded-2xl p-6 text-left shadow-2xl relative max-h-[90vh] overflow-y-auto">
      
      <button 
        @click="$emit('close')"
        class="absolute top-4 right-4 p-1.5 text-gray-400 hover:text-white rounded-lg transition-colors"
      >
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      <h2 class="text-xl font-bold text-white tracking-tight mb-3 flex items-center gap-2">
        <span>Cara Bermain</span>
        <span class="text-xs px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
          Bantuan
        </span>
      </h2>

      <div class="space-y-4 text-sm text-gray-300">
        <p>
          Tujuan Anda adalah menemukan <strong class="text-white">satu kata rahasia</strong> dalam bahasa Indonesia setiap harinya.
        </p>

        <div class="p-3.5 rounded-xl bg-surface-card border border-surface-border space-y-2">
          <div class="font-semibold text-white text-xs uppercase tracking-wider text-emerald-400">
            Mekanisme Semantik (Makna)
          </div>
          <p class="text-xs text-gray-400 leading-relaxed">
            Permainan ini menggunakan kecerdasan buatan (*AI Semantic Similarity*) untuk menghitung seberapa dekat makna kata tebakan Anda dengan kata rahasia.
          </p>
        </div>

        <div>
          <div class="font-semibold text-white mb-2">Sistem Peringkat (Ranking):</div>
          <ul class="space-y-2 text-xs">
            <li class="flex items-center gap-2.5">
              <span class="font-mono font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">#1</span>
              <span><strong>Kata Rahasia</strong> — Anda memenangkan permainan!</span>
            </li>
            <li class="flex items-center gap-2.5">
              <span class="font-mono font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">#2 - #30</span>
              <span><strong>Hampir Benar</strong> — Makna sangat identik atau sinonim langsung.</span>
            </li>
            <li class="flex items-center gap-2.5">
              <span class="font-mono font-bold text-teal-400 bg-teal-500/10 px-2 py-0.5 rounded border border-teal-500/20">#31 - #250</span>
              <span><strong>Sangat Dekat</strong> — Berada dalam satu topik/konteks yang sama.</span>
            </li>
            <li class="flex items-center gap-2.5">
              <span class="font-mono font-bold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">#251 - #1000</span>
              <span><strong>Mulai Mendekat</strong> — Memiliki keterkaitan umum.</span>
            </li>
            <li class="flex items-center gap-2.5">
              <span class="font-mono font-bold text-gray-400 bg-gray-800 px-2 py-0.5 rounded border border-gray-700">> #1000</span>
              <span><strong>Jauh</strong> — Makna kata tidak ada hubungan langsung.</span>
            </li>
          </ul>
        </div>

        <div class="border-t border-surface-border pt-3">
          <p class="text-xs text-gray-400 leading-relaxed">
            <strong class="text-gray-300">Catatan:</strong> Ranking dihitung terhadap puluhan ribu kata bahasa Indonesia. Tebakan tidak dibatasi jumlah percobaan. Kata baru diperbarui setiap pukul 00:00 WIB (Asia/Jakarta).
          </p>
        </div>
      </div>

      <button
        @click="$emit('close')"
        class="mt-6 w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm rounded-xl transition-colors"
      >
        Saya Mengerti, Mulai Main
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineEmits<{
  (e: 'close'): void;
}>();
</script>
