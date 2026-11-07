import { useEffect, useState } from 'react'
import { api } from './api.js'
import SaksiKarti from './SaksiKarti.jsx'

const YENILEME_MS = 5000

export default function App() {
  const [ozet, setOzet] = useState([])
  const [olaylar, setOlaylar] = useState([])
  const [hata, setHata] = useState(null)

  async function yenile() {
    try {
      const [o, e] = await Promise.all([api.ozet(), api.olaylar(10)])
      setOzet(o)
      setOlaylar(e)
      setHata(null)
    } catch (err) {
      setHata(err.message)
    }
  }

  useEffect(() => {
    yenile()
    const zamanlayici = setInterval(yenile, YENILEME_MS)
    return () => clearInterval(zamanlayici)
  }, [])

  const ortam = ozet.find((s) => s.son_olcum)?.son_olcum

  return (
    <main>
      <header>
        <h1>Yapay Zekâ Destekli Akıllı Sulama Sistemi</h1>
        {ortam && (
          <p>
            Ortam sıcaklığı: <b>{ortam.sicaklik ?? '-'} °C</b> · Hava nemi: <b>{ortam.hava_nem ?? '-'} %</b>
          </p>
        )}
        <div className="dugmeler">
          <button onClick={() => api.modDegistir('otomatik')}>Otomatik mod</button>
          <button onClick={() => api.modDegistir('manuel')}>Manuel mod</button>
        </div>
        {hata && <p className="hata">Bağlantı hatası: {hata}</p>}
      </header>

      <section className="kartlar">
        {ozet.map((s) => (
          <SaksiKarti key={s.saksi.id} veri={s} />
        ))}
      </section>

      <section>
        <h2>Son sulamalar</h2>
        <table>
          <thead>
            <tr><th>Zaman</th><th>Saksı</th><th>Süre (sn)</th><th>Su (ml)</th><th>Kaynak</th></tr>
          </thead>
          <tbody>
            {olaylar.map((o) => (
              <tr key={o.id}>
                <td>{new Date(o.zaman).toLocaleString('tr-TR')}</td>
                <td>{o.saksi_id}</td>
                <td>{o.sure_sn}</td>
                <td>{Math.round(o.su_ml)}</td>
                <td>{o.kaynak}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </main>
  )
}
