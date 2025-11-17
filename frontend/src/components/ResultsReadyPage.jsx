import React, { useState } from 'react';
import './ResultsReadyPage.css';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { API_ENDPOINTS } from '../config';
import logo from '../assets/welcomelogo.png';

// Soru ve analiz eşleştirmeleri
const QUESTIONS = [
  {
    id: 'bmi_age',
    question: 'Yaşınızı, boyunuzu ve kilonuzu belirtiniz.',
    info: 'Yaş, boy ve kilo gibi fiziksel bilgiler; ideal yastık yüksekliği ve destek düzeyini belirlememize yardımcı olur. Bu bilgiler yalnızca daha doğru bir öneri sunmak amacıyla kullanılacaktır.'
  },
  {
    id: 'uyku_pozisyonu',
    question: 'Sizin için en rahat uyku pozisyonunu seçer misiniz?',
    info: 'Uyku pozisyonu, boyun ve omurga sağlığınızı doğrudan etkiler. Doğru yastık, uyku tarzınıza uyum sağlamalıdır.'
  },
  {
    id: 'uyku_düzeni',
    question: 'Uyku düzeniniz genellikle nasıldır?',
    info: 'Terleme sorunu için özel yastıklar mevcuttur.'
  },
  {
    id: 'tempo',
    question: 'Günlük yaşam temponuzu nasıl tanımlarsınız?',
    info: 'Yoğun tempolu yaşamda vücut daha fazla destek ve dinlenmeye ihtiyaç duyar. Doğru yastık, günün yorgunluğunu hafifletir.'
  },
  {
    id: 'agri_bolge',
    question: 'Sabahları belirli bir bölgede ağrı hissediyor musunuz?',
    info: 'Boyun, omuz veya bel ağrısı; yanlış yastık seçiminden kaynaklanıyor olabilir. Vücudunuzu dinleyin, ihtiyacınıza uygun yastığı seçin.'
  },
      {
      id: 'dogal_malzeme',
      question: 'Doğal malzemelere (kaz tüyü,yün,bambupamuk gibi) karşı alerjiniz veya hassasiyetiniz var mı ?',
      info: 'Bazı kişiler doğal dolgu malzemelerine (kaz tüyü,yün,bambu,pamuk gibi) karşı alerjik reaksiyon veya hassasiyet gösterebilir. Bu kişiler için, elyaf dolgulu veya visco sünger dolgulu ürünlerin kullanımı daha sağlıklı ve konforlu bir tercih olabilir.'
    },
      {
      id: 'ideal_sertlik',
      question: 'Sizin için ideal yastık sertliği nedir?',
      info: 'Yastık sertliği, baş ve boynunuza ne kadar destek verdiğini belirler. Yumuşak yastıklar daha çok batarken, sert yastıklar daha sıkı bir yapı sunar. Konforunuz için size en uygun olanı seçin.'
    },
  {
    id: 'sertlik',
    question: 'Yatak sertlik derecenizi belirtir misiniz?',
    info: 'Yatak sertliği, yastığın yüksekliği ve dolgunluğu ile uyumlu olmalı. Uyumlu ikili, daha sağlıklı bir uyku sağlar.'
  }
];

