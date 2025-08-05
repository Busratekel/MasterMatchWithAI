import React, { useState } from 'react';
import Slider from '@mui/material/Slider'; // npm install @mui/material @emotion/react @emotion/styled
import './VKICalculator.css';

const minBoy = 120, maxBoy = 220;
const minKilo = 30, maxKilo = 220;

const yasOptions = Array.from({ length: 101 }, (_, i) => i.toString()).concat('99+');

function VKICalculator() {
  const [yas, setYas] = useState('');
  const [boy, setBoy] = useState(170);
  const [kilo, setKilo] = useState(70);

  let vki = '';
  let kategori = '';
  let aciklama = '';

  if (yas !== '' && Number(yas) > 7) {
    vki = (kilo / ((boy / 100) ** 2)).toFixed(1);
    if (vki < 18.5) {
      kategori = 'Zayıf';
      aciklama = 'Kilonuz idealin altında.';
    } else if (vki < 25) {
      kategori = 'Orta';
      aciklama = 'Kilonuz ideal seviyede.';
    } else {
      kategori = 'Kilolu';
      aciklama = 'Kilonuz idealin üstünde.';
    }
  } else if (yas !== '' && Number(yas) <= 7) {
    kategori = 'Zayıf';
    aciklama = '0-7 yaş arası için BMI hesaplanmaz.';
  }

  return (
    <div className="vki-container">
      <h2>Vücut Kitle İndeksi Hesaplama</h2>
      <div className="vki-row">
        <label>Yaşınız:</label>
        <select value={yas} onChange={e => setYas(e.target.value)}>
          <option value="">Seç</option>
          {yasOptions.map(opt => (
            <option key={opt} value={opt}>{opt}</option>
          ))}
        </select>
      </div>
      {yas !== '' && Number(yas) > 7 && (
        <>
          <div className="vki-row">
            <label>Boyunuz: <b>{boy} cm</b></label>
            <Slider min={minBoy} max={maxBoy} value={boy} onChange={(_, v) => setBoy(v)} />
          </div>
          <div className="vki-row">
            <label>Kilonuz: <b>{kilo} kg</b></label>
            <Slider min={minKilo} max={maxKilo} value={kilo} onChange={(_, v) => setKilo(v)} />
          </div>
        </>
      )}
      <div className="vki-result">
        {kategori && (
          <>
            <h3>Kategori: <span className={`vki-cat vki-cat-${kategori.toLowerCase()}`}>{kategori}</span></h3>
            {vki && <div>VKI: <b>{vki}</b></div>}
            <div className="vki-desc">{aciklama}</div>
          </>
        )}
      </div>
    </div>
  );
}

export default VKICalculator; 