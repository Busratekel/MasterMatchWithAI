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
  switch (qid) {
    case 'uyku_pozisyonu':
      if (answer.includes('Yan')) return 'Yan uyku pozisyonunu tercih edenler için, boyun ve omurga hizasını koruyan destekli yastıklar daha rahat bir uyku sağlar.';
      if (answer.includes('Sırt')) return 'Sırt üstü uyuyanlar için orta yükseklikte yastıklar, baş ve boyun için daha dengeli bir destek sağlar.';
      if (answer.includes('Yüz')) return 'Yüz üstü uyuyanlar için ince ve yumuşak yapıda yastıklar daha konforlu olur.';
      if (answer.includes('Hareketli Uyku Pozisyonu')) return 'Uyku pozisyonu sık sık değişenler için, farklı bölgelere uyum sağlayan esnek yapılı yastıklar ideal bir seçenek olur.';
      break;
    case 'uyku_düzeni':
      if (answer.includes('terleme')) return 'Terleme sorununuz için nefes alabilen, serinletici ve pamuk kumaşlı yastıklar önerilir.';
      if (answer.includes('horlama')) return 'Horlama problemi için nefes almayı kolaylaştıracak yapıda olan yastıklar faydalı olabilir.';
      if (answer.includes('Reflü')) return 'Reflü için baş ve boyun bölgesini hafifçe yükselten yastıklar önerilir.';
      if (answer.includes('Hiçbir problem')) return 'Uyku düzeniniz iyi ise orta sertlikte ve klasik formda yastıklar günlük kullanım için uygundur.';
      break;
    case 'tempo':
      if (answer.includes('Yoğun')) return 'Yoğun tempolu günlerde, stresi azaltan ve basıncı dengeleyen sünger yastıklar tercih edilmelidir.';
      if (answer.includes('orta')) return 'Orta tempolu günlerde, dengeli destek sunan ve rahatlık sağlayan orta sertlikte yastıklar tercih edilmelidir.';
      if (answer.includes('sakin')) return 'Sakin tempolu günlerde, hafif ve nefes alabilir yapıda, konfor odaklı yastıklar tercih edilmelidir.';
      break;
    case 'agri_bolge':
      if (answer.includes('Sadece Bel Ağrısı')) return 'Bel ağrısı yaşamamak için omurga hizasını korumak oldukça önemlidir.';
      if (answer.includes('Sadece Omuz Ağrısı')) return 'Omuz ağrıları, genellikle boyun desteği sağlamayan yastıklar kullanıldığında ortaya çıkan ağrılardır, boyun desteği sağlayan yastık kullanılması ideal bir uyku sağlar.';
      if (answer.includes('Sadece Boyun Ağrısı')) return 'Boyun bölgesine tam destek sağlayan yastık kullanımı, boyun ağrılarının azalmasına yardımcı olur.';
      if (answer.includes('Hepsi')) return 'Hem omurga hizasını, hem de boyun desteğini bir arada sağlamak, rahat bir uyku için oldukça önemlidir.';
      if (answer.includes('Hiçbir ağrı')) return 'Ağrınız bulunmuyorsa orta sertlikte ve klasik formda yastıklar günlük kullanım için uygundur.';
      break;
    
    case 'dogal_malzeme':
      if (answer.includes('Evet')) return 'Alerji/hassasiyet durumunuz için elyaf dolgulu veya visco sünger dolgulu yastıklar önerilir.';
      if (answer.includes('Hayır')) return 'Doğal malzemelere karşı hassasiyetiniz yoksa tüm yastık türlerini kullanabilirsiniz.';
      break;
    case 'ideal_sertlik':
      if (answer.includes('Yumuşak')) return 'Yumuşak yastıklar boyun desteği sağlarken konfor sunar.';
      if (answer.includes('Orta-Sert')) return 'Orta-sert yastıklar denge ile birlikte daha fazla destek sağlar.';
      if (answer.includes('Sert')) return 'Sert yastıklar maksimum boyun desteği sağlar.';
      break;
    case 'yastik_yukseklik':
      if (answer.includes('Alçak')) return 'Alçak yükseklik; yüzüstü uyuyanlar veya ince yastık sevenler için daha uygundur.';
      if (answer.includes('Orta')) return 'Orta yükseklik çoğu kullanıcı için dengeli bir seçimdir; boyun hizasını rahatça korur.';
      if (answer.includes('Yüksek')) return 'Yüksek yükseklik; geniş omuz yapısı olan veya yan uyuyan kullanıcılar için boynu destekler.';
      break;
    case 'sertlik':
      if (answer.includes('Yumuşak')) return 'Yumuşak yataklarda yumuşak yastıklar tercih edilebilir.';
      if (answer.includes('Orta')) return 'Orta sertlikte yataklar için orta sertlikteki yastıklar uygundur.';
      if (answer.includes('Sert')) return 'Sert yataklarda sert yastıklar tercih edilebilir.';
      break;
    default:
      return null;
  }
  return null;
}