// Cevaba göre analiz metni döndüren fonksiyon
function getAnswerAnalysis(qid, answer) {
  if (!answer) return null;

  const answerStr = (() => {
    if (Array.isArray(answer)) return answer.join(', ');
    if (typeof answer === 'object' && answer !== null) {
      try {
        return Object.entries(answer).map(([k, v]) => `${k}: ${v}`).join(', ');
      } catch (_) {
        return JSON.stringify(answer);
      }
    }
    return String(answer);
  })();

  switch (qid) {
    case 'uyku_pozisyonu':
      if (answerStr.includes('Yan')) return 'Yan uyku pozisyonunu tercih edenler için, boyun ve omurga hizasını koruyan destekli yastıklar daha rahat bir uyku sağlar.';
      if (answerStr.includes('Sırt')) return 'Sırt üstü uyuyanlar için orta yükseklikte yastıklar, baş ve boyun için daha dengeli bir destek sağlar.';
      if (answerStr.includes('Yüz')) return 'Yüz üstü uyuyanlar için ince ve yumuşak yapıda yastıklar daha konforlu olur.';
      if (answerStr.includes('Hareketli Uyku Pozisyonu')) return 'Uyku pozisyonu sık sık değişenler için, farklı bölgelere uyum sağlayan esnek yapılı yastıklar ideal bir seçenek olur.';
      break;
    case 'uyku_düzeni':
      if (answerStr.toLowerCase().includes('terleme')) return 'Terleme sorununuz için nefes alabilen, serinletici ve pamuk kumaşlı yastıklar önerilir.';
      if (answerStr.toLowerCase().includes('horlama')) return 'Horlama problemi için nefes almayı kolaylaştıracak yapıda olan yastıklar faydalı olabilir.';
      if (answerStr.includes('Reflü')) return 'Reflü için baş ve boyun bölgesini hafifçe yükselten yastıklar önerilir.';
      if (answerStr.includes('Hiçbir problem')) return 'Uyku düzeniniz iyi ise orta sertlikte ve klasik formda yastıklar günlük kullanım için uygundur.';
      break;
    case 'tempo':
      if (answerStr.includes('Yoğun')) return 'Yoğun tempolu günlerde, stresi azaltan ve basıncı dengeleyen sünger yastıklar tercih edilmelidir.';
      if (answerStr.toLowerCase().includes('orta')) return 'Orta tempolu günlerde, dengeli destek sunan ve rahatlık sağlayan orta sertlikte yastıklar tercih edilmelidir.';
      if (answerStr.toLowerCase().includes('sakin')) return 'Sakin tempolu günlerde, hafif ve nefes alabilir yapıda, konfor odaklı yastıklar tercih edilmelidir.';
      break;
    case 'agri_bolge':
      const selected = Array.isArray(answer) ? answer : [answerStr];
      const normalize = (text) => (text || '').toLowerCase();
      const hasBel = selected.some(opt => normalize(opt).includes('bel'));
      const hasOmuz = selected.some(opt => normalize(opt).includes('omuz'));
      const hasBoyun = selected.some(opt => normalize(opt).includes('boyun'));
      const hasNone = selected.some(opt => normalize(opt).includes('hiçbir'));
      const hasAll = hasBel && hasOmuz && hasBoyun;

      if (hasAll) {
        return 'Bel ağrısı yaşamamak için omurga hizasını korumak oldukça önemlidir. Omuz ağrıları, genellikle boyun desteği sağlamayan yastıklar kullanıldığında ortaya çıkan ağrılardır, boyun desteği sağlayan yastık kullanılması ideal bir uyku sağlar. Boyun bölgesine tam destek sağlayan yastık kullanımı, boyun ağrılarının azalmasına yardımcı olur. Hem omurga hizasını, hem de boyun desteğini bir arada sağlamak, rahat bir uyku için oldukça önemlidir.';
      }
      if (hasBel) return 'Bel ağrısı yaşamamak için omurga hizasını korumak oldukça önemlidir.';
      if (hasOmuz) return 'Omuz ağrıları, genellikle boyun desteği sağlamayan yastıklar kullanıldığında ortaya çıkan ağrılardır, boyun desteği sağlayan yastık kullanılması ideal bir uyku sağlar.';
      if (hasBoyun) return 'Boyun bölgesine tam destek sağlayan yastık kullanımı, boyun ağrılarının azalmasına yardımcı olur.';
      if (hasNone || answerStr.includes('Hiçbir ağrı')) return 'Ağrınız bulunmuyorsa orta sertlikte ve klasik formda yastıklar günlük kullanım için uygundur.';
      break;
    
    case 'dogal_malzeme':
      if (answerStr.includes('Evet')) return 'Alerji/hassasiyet durumunuz için elyaf dolgulu veya visco sünger dolgulu yastıklar önerilir.';
      if (answerStr.includes('Hayır')) return 'Doğal malzemelere karşı hassasiyetiniz yoksa tüm yastık türlerini kullanabilirsiniz.';
      break;
    case 'ideal_sertlik':
      if (answerStr.includes('Yumuşak')) return 'Yumuşak yastıklar boyun desteği sağlarken konfor sunar.';
      if (answerStr.includes('Orta-Sert')) return 'Orta-sert yastıklar denge ile birlikte daha fazla destek sağlar.';
      if (answerStr.includes('Sert')) return 'Sert yastıklar maksimum boyun desteği sağlar.';
      break;
    case 'yastik_yukseklik':
      if (answerStr.includes('Alçak')) return 'Alçak yükseklik; yüzüstü uyuyanlar veya ince yastık sevenler için daha uygundur.';
      if (answerStr.includes('Orta')) return 'Orta yükseklik çoğu kullanıcı için dengeli bir seçimdir; boyun hizasını rahatça korur.';
      if (answerStr.includes('Yüksek')) return 'Yüksek yükseklik; geniş omuz yapısı olan veya yan uyuyan kullanıcılar için boynu destekler.';
      break;
    case 'sertlik':
      if (answerStr.includes('Yumuşak')) return 'Yumuşak yataklarda yumuşak yastıklar tercih edilebilir.';
      if (answerStr.includes('Orta')) return 'Orta sertlikte yataklar için orta sertlikteki yastıklar uygundur.';
      if (answerStr.includes('Sert')) return 'Sert yataklarda sert yastıklar tercih edilebilir.';
      break;
    default:
      return null;
  }
  return null;
}

