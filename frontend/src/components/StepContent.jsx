import React, { useState, useEffect, useRef } from 'react';
import Tooltip from '@mui/material/Tooltip';
import ClickAwayListener from '@mui/material/ClickAwayListener';
// import Slider from '@mui/material/Slider'; // Eski slider UI - yoruma alındı
import './StepContent.css';

// Tüm görselleri import et (Webpack build için gerekli)
import imgHareketliUykuPozisyonu from '../assets/hareketliuykupozisyonu.png';
import imgSirtUstuUykuPozisyonu from '../assets/sirtustuuykupozisyonu.png';
import imgYanUykuPozisyonu from '../assets/yanuykupozisyonu.png';
import imgYuzUstuUykuPozisyonu from '../assets/yuzustuuykupozisyonu.png';
import imgGeneldeOrtaTempoda from '../assets/geneldeortatempoda,dengelibirgunumoluyor..png';
import imgOldukcaSakinBirTempom from '../assets/oldukcasakinbirtempomvar..png';
import imgYoguntempoluBirGun from '../assets/yoguntempolubirgungeciriyorum..png';
import imgHicbirProblemYasamiyorum from '../assets/hicbirproblemyasamiyorum,sabahlaridinlenmisuyaniyorum..png';
import imgNefesAlmaktaZorlaniyorum from '../assets/nefesalmaktazorlaniyorum,zamanzamanhorlamaproblemiyasiyorum.png';
import imgRefluNedeniyle from '../assets/reflunedeniylegecelerisiksikuyaniyorum..png';
import imgUykumTerlemeNedeniyle from '../assets/uykumterlemenedeniylebolunuyor..png';
import imgSadecebelAgrisi from '../assets/sadecebelagrisi.png';
import imgSadeceBoyunAgrisi from '../assets/sadeceboyunagrisi.png';
import imgSadeceOmuzAgrisi from '../assets/sadeceomuzagrisi.png';
import imgHepsi from '../assets/hepsi.png';
import imgHicbirAgriHissetmiyorum from '../assets/hicbiragrihissetmiyorum.png';
import imgEvetButurDogalMalzemelere from '../assets/evet,buturdogalmalzemelerekarsialerjim,hassasiyetimvar.png';
import imgHayirYok from '../assets/hayir,yok.png';
import imgYumusak from '../assets/yumusak.png';
import imgOrta from '../assets/orta.png';
import imgSert from '../assets/sert.png';
import imgYukseklikAlcak from '../assets/yukseklikalcak.png';
import imgYukseklikOrta from '../assets/yukseklikorta.png';
import imgYukseklikYuksek from '../assets/yukseklikyuksek.png';
import imgYumusakYatak from '../assets/yumusakyatak.png';
import imgOrtaSertYatak from '../assets/orta-sertyatak.png';
import imgSertYatak from '../assets/sertyatak.png';

// Görsel mapping objesi
const IMAGE_MAP = {
  // Uyku pozisyonları
  'hareketliuykupozisyonu': imgHareketliUykuPozisyonu,
  'sirtustuuykupozisyonu': imgSirtUstuUykuPozisyonu,
  'yanuykupozisyonu': imgYanUykuPozisyonu,
  'yuzustuuykupozisyonu': imgYuzUstuUykuPozisyonu,
  // Tempo
  'geneldeortatempoda,dengelibirgunumoluyor.': imgGeneldeOrtaTempoda,
  'oldukcasakinbirtempomvar.': imgOldukcaSakinBirTempom,
  'yoguntempolubirgungeciriyorum.': imgYoguntempoluBirGun,
  // Uyku düzeni
  'hicbirproblemyasamiyorum,sabahlaridinlenmisuyaniyorum.': imgHicbirProblemYasamiyorum,
  'nefesalmaktazorlaniyorum,zamanzamanhorlamaproblemiyasiyorum': imgNefesAlmaktaZorlaniyorum,
  'reflunedeniylegecelerisiksikuyaniyorum.': imgRefluNedeniyle,
  'uykumterlemenedeniylebolunuyor.': imgUykumTerlemeNedeniyle,
  // Ağrı bölgeleri
  'sadecebelagrisi': imgSadecebelAgrisi,
  'sadeceboyunagrisi': imgSadeceBoyunAgrisi,
  'sadeceomuzagrisi': imgSadeceOmuzAgrisi,
  'hepsi': imgHepsi,
  'hicbiragrihissetmiyorum': imgHicbirAgriHissetmiyorum,
  // Doğal malzeme
  'evet,buturdogalmalzemelerekarsialerjim,hassasiyetimvar': imgEvetButurDogalMalzemelere,
  'hayir,yok': imgHayirYok,
  // Yastık sertliği
  'yumusak': imgYumusak,
  'orta': imgOrta,
  'sert': imgSert,
  // Yastık yüksekliği
  'yukseklikalcak': imgYukseklikAlcak,
  'yukseklikorta': imgYukseklikOrta,
  'yukseklikyuksek': imgYukseklikYuksek,
  // Yatak sertliği
  'yumusakyatak': imgYumusakYatak,
  'orta-sertyatak': imgOrtaSertYatak,
  'sertyatak': imgSertYatak
};

