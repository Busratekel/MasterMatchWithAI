import React, { useState, useEffect, useRef } from 'react';
import Slider from '@mui/material/Slider';
import './StepContent.css';

const minBoy = 120, maxBoy = 220;
const minKilo = 30, maxKilo = 220;
const yasOptions = Array.from({ length: 67 }, (_, i) => i.toString()).concat('65+');

function VKIBar({ vki }) {
  const min = 10, max = 40;
  let percent = 0;
  if (vki) {
    percent = Math.min(100, Math.max(0, ((vki - min) / (max - min)) * 100));
  }
  return (
    <div className="vki-bar-container">
      <div className="vki-bar-bg">
        <div className="vki-bar-indicator" style={{ left: `calc(${percent}% - 10px)` }} />
      </div>
      <div className="vki-bar-labels">
        <span>Zayıf</span>
        <span>Orta</span>
        <span>Kilolu</span>
      </div>
    </div>
  );
}

const StepContent = ({ question, answer, onAnswerChange, answers }) => {
  // Tüm hook'lar en başta, koşulsuz
  const [localAge, setLocalAge] = useState('0');
  const [localHeight, setLocalHeight] = useState(minBoy);
  const [localWeight, setLocalWeight] = useState(minKilo);
  const [bmiValue, setBmiValue] = useState('');
  const isFirstMount = useRef(true);

  useEffect(() => {
    if (question.type === 'bmi_age' && answer && isFirstMount.current) {
      setLocalAge(answer.yas || '0');
      setLocalHeight(Number(answer?.boy) || minBoy);
      setLocalWeight(Number(answer?.kilo) || minKilo);
      isFirstMount.current = false;
    }
  }, []);

  useEffect(() => {
    if (question.type === 'bmi_age') {
      let vki = '';
      let vkiKategori = '';
      let yasKategori = '';
      let yasNumeric = null;
      if (localAge && !isNaN(Number(localAge))) {
        yasNumeric = Number(localAge);
      } else if (localAge === '65+') {
        yasNumeric = 65;
      }
      // Yaş kategorisini belirle
      if (localAge !== '' && yasNumeric !== null) {
        if (yasNumeric <= 7) {
          yasKategori = '0-7';
          vkiKategori = 'Zayıf'; // 0-7 yaş için otomatik Zayıf
        } else {
          yasKategori = '7+';
        }
      }
      // VKI hesapla (her yaş için)
      if (localAge !== '' && yasNumeric !== null && localHeight > 0 && localWeight > 0) {
        const vkiHesaplanan = (localWeight / ((localHeight / 100) ** 2));
        vki = vkiHesaplanan.toFixed(1); // vki_sayisal için her zaman sayısal değer
        if (yasNumeric > 7) {
          setBmiValue(vki);
          if (vkiHesaplanan < 18.5) {
            vkiKategori = 'Zayıf';
          } else if (vkiHesaplanan < 25) {
            vkiKategori = 'Orta';
          } else {
            vkiKategori = 'Kilolu';
          }
        } else {
          setBmiValue(''); // 0-7 yaş için VKI gösterilmez
        }
      } else {
      setBmiValue('');
      }
      // Yeni cevapları oluştur
      const newBmiAge = {
        yas_gercek: localAge,
        boy: localHeight,
        kilo: localWeight,
        vki: vkiKategori,
        vki_sayisal: vki
      };
      // Eğer cevap değiştiyse güncelle
      if (JSON.stringify(answer) !== JSON.stringify(newBmiAge)) {
        onAnswerChange(question.id, newBmiAge);
      }
      // Kategoriler için de aynı kontrol
      if (yasKategori && answers.yas !== yasKategori) {
        onAnswerChange('yas', yasKategori);
      }
      if (vkiKategori && answers.bmi !== vkiKategori) {
        onAnswerChange('bmi', vkiKategori);
      }
    }
  }, [localAge, localHeight, localWeight, question.id, onAnswerChange, question.type, answer, answers, bmiValue]);

  // Yaş 7'den küçükse boy ve kilo değerlerini resetle
  useEffect(() => {
    if (question.id === 'bmi_age' && localAge !== '' && Number(localAge) <= 7) {
      if (localHeight !== minBoy) setLocalHeight(minBoy);
      if (localWeight !== minKilo) setLocalWeight(minKilo);
    }
  }, [localAge, question.id]);

  // bmi_age tipi için özel render
  if (question.id === 'bmi_age') {
      return (
    <>
      <div className="step-content-header">
      <h2 className="step-question-title">{question.question}</h2>
      <hr className="content-divider" />
      </div>
        <div className="bmi-age-special-wrapper">
        <div className="bmi-row-modern" style={{ marginBottom: '4px' }}>
            <label htmlFor="yas-slider">Yaşınız:</label>
            <div className="bmi-value-group">
              <input className="bmi-value-box" value={localAge === 65 ? '65+' : localAge} readOnly />
              <span className="bmi-unit">yaş</span>
            </div>
          </div>
          <Slider
            id="yas-slider"
            min={0}
            max={65}
            step={1}
            value={Number(localAge)}
            onChange={(_, v) => setLocalAge(Number(v))}
            className="MuiSlider-root"
          />
          {/* Her zaman boy ve kilo inputları gösterilecek */}
          <div className="bmi-row-modern" style={{ marginBottom: '4px' }}>
            <label htmlFor="boy-slider">Boyunuz:</label>
            <div className="bmi-value-group">
              <input className={`bmi-value-box${localAge !== '' && Number(localAge) <= 7 ? ' bmi-disabled' : ''}`} value={localHeight} readOnly />
              <span className="bmi-unit">cm</span>
            </div>
          </div>
          <Slider
            id="boy-slider"
            min={minBoy}
            max={maxBoy}
            value={Number(localHeight)}
            onChange={(_, v) => setLocalHeight(Number(v))}
            className={`MuiSlider-root${localAge !== '' && Number(localAge) <= 7 ? ' bmi-disabled-slider' : ''}`}
            disabled={localAge !== '' && Number(localAge) <= 7}
          />
          <div className="bmi-row-modern" style={{ marginBottom: '4px' }}>
            <label htmlFor="kilo-slider">Kilonuz:</label>
            <div className="bmi-value-group">
              <input className={`bmi-value-box${localAge !== '' && Number(localAge) <= 7 ? ' bmi-disabled' : ''}`} value={localWeight} readOnly />
              <span className="bmi-unit">kg</span>
            </div>
          </div>
          <Slider
            id="kilo-slider"
            min={minKilo}
            max={maxKilo}
            value={localWeight}
            onChange={(_, v) => setLocalWeight(v)}
            className={`MuiSlider-root${localAge !== '' && Number(localAge) <= 7 ? ' bmi-disabled-slider' : ''}`}
            disabled={localAge !== '' && Number(localAge) <= 7}
          />
          {/* Uyarı veya BMI barı */}
          <div className="vki-row" style={{ width: '100%', flexDirection: 'column', alignItems: 'center', marginTop: '82px' }}>
            {localAge !== '' && Number(localAge) <= 7 ? (
              <span className="bmi-warning">0-7 yaş arası için BMI hesaplanmaz.</span>
            ) : (
              <>
                <VKIBar vki={bmiValue} />
                {bmiValue && (
                  <div className="vki-value">VKI: <b>{bmiValue}</b></div>
                )}
              </>
            )}
          </div>
        </div>
      </>
    );
  }

  // Diğer soru tipleri için eski render
  const handleOptionClick = (option) => {
    
    if (question.id === 'uyku_pozisyonu') {
      const current = Array.isArray(answer) ? answer : [];
      
      // Eğer Pozisyonum değişken seçildiyse, sadece onu seçili yap
      if (option === 'Pozisyonum değişken') {
        const newAnswer = current.includes(option) ? [] : ['Pozisyonum değişken'];
        onAnswerChange(question.id, newAnswer);
        return;
      }
      // Diğerlerinden biri seçildiyse, Pozisyonum değişkeni kaldır ve klasik checkbox mantığı uygula
      let newAnswer = current.includes(option)
        ? current.filter(opt => opt !== option)
        : [...current.filter(opt => opt !== 'Pozisyonum değişken'), option];
      onAnswerChange(question.id, newAnswer);
      return;
    }
    onAnswerChange(question.id, option);
  };

  /*const handleCheckboxChange = (option) => {
    const currentAnswer = Array.isArray(answer) ? answer : [];
    const newAnswer = currentAnswer.includes(option)
      ? currentAnswer.filter(opt => opt !== option)
      : [...currentAnswer, option];
    onAnswerChange(question.id, newAnswer);
  };*/


  const isOptionSelected = (option) => {
    if (question.type === 'radio') {
      return answer === option;
    } else {
      const currentAnswer = answer || [];
      if (!Array.isArray(currentAnswer)) return false;

      if (option === 'Hepsi') {
        // Hepsi seçili sayılması için: tüm normal seçenekler seçiliyse
        const normalOptions = question.options.filter(opt => !['Hepsi', 'Hiçbir ağrı hissetmiyorum', 'Pozisyonum değişken'].includes(opt));
        return normalOptions.length > 0 && normalOptions.every(opt => currentAnswer.includes(opt));
      }
      return currentAnswer.includes(option);
    }
  };

  const isTwoOptions = question.options && question.options.length === 2 && !question.options.includes('Hepsi') && !question.options.includes('HİSSETMİYORUM');

  

  return (
          <>
        <div className="step-content-header">
        <h2 className="step-question-title">{question.question}</h2>
        <hr className="content-divider" />
        </div>
      <div className="step-content-actions">
      <div className={`options-container ${isTwoOptions ? 'two-options' : ''}`}>
        {question.options && question.options.map((option, index) => {
          // İdeal sertlik sorusu için sadece 3 temel seçenek göster
          if (question.id === 'ideal_sertlik' && !['Yumuşak', 'Orta', 'Sert'].includes(option)) {
            return null;
          }
          
          // Option metnini dosya adına çevir
          const getImageSrc = (option) => {
            return require(`../assets/${option
              .toLowerCase()
              .replace(/ /g, '')
              .replace(/ı/g, 'i')
              .replace(/ü/g, 'u')
              .replace(/ş/g, 's')
              .replace(/ö/g, 'o')
              .replace(/ç/g, 'c')
              .replace(/ğ/g, 'g')
              .replace(/İ/g, 'i')
              .replace(/Ü/g, 'u')
              .replace(/Ş/g, 's')
              .replace(/Ö/g, 'o')
              .replace(/Ç/g, 'c')
              .replace(/Ğ/g, 'g')
            }.png`);
          };
          return (
            <div
              key={index}
              className={`option-item ${isOptionSelected(option) ? 'selected' : ''}`}
              onClick={() => handleOptionClick(option)}
              style={{
                pointerEvents: 'auto',
                opacity: 1
              }}
            >
              {/* Option görseli */}
              <div className={`option-image-wrapper`}>
                <div className={`option-image-border${isOptionSelected(option) ? ' selected' : ''}`}>
                  <img
                    src={getImageSrc(option)}
                    alt={option}
                    className="option-image"
                    style={{ width: 200, height: 300, objectFit: 'contain', marginBottom: 8, display: 'block', marginLeft: 'auto', marginRight: 'auto' }}
                  />
                </div>
              </div>
              <span className="option-text">{option}</span>
            </div>
          );
        })}
        </div>
        <div className="form-navigation">
          <div className="form-nav-right">
          </div>
        </div>
      </div>
    </>
  );
};

export default StepContent; 