function formatAnswerForDisplay(value, questionId) {
  if (Array.isArray(value)) {
    if (questionId === 'agri_bolge') {
      const normalize = (text = '') => text.toLowerCase();
      const hasBel = value.some(opt => normalize(opt).includes('bel'));
      const hasOmuz = value.some(opt => normalize(opt).includes('omuz'));
      const hasBoyun = value.some(opt => normalize(opt).includes('boyun'));
      if (hasBel && hasOmuz && hasBoyun) {
        return 'Hepsi';
      }
    }
    return value.join(', ');
  }
  if (typeof value === 'object' && value !== null) {
    try {
      return Object.entries(value).map(([k, v]) => `${k}: ${v}`).join(', ');
    } catch (_) {
      return JSON.stringify(value);
    }
  }
  if (value === undefined || value === null) return '';
  return String(value);
}

// Analizli HTML metni oluşturucu
function generateAnalysisHtml(answers) {
  let html = '<h2>Yastık Analiz Sonuçlarınız</h2>';
  QUESTIONS.filter(q => q.id !== 'bmi_age').forEach(q => {
    const userAnswer = answers && answers[q.id];
    if (!userAnswer) return;
    const answerText = formatAnswerForDisplay(userAnswer, q.id);
    const analysis = getAnswerAnalysis(q.id, userAnswer);
    html += `<div style="margin-bottom:18px;">
      <b>${q.question}</b><br>
      <span>Cevabınız: ${answerText}</span><br>
      ${analysis ? `<span style='color:#1976d2;'>${analysis}</span>` : ''}
    </div>`;
  });
  return html;
}