const minBoy = 120, maxBoy = 220;
const minKilo = 30, maxKilo = 220;
const yasSelectOptions = Array.from({ length: 86 }, (_, i) => ({
  value: String(i),
  label: i === 85 ? '85+' : String(i),
}));
const boySelectOptions = Array.from({ length: maxBoy - minBoy + 1 }, (_, i) => {
  const boy = minBoy + i;
  return { value: String(boy), label: `${boy} cm` };
});
const kiloSelectOptions = Array.from({ length: maxKilo - minKilo + 1 }, (_, i) => {
  const kilo = minKilo + i;
  return { value: String(kilo), label: `${kilo} kg` };
});

function BmiDropdown({
  id,
  title,
  hint,
  value,
  options,
  disabled = false,
  open,
  onToggle,
  onChange,
}) {
  const listRef = useRef(null);
  const safeValue = value && typeof value === 'object' && value.value !== undefined
    ? String(value.value)
    : (value === undefined || value === null ? '' : String(value));
  const selected = options.find((opt) => String(opt.value) === safeValue);
  const selectedLabel = selected ? String(selected.label) : '';

  useEffect(() => {
    if (!open || !listRef.current) return;
    const active = listRef.current.querySelector('.bmi-dd-option.selected');
    if (active && typeof active.scrollIntoView === 'function') {
      active.scrollIntoView({ block: 'nearest' });
    }
  }, [open, safeValue]);

  return (
    <div className={`bmi-dropdown-field${disabled ? ' disabled' : ''}${open ? ' open' : ''}`}>
      <span className="bmi-dropdown-title" id={`${id}-label`}>{title}</span>
      <div className="bmi-dd">
        <button
          type="button"
          id={id}
          className={`bmi-dd-trigger${safeValue ? ' has-value' : ''}${open ? ' open' : ''}`}
          aria-haspopup="listbox"
          aria-expanded={open}
          aria-labelledby={`${id}-label`}
          disabled={disabled}
          onClick={() => !disabled && onToggle()}
        >
          <span className="bmi-dd-texts">
            <span className="bmi-dd-hint">{hint}</span>
            {selectedLabel ? <span className="bmi-dd-value">{selectedLabel}</span> : null}
          </span>
          <span className="bmi-dd-chevron" aria-hidden="true" />
        </button>
        {open && !disabled && (
          <ul
            className="bmi-dd-menu"
            role="listbox"
            ref={listRef}
            aria-labelledby={`${id}-label`}
          >
            {options.map((opt) => {
              const optValue = String(opt.value);
              const optLabel = String(opt.label);
              const isSelected = safeValue === optValue;
              return (
                <li
                  key={optValue}
                  role="option"
                  aria-selected={isSelected}
                  className={`bmi-dd-option${isSelected ? ' selected' : ''}`}
                  onClick={() => {
                    onChange(optValue);
                    onToggle(false);
                  }}
                >
                  {optLabel}
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </div>
  );
}

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
    </div>
  );
}

const StepContent = ({ question, answer, onAnswerChange, answers }) => {
  // Tüm hook'lar en başta, koşulsuz
  const [localAge, setLocalAge] = useState('');
  const [localHeight, setLocalHeight] = useState('');
  const [localWeight, setLocalWeight] = useState('');
  const [bmiValue, setBmiValue] = useState('');
  const [vkiInfoOpen, setVkiInfoOpen] = useState(false);
  const [openDropdown, setOpenDropdown] = useState(null); // 'yas' | 'boy' | 'kilo' | null
  const isFirstMount = useRef(true);
  const ageNumber = (() => {
    if (localAge && typeof localAge === 'object' && localAge.value !== undefined) {
      return Number(localAge.value);
    }
    if (localAge === '' || localAge === undefined || localAge === null) return NaN;
    return Number(localAge);
  })();
  const isChild = !Number.isNaN(ageNumber) && ageNumber <= 7;

  useEffect(() => {
    if (!openDropdown) return undefined;
    const handleOutside = (event) => {
      if (!event.target.closest('.bmi-dropdown-field')) {
        setOpenDropdown(null);
      }
    };
    document.addEventListener('mousedown', handleOutside);
    document.addEventListener('touchstart', handleOutside);
    return () => {
      document.removeEventListener('mousedown', handleOutside);
      document.removeEventListener('touchstart', handleOutside);
    };
  }, [openDropdown]);

  const toggleDropdown = (key, forceClose) => {
    if (forceClose === false) {
      setOpenDropdown(null);
      return;
    }
    setOpenDropdown((prev) => (prev === key ? null : key));
  };

  useEffect(() => {
    if (question.type === 'bmi_age' && answer && isFirstMount.current) {
      const pick = (v) => {
        if (v && typeof v === 'object' && v.value !== undefined) return String(v.value);
        if (v === undefined || v === null || v === '') return '';
        return String(v);
      };
      const restoredAge = pick(answer.yas_gercek);
      setLocalAge(restoredAge);
      if (restoredAge === '' || Number(restoredAge) > 7) {
        setLocalHeight(pick(answer.boy));
        setLocalWeight(pick(answer.kilo));
      }
      isFirstMount.current = false;
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (question.type === 'bmi_age') {
      if (localAge === '') {
        if (bmiValue) setBmiValue('');
        if (answer && answer.yas_gercek !== '' && answer.yas_gercek !== undefined) {
          onAnswerChange(question.id, { yas_gercek: '', boy: '', kilo: '', vki: '', vki_sayisal: '' });
        }
        if (answers.yas) onAnswerChange('yas', '');
        if (answers.bmi) onAnswerChange('bmi', '');
        return;
      }

      let vki = '';
      let vkiKategori = '';
      let yasKategori = '';
      let yasNumeric = null;
      if (localAge && !isNaN(Number(localAge))) {
        yasNumeric = Number(localAge);
      } else if (localAge === '65+' || localAge === '85+') {
        yasNumeric = localAge === '85+' ? 85 : 65;
      }

      if (localAge !== '' && yasNumeric !== null) {
        if (yasNumeric <= 7) {
          yasKategori = '0-7';
          vkiKategori = 'Zayıf';
        } else {
          yasKategori = '7+';
        }
      }

      const heightNum = Number(localHeight && typeof localHeight === 'object' ? localHeight.value : localHeight);
      const weightNum = Number(localWeight && typeof localWeight === 'object' ? localWeight.value : localWeight);
      const ageRaw = localAge && typeof localAge === 'object' ? localAge.value : localAge;
      const ageStr = ageRaw === undefined || ageRaw === null ? '' : String(ageRaw);
      const hasBody = ageStr !== '' && localHeight !== '' && localWeight !== '' && heightNum > 0 && weightNum > 0;

      if (ageStr !== '' && yasNumeric !== null && hasBody) {
        const vkiHesaplanan = (weightNum / ((heightNum / 100) ** 2));
        vki = vkiHesaplanan.toFixed(1);
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
          setBmiValue('');
        }
      } else {
        setBmiValue('');
        if (yasNumeric === null || yasNumeric > 7) {
          vkiKategori = '';
        }
      }

      const newBmiAge = {
        yas_gercek: ageStr,
        boy: isChild ? minBoy : (localHeight === '' ? '' : heightNum),
        kilo: isChild ? minKilo : (localWeight === '' ? '' : weightNum),
        vki: vkiKategori,
        vki_sayisal: vki
      };

      if (JSON.stringify(answer) !== JSON.stringify(newBmiAge)) {
        onAnswerChange(question.id, newBmiAge);
      }
      if (yasKategori && answers.yas !== yasKategori) {
        onAnswerChange('yas', yasKategori);
      }
      if (vkiKategori && answers.bmi !== vkiKategori) {
        onAnswerChange('bmi', vkiKategori);
      } else if (!vkiKategori && answers.bmi) {
        onAnswerChange('bmi', '');
      }
    }
  }, [localAge, localHeight, localWeight, question.id, onAnswerChange, question.type, answer, answers, bmiValue, isChild]);

  // Yaş 7'den küçükse boy ve kilo seçimini temizle
  useEffect(() => {
    if (question.id === 'bmi_age' && isChild) {
      if (localHeight !== '') setLocalHeight('');
      if (localWeight !== '') setLocalWeight('');
      if (openDropdown === 'boy' || openDropdown === 'kilo') setOpenDropdown(null);
    }
  }, [isChild, localHeight, localWeight, openDropdown, question.id]);

  // bmi_age tipi için özel render
  if (question.id === 'bmi_age') {
      return (
    <>
      <div className="step-content-header">
      <h2 className="step-question-title">{question.question}</h2>
      <hr className="content-divider" />
      </div>
        {/* Yaş, Boy, Kilo - özel dropdown (ikinci görseldeki gibi) */}
        <div className="bmi-input-container bmi-dropdown-container">
          <BmiDropdown
            id="yas-select"
            title="Yaş"
            value={localAge}
            options={yasSelectOptions}
            open={openDropdown === 'yas'}
            onToggle={(force) => toggleDropdown('yas', force)}
            onChange={setLocalAge}
          />

          <BmiDropdown
            id="boy-select"
            title="Boy"
            value={localHeight}
            options={boySelectOptions}
            disabled={isChild}
            open={openDropdown === 'boy'}
            onToggle={(force) => toggleDropdown('boy', force)}
            onChange={setLocalHeight}
          />

          <BmiDropdown
            id="kilo-select"
            title="Kilo"
            value={localWeight}
            options={kiloSelectOptions}
            disabled={isChild}
            open={openDropdown === 'kilo'}
            onToggle={(force) => toggleDropdown('kilo', force)}
            onChange={setLocalWeight}
          />
        </div>

        {/* VKI Container */}
        <div className="vki-container">
          {isChild ? (
            <span className="bmi-warning">0-7 yaş arası için VKI değeri hesaplanamaz.</span>
          ) : (
            <div className="vki-content-wrapper">
              <VKIBar vki={bmiValue} />
              {bmiValue && (
                  <div className="vki-value" style={{ display: 'flex', alignItems: 'center', gap: 6, whiteSpace: 'nowrap' }}>
                  <ClickAwayListener onClickAway={() => setVkiInfoOpen(false)}>
                  <Tooltip
                    title={'VKİ (Vücut Kitle İndeksi), kilonuzun boyunuza oranıdır. Referans: 18.5 altı Zayıf, 18.5–24.9 Orta, 25 ve üzeri Kilolu.'}
                    placement="top"
                    arrow
                    open={vkiInfoOpen}
                    onClose={() => setVkiInfoOpen(false)}
                    disableHoverListener
                    disableFocusListener
                    disableTouchListener
                  >
                    <span
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        width: 18,
                        height: 18,
                        borderRadius: '50%',
                        background: '#e3f2fd',
                        color: '#1976d2',
                        fontSize: 12,
                        fontWeight: 700,
                        cursor: 'help'
                      }}
                      onMouseEnter={() => setVkiInfoOpen(true)}
                      onMouseLeave={() => setVkiInfoOpen(false)}
                      onFocus={() => setVkiInfoOpen(true)}
                      onBlur={() => setVkiInfoOpen(false)}
                      onClick={(e) => { e.stopPropagation(); setVkiInfoOpen(prev => !prev); }}
                      onTouchEnd={(e) => { e.preventDefault(); e.stopPropagation(); setVkiInfoOpen(prev => !prev); }}
                      onClickCapture={(e) => e.stopPropagation()}
                      role="button"
                      aria-label="VKI bilgisi"
                    >
                      ?
                    </span>
                  </Tooltip>
                  </ClickAwayListener>
                  Vücut Kitle İndeksi:
                  <span className="vki-value-box">{bmiValue}</span>
                </div>
              )}
            </div>
          )}
        </div>
      </>
    );
  }

  // Diğer soru tipleri için eski render
  const handleOptionClick = (option) => {
    
    if (question.id === 'uyku_pozisyonu') {
      const current = Array.isArray(answer) ? answer : [];
      
      // Eğer Hareketli Uyku Pozisyonu seçildiyse, sadece onu seçili yap
      if (option === 'Hareketli Uyku Pozisyonu') {
        const newAnswer = current.includes(option) ? [] : ['Hareketli Uyku Pozisyonu'];
        onAnswerChange(question.id, newAnswer);
        return;
      }
      // Diğerlerinden biri seçildiyse, Hareketli Uyku Pozisyonu kaldır ve klasik checkbox mantığı uygula
      let newAnswer = current.includes(option)
        ? current.filter(opt => opt !== option)
        : [...current.filter(opt => opt !== 'Hareketli Uyku Pozisyonu'), option];
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
        const normalOptions = question.options.filter(opt => !['Hepsi', 'Hiçbir ağrı hissetmiyorum', 'Hareketli Uyku Pozisyonu'].includes(opt));
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
      <div className={`options-container ${isTwoOptions ? 'two-options' : ''} ${question.type === 'checkbox' ? 'checkbox-options' : ''}`}>
        {question.options && question.options.map((option, index) => {
          // İdeal sertlik sorusu için sadece temel seçenekleri göster ("Yastık" ekini temizle)
          if (question.id === 'ideal_sertlik') {
            const base = option.replace(/\s*yastık$/i, '');
            if (!['Yumuşak', 'Orta-Sert', 'Sert'].includes(base)) {
              return null;
            }
          }
          
          // Option metnini dosya adına çevir
          const getImageSrc = (option) => {
            // Yastık yüksekliği için özel dosya adları kullan
            if (question.id === 'yastik_yukseklik') {
              const map = {
                'Alçak': 'yukseklikalcak',
                'Orta': 'yukseklikorta',
                'Yüksek': 'yukseklikyuksek'
              };
              const key = map[option] || 'yukseklikorta';
              return IMAGE_MAP[key] || IMAGE_MAP['yukseklikorta'];
            }
            
            // Yatak sertliği için özel dosya adları kullan
            if (question.id === 'sertlik') {
              const map = {
                'Yumuşak Yatak': 'yumusakyatak',
                'Orta-Sert Yatak': 'orta-sertyatak',
                'Sert Yatak': 'sertyatak'
              };
              const key = map[option];
              if (key && IMAGE_MAP[key]) {
                return IMAGE_MAP[key];
              }
            }
            
            // "Yastık" ekini temizle ve görsel eşleştirmesi yap
            const noSuffix = option.replace(/\s*yastık$/i, '');
            const mapped = noSuffix === 'Orta-Sert' ? 'Orta' : noSuffix;
            const key = mapped
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
              .replace(/Ğ/g, 'g');
            
            return IMAGE_MAP[key] || require(`../assets/${key}.png`);
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
                    style={{ width: 150, height: 280, objectFit: 'contain', marginBottom: 8, display: 'block', marginLeft: 'auto', marginRight: 'auto' }}
                  />
                </div>
              </div>
              <span className="option-text">
                {typeof option === 'object' && option !== null
                  ? String(option.label ?? option.value ?? '')
                  : option}
              </span>
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