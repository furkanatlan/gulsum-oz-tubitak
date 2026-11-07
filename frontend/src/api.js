// Backend API çağrıları. Tüm adresler /api ile başlar (vite.config.js yönlendirir).

async function istek(yol, secenekler = {}) {
  const yanit = await fetch(yol, {
    headers: { 'Content-Type': 'application/json' },
    ...secenekler,
  })
  if (!yanit.ok) throw new Error(`${yol} -> ${yanit.status}`)
  return yanit.json()
}

export const api = {
  ozet: () => istek('/api/saksilar/ozet'),
  olcumler: (saksiId, saat = 24) => istek(`/api/olcumler?saksi_id=${saksiId}&saat=${saat}`),
  olaylar: (limit = 20) => istek(`/api/sulama/olaylar?limit=${limit}`),
  manuelSula: (saksiId, sureSn) =>
    istek('/api/sulama/manuel', { method: 'POST', body: JSON.stringify({ saksi_id: saksiId, sure_sn: sureSn }) }),
  modDegistir: (mod) => istek('/api/sulama/mod', { method: 'POST', body: JSON.stringify({ mod }) }),
  goruntuAdresi: (id) => `/api/goruntuler/${id}/dosya`,
}