const ResultsReadyPage = ({ logId, answers, onShowResults, recommendation }) => {
  const [showMailPopup, setShowMailPopup] = useState(false);
  const [email, setEmail] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [sendError, setSendError] = useState('');

  const handleShowResultsClick = async () => {
    // Sonuçları görmeye tıklanınca analizAlindiMi: true gönder
    // VE önerilen yastıkları kaydet
    if (logId) {
      // Önerilen yastık isimlerini al
      let pillowNames = [];
      if (recommendation && recommendation.recommendation && Array.isArray(recommendation.recommendation)) {
        pillowNames = recommendation.recommendation.map(pillow => pillow.isim || pillow.name).filter(Boolean);
      }
      
      fetch(API_ENDPOINTS.SAVE_MAIL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          logId,
          analizAlindiMi: true,
          onerilen_yastiklar: pillowNames.length > 0 ? JSON.stringify(pillowNames) : null
        })
      });
    }
    // Direkt mail popup'ını aç
    setShowMailPopup(true);
  };

  const handleSendMail = async () => {
    // 1. Frontend format kontrolü
    const cleanedEmailPre = (email || '').trim();
    const emailRegex = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;
    if (!cleanedEmailPre || !emailRegex.test(cleanedEmailPre)) {
      toast.error('Lütfen geçerli bir e-posta adresi girin!', {
        autoClose: 5000,
        position: "top-center",
        style: { zIndex: 1001 } // Popup'tan yüksek
      });
      return; // Popup AÇIK KALSIN
    }
    
    if (!logId) {
      toast.error('Mail Gönderilemedi! Sayfayı yenileyin.', {
        autoClose: 5000,
        position: "top-center",
        style: { zIndex: 1001 } // Popup'tan yüksek
      });
      return; // Popup AÇIK KALSIN
    }
    
    // 2. Loading durumu göster
    setIsSending(true);
    setSendError('');
    
    // 3. Backend'e domain kontrolü için gönder
    const analysisHtml = generateAnalysisHtml(answers);
    const cleanedEmail = cleanedEmailPre;
    
    // Önerilen yastık isimlerini al
    let pillowNames = [];
    if (recommendation && recommendation.recommendation && Array.isArray(recommendation.recommendation)) {
      pillowNames = recommendation.recommendation.map(pillow => pillow.isim || pillow.name).filter(Boolean);
    }
    
    const requestBody = {
      email: cleanedEmail,
      logId: logId,
      analizAlindiMi: true,
      analysisHtml: analysisHtml,
      onerilen_yastiklar: pillowNames.length > 0 ? JSON.stringify(pillowNames) : null
    };
    
    try {
      const response = await fetch(API_ENDPOINTS.SAVE_MAIL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(requestBody),
        cache: 'no-store'
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        let errorData;
        try {
          errorData = JSON.parse(errorText);
        } catch {
          throw new Error('Mail gönderilemedi');
        }
        
        // Backend'den hata geldi (domain geçersiz olabilir)
        const errorMessage = errorData.error || 'Mail gönderilemedi';
        setSendError(errorMessage);
        toast.error(errorMessage, {
          autoClose: 5000,
          position: "top-center",
          style: { zIndex: 1001 } // Popup'tan yüksek
        });
        setIsSending(false);
        return; // Popup AÇIK KALSIN, hata göster
      }
      
      const result = await response.json();
      
        if (result.success) {
          // Başarılı! Popup'ı kapat ve sonuçları göster
          setIsSending(false); // Loading durumunu kapat
          setShowMailPopup(false);
          try {
            localStorage.setItem('pillowCurrentPage', 'results');
          } catch {}
          onShowResults();
          
          // Başarı mesajı
          toast.success('Mailiniz başarıyla gönderildi!', {
            autoClose: 4000,
            position: "top-right",
            style: { zIndex: 1001 } // Popup'tan yüksek
          });
        } else {
          throw new Error(result.error || 'Mail gönderilemedi');
        }
    } catch (err) {
      console.error('Mail gönderme hatası:', err);
      const errorMessage = err.message || 'Mail gönderilemedi';
      setSendError(errorMessage);
      toast.error(errorMessage, {
        autoClose: 5000,
        position: "top-center",
        style: { zIndex: 1001 } // Popup'tan yüksek
      });
      setIsSending(false);
      // Popup AÇIK KALSIN
    }
  };

  const handleSkipMail = () => {
    // Popup'ı kapat ve web sitesine yönlendir
    setShowMailPopup(false);
    window.location.href = 'https://www.doquhome.com.tr';
  };

  return (
    <div className="results-page-container">
      <img src={logo} alt="Logo" className="results-logo" />
      <div className="results-page-center">
        <h1 className="results-ready-title">İşte Size Özel Yastık Analiziniz!</h1>
        <button onClick={handleShowResultsClick} className="show-results-button" style={{display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px'}}>
          Sonuçları Göster
          <span className="arrow-animate">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="5" y1="12" x2="19" y2="12"/>
              <polyline points="12 5 19 12 12 19"/>
            </svg>
          </span>
        </button>
        <div className="result-analysis-list">
          {QUESTIONS.filter(q => q.id !== 'bmi_age').map(q => {
            const userAnswer = answers && answers[q.id];
            if (!userAnswer) return null;
            let answerText;
            if (Array.isArray(userAnswer)) {
              answerText = userAnswer.join(', ');
            } else if (typeof userAnswer === 'object' && userAnswer !== null) {
              answerText = Object.entries(userAnswer).map(([k, v]) => `${k}: ${v}`).join(', ');
            } else if (typeof userAnswer === 'string' || typeof userAnswer === 'number') {
              answerText = userAnswer;
            } else {
              answerText = JSON.stringify(userAnswer);
            }
            const analysis = getAnswerAnalysis(q.id, answerText);
            return (
              <div key={q.id} className="result-analysis-item">
                <div className="result-analysis-row">
                  <div className="result-analysis-question"><b>{q.question}</b></div>
                  <div className="result-analysis-answer">
                    {answerText}</div>
                </div>
                {analysis && <div className="result-analysis-comment">{analysis}</div>}
              </div>
            );
          })}
          <button onClick={handleShowResultsClick} className="show-results-button" style={{display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px'}}>
            Sonuçları Göster
            <span className="arrow-animate">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="5" y1="12" x2="19" y2="12"/>
                <polyline points="12 5 19 12 12 19"/>
              </svg>
            </span>
          </button>
        </div>
        {/* Mail popup */}
        {showMailPopup && (
          <div 
            className="popup-overlay"
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0, 0, 0, 0.3)', // Semi-transparent
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1000
            }}
          >
            <div 
              className="popup-content"
              style={{
                backgroundColor: 'white',
                borderRadius: '12px',
                padding: '32px',
                maxWidth: '500px',
                width: '95%',
                boxShadow: '0 10px 30px rgba(0, 0, 0, 0.3)'
              }}
            >
              <h2 className="popup-title">Lütfen Mail Adresinizi Girin</h2>
              <p style={{ fontSize: '0.95rem', color: '#666', marginBottom: '12px' }}>
                Analiz sonuçlarınız e-posta adresinize gönderilecektir.
              </p>
              <input
                type="email"
                className="email-value-box"
                placeholder="ornek@email.com"
                value={email}
                onChange={e => setEmail(e.target.value)}
                onKeyPress={e => {
                  if (e.key === 'Enter' && email && !isSending && logId) {
                    handleSendMail();
                  }
                }}
                style={{ fontSize: '1.2rem', margin: '18px 0', width: '100%'}}
              />
              {sendError && (
                <div style={{ color: '#c62828', marginTop: 4, marginBottom: 8, fontSize: '0.95rem' }}>
                  {sendError}
                </div>
              )}
              <div className="popup-buttons">
                <button 
                  className="btn btn-primary" 
                  onClick={handleSendMail} 
                  disabled={!email || !logId || isSending}
                >
                  {isSending ? 'Gönderiliyor...' : 'Gönder'}
                </button>
                <button className="btn btn-secondary" onClick={handleSkipMail} disabled={isSending}>
                  Vazgeç
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultsReadyPage; 