// Analizli HTML metni oluşturucu
function generateAnalysisHtml(answers) {
  let html = '<h2>Yastık Analiz Sonuçlarınız</h2>';
  QUESTIONS.filter(q => q.id !== 'bmi_age').forEach(q => {
    const userAnswer = answers && answers[q.id];
    if (!userAnswer) return;
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
    html += `<div style="margin-bottom:18px;">
      <b>${q.question}</b><br>
      <span>Cevabınız: ${answerText}</span><br>
      ${analysis ? `<span style='color:#1976d2;'>${analysis}</span>` : ''}
    </div>`;
  });
  return html;
}

const ResultsReadyPage = ({ logId, answers, onShowResults }) => {
  const [showMailPopup, setShowMailPopup] = useState(false);
  const [wantsMail, setWantsMail] = useState(null); // null: henüz seçilmedi, true: evet, false: hayır
  const [email, setEmail] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [sendError, setSendError] = useState('');
  
  //

  const handleShowResultsClick = async () => {
    // Sonuçları görmeye tıklanınca analizAlindiMi: true gönder
    if (logId) {
      fetch(API_ENDPOINTS.SAVE_MAIL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          logId,
          analizAlindiMi: true
        })
      });
    }
    // Popup'ı kesinlikle aç ve state'i sıfırla
    setWantsMail(null);
    setShowMailPopup(true);
  };

  const handleMailChoice = async (choice) => {
    // Popup açık kalsın ve seçim net olsun
    setShowMailPopup(true);
    setWantsMail(choice);
    
    if (!choice) {
      setShowMailPopup(false);
      onShowResults(); // Sonuçlar sayfasına hemen yönlendir
      // Hayır derse tekrar analizAlindiMi: true gönderme gerek yok, zaten yukarıda gönderildi
    }
  };

  const handleSendMail = async () => {
    setIsSending(true);
    setSendError('');
    // Kullanıcıya süreç başladığını bildir
    try {
      toast.info('Gönderiliyor...', { autoClose: 1500, position: 'top-center' });
    } catch {}
    
    // LogId kontrolü için toast mesajı
    if (!logId) {
      toast.error('Mail Gönderilemedi! Sayfayı yenileyin.', {
        autoClose: 5000,
        position: "top-center"
      });
      setIsSending(false);
      return;
    }
    
    // Email kontrolü
    const cleanedEmailPre = (email || '').trim();
    const emailRegex = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;
    if (!cleanedEmailPre || !emailRegex.test(cleanedEmailPre)) {
      toast.error('Geçerli bir email adresi girin!', {
        autoClose: 5000,
        position: "top-center"
      });
      setIsSending(false);
      return;
    }
    
    try {
      // Gönderim başladı bildirimini sade tut
      const logIdText = logId != null ? String(logId) : '';
      // Bilgilendirme tostu opsiyonel, mesajlı kullan
      // toast.info(`Gönderiliyor... (#${logIdText.slice(-6)})`, { autoClose: 1500, position: 'top-center' });
      
      const analysisHtml = generateAnalysisHtml(answers);
      
      const cleanedEmail = cleanedEmailPre;
      const requestBody = {
        email,
        logId: logId,
        analizAlindiMi: true,
        analysisHtml: analysisHtml
      };
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 saniye timeout (mobil ağlar için daha toleranslı)
      
      const response = await fetch(API_ENDPOINTS.SAVE_MAIL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify({ ...requestBody, email: cleanedEmail }),
        signal: controller.signal,
        cache: 'no-store',
        keepalive: false
      });
      
      clearTimeout(timeoutId);
      
      const contentType = response.headers.get('content-type') || '';
      if (!response.ok) {
        let serverMsg = '';
        try {
          if (contentType.includes('application/json')) {
            const j = await response.json();
            serverMsg = j.reason ? `${j.error}: ${j.reason}` : (j.error || 'İşlem başarısız');
          } else {
            serverMsg = await response.text();
          }
        } catch {}
        throw new Error(serverMsg || `HTTP ${response.status}`);
      }
      const result = contentType.includes('application/json') ? await response.json() : { success: false };
      
      if (result.success) {
        toast.success('Mailiniz başarıyla gönderildi!', {
          autoClose: 5000,
          position: "top-right"
        });
        // Popup'ı kapat ve sonuçlara hemen git (mobilde takılmayı önlemek için bekleme kaldırıldı)
        setShowMailPopup(false);
        try {
          localStorage.setItem('pillowCurrentPage', 'results');
        } catch {}
        try {
          onShowResults();
        } catch (e) {}
        // Ek güvenlik: 2 sn sonra yine dene (tek seferlik)
        setTimeout(() => {
          try { onShowResults(); } catch {}
        }, 2000);
      } else {
        throw new Error(result.error || 'Mail gönderilemedi.');
      }
    } catch (err) {
      let errorMessage = 'Mail gönderilemedi';
      if (err.name === 'AbortError') {
        errorMessage = 'Mail gönderme zaman aşımına uğradı. Lütfen tekrar deneyin.';
      } else if (err.message.includes('Failed to fetch')) {
        errorMessage = 'Sunucuya bağlanılamadı. İnternet bağlantınızı kontrol edin.';
      } else if (err.message.includes('NetworkError')) {
        errorMessage = 'Ağ hatası. Lütfen tekrar deneyin.';
      } else {
        // Backend reason yakala
        const m = /\{"error":\s*"([^"]+)"(?:,\s*"reason":\s*"([^"]+)")?/i.exec(err.message || '');
        if (m) {
          errorMessage = m[2] ? `${m[1]}: ${m[2]}` : m[1];
        } else {
          errorMessage = `Mail gönderilemedi`;
        }
      }
      setSendError(errorMessage);
      try {
        toast.error(errorMessage, { autoClose: 8000, position: 'top-center' });
      } catch (_) {
        try { alert(errorMessage); } catch (_) {}
      }
    } finally {
      setIsSending(false);
    }
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
          <div className="popup-overlay">
            <div className="popup-content">
              <h2 className="popup-title">Analiz Sonuçlarınızı Mail Olarak Almak İster misiniz?</h2>
              {wantsMail === null && (
                <div className="popup-buttons">
                  <button className="btn btn-primary" onClick={() => handleMailChoice(true)}>Evet</button>
                  <button className="btn btn-secondary" onClick={() => handleMailChoice(false)}>Hayır</button>
                </div>
              )}
              {wantsMail === true && (
                <>
                  <input
                    type="email"
                    className="email-value-box"
                    placeholder="E-posta adresinizi girin"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    style={{ fontSize: '1.2rem', margin: '18px 0', width: '100%'}}
                  />
                  {sendError && (
                    <div style={{ color: '#c62828', marginTop: 4, marginBottom: 8, fontSize: '0.95rem' }}>
                      {sendError}
                    </div>
                  )}
                  <div className="popup-buttons">
                    <button className="btn btn-primary" onClick={handleSendMail} disabled={!email || isSending || !logId}>
                      {isSending ? "Gönderiliyor..." : "Gönder"}
                    </button>
                    <button className="btn btn-secondary" onClick={() => setShowMailPopup(false)} disabled={isSending}>Vazgeç</button>
                  </div>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultsReadyPage; 