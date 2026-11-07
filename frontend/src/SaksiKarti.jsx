import { api } from './api.js'

// Tek bir saksının özet kartı.
// GÖREV (Öğrenci B): Kartın altına son 24 saatin toprak nemi grafiğini ekleyin
// (recharts kütüphanesi yüklü; veriyi api.olcumler(saksiId) ile alın).
export default function SaksiKarti({ veri }) {
  const { saksi, son_olcum, son_goruntu, toplam_su_ml, son_24_saat_su_ml } = veri

  return (
    <article className="kart">
      <h3>{saksi.ad}</h3>
      {son_goruntu ? (
        <img src={api.goruntuAdresi(son_goruntu.id)} alt={`${saksi.ad} fotoğrafı`} />
      ) : (
        <div className="foto-yok">Fotoğraf yok</div>
      )}
      <p>Toprak nemi: <b>{son_olcum ? `${son_olcum.toprak_nem} %` : '-'}</b></p>
      <p>Vana: <b>{son_olcum?.vana_acik ? 'Açık' : 'Kapalı'}</b></p>
      <p>Son 24 saat su: <b>{Math.round(son_24_saat_su_ml)} ml</b></p>
      <p>Toplam su: <b>{Math.round(toplam_su_ml)} ml</b></p>
      {son_goruntu?.yesil_oran != null && (
        <p>Yeşil oran: <b>{(son_goruntu.yesil_oran * 100).toFixed(1)} %</b></p>
      )}
      <button onClick={() => api.manuelSula(saksi.id, 5)}>5 sn sula</button>
    </article>
  )
}
