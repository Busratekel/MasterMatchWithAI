import React, { useState, useEffect, useCallback, useRef } from 'react';
import './App.css';
import WelcomePage from './components/WelcomePage';
import StepperForm from './components/StepperForm';
import LoadingPage from './components/LoadingPage';
import ResultsReadyPage from './components/ResultsReadyPage';
import ResultsPage from './components/ResultsPage';
import ResumePopup from './components/ResumePopup';
import KvkkPdfModal from './components/KvkkPdfModal';
import { API_ENDPOINTS } from './config';
import { ToastContainer } from 'react-toastify';
import splashImage from './assets/splash.png';

// --- KONFİGÜRASYON ---

function App() {
  const [kvkkApproved, setKvkkApproved] = useState(false);
  const [consent, setConsent] = useState('');
  const [questions, setQuestions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [questionError, setQuestionError] = useState(null);
  const [currentPage, setCurrentPage] = useState('splash');
  const [showResumePopup, setShowResumePopup] = useState(false);
  const [popupMode, setPopupMode] = useState('resume'); // 'resume' veya 'restart_only'

  // --- Sonuçlara geçişi yöneten sağlam state ---
  const [apiResult, setApiResult] = useState(null);
  const [isVideoTimerFinished, setIsVideoTimerFinished] = useState(false);

  const [answers, setAnswers] = useState({});
  const [currentStep, setCurrentStep] = useState(0);
  const [answeredSteps, setAnsweredSteps] = useState([]);
  
  // KVKK ve modal state'leri
  const [showKvkkModal, setShowKvkkModal] = useState(false);
  const [kvkkMetinId, setKvkkMetinId] = useState(null);
  const [logId, setLogId] = useState(() => {
    // Uygulama ilk açıldığında localStorage'dan logId'yi yükle
    return localStorage.getItem('pillowLogId') || null;
  });

  // Video ref
  const videoRef = useRef(null);
  
  // Uygulama başlarken localStorage'dan yükleme için tek etki (24 saat kontrolü ile)
  useEffect(() => {
    try {
      const savedPage = localStorage.getItem('pillowCurrentPage');
      const savedAnswers = JSON.parse(localStorage.getItem('pillowAnswers') || '{}');
      const savedExpiryTime = localStorage.getItem('pillowExpiryTime');
      
      // 24 saat geçmiş mi kontrol et
      if (savedExpiryTime && Date.now() > parseInt(savedExpiryTime)) {
        // Süre geçmiş, localStorage'ı temizle
        localStorage.removeItem('pillowCurrentPage');
        localStorage.removeItem('pillowAnswers');
        localStorage.removeItem('pillowCurrentStep');
        localStorage.removeItem('pillowAnsweredSteps');
        localStorage.removeItem('pillowExpiryTime');
        return; // Hiçbir şey yükleme
      }
      
      if (savedPage && Object.keys(savedAnswers).length > 0) {
        // Test devam ederken (loading) veya sonuçlar sayfasındayken sayfa yenilenirse...
        if (savedPage === 'loading' || savedPage === 'results') {
          setAnswers(savedAnswers);
          // Eğer sonuçlar sayfasındaysa, popup'ı "sadece yeniden başlat" modunda aç
          if (savedPage === 'results') {
            setPopupMode('restart_only');
          } else {
            setPopupMode('resume');
          }
          setShowResumePopup(true);
        } else {
          // Diğer sayfalarda durumu normal şekilde yükle
          const savedCurrentStep = parseInt(localStorage.getItem('pillowCurrentStep'), 10);
          const savedAnsweredSteps = JSON.parse(localStorage.getItem('pillowAnsweredSteps') || '[]');
          setCurrentPage(savedPage);
          setAnswers(savedAnswers);
          if (!isNaN(savedCurrentStep)) setCurrentStep(savedCurrentStep);
          setAnsweredSteps(savedAnsweredSteps);
        }
      } else {
        // Kayıtlı durum yoksa splash ekranından 4 saniye sonra welcome'a geç
        setCurrentPage('splash');
        setTimeout(() => {
          setCurrentPage('welcome');
        }, 4000);
      }
    } catch (error) {
      handleRestart();
    }
  }, []); // Sadece ilk yüklemede bir kez çalışır

  // Soruları getiren fonksiyon
  const fetchQuestions = useCallback(async () => {
    setIsLoading(true);
    setQuestionError(null);
    try {
      // Önce API health kontrolü yap
      const healthResponse = await fetch(API_ENDPOINTS.HEALTH);
      if (!healthResponse.ok) {
        setQuestionError('API bağlantısı kurulamadı. Lütfen daha sonra tekrar deneyin.');
        return;
      }

      const response = await fetch(API_ENDPOINTS.QUESTIONS);
      if (response.ok) {
        const data = await response.json();
        setQuestions(data.questions || []);
      } else {
        setQuestionError('Sorular yüklenemedi. Lütfen sayfayı yenileyin.');
      }
    } catch (error) {
      setQuestionError('Bağlantı hatası. Lütfen internet bağlantınızı kontrol edin.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Soruları yükle
  useEffect(() => {
    fetchQuestions();
  }, [fetchQuestions]);

  // localStorage'a durumu kaydeden yardımcı fonksiyon (24 saat sonra otomatik silinir)
  const saveStateToStorage = useCallback(() => {
    try {
      const expiryTime = Date.now() + (24 * 60 * 60 * 1000); // 24 saat sonra
      localStorage.setItem('pillowCurrentPage', currentPage);
      localStorage.setItem('pillowAnswers', JSON.stringify(answers));
      localStorage.setItem('pillowCurrentStep', currentStep.toString());
      localStorage.setItem('pillowAnsweredSteps', JSON.stringify(answeredSteps));
      localStorage.setItem('pillowExpiryTime', expiryTime.toString());
    } catch (error) {
    }
  }, [currentPage, answers, currentStep, answeredSteps]);

  // Durum değiştiğinde localStorage'a kaydet, ancak sadece welcome/splash sayfasında değilsek veya cevaplar varsa
  useEffect(() => {
    if ((currentPage !== 'welcome' && currentPage !== 'splash') || Object.keys(answers).length > 0) {
      saveStateToStorage();
    }
  }, [currentPage, answers, saveStateToStorage]);

  const handleStartTest = () => {
    // localStorage'ı tamamen temizle
    try {
      localStorage.removeItem('pillowCurrentPage');
      localStorage.removeItem('pillowAnswers');
      localStorage.removeItem('pillowCurrentStep');
      localStorage.removeItem('pillowAnsweredSteps');
      localStorage.removeItem('pillowExpiryTime');
    } catch (error) {
    }
    // Sonra durumu sıfırla
    setAnswers({});
    setCurrentStep(0);
    setAnsweredSteps([]);
    setCurrentPage('stepper');
  };

  const handleCompleteTest = useCallback(async (finalAnswers) => {
    setCurrentPage('loading');
    setApiResult(null);
    setIsVideoTimerFinished(false);
    try {
      const response = await fetch(API_ENDPOINTS.RECOMMEND, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ responses: finalAnswers }),
      });
      if (response.ok) {
        const result = await response.json();
        setApiResult(result);
        setLogId(result.log_id);
        if (result.log_id) {
          localStorage.setItem('pillowLogId', result.log_id);
        }
        if (result.log_id && kvkkMetinId) {
          await fetch(API_ENDPOINTS.KVKK_ONAY_EKLE, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              log_id: result.log_id,
              kvkk_metin_id: kvkkMetinId,
              onay_durumu: true,
              onay_yontemi: 'popup'
            })
          });
        }
      } else {
        alert('Öneriler alınamadı. Lütfen tekrar deneyin.');
        setCurrentPage('stepper');
      }
    } catch (error) {
      alert('Bağlantı hatası. Lütfen tekrar deneyin.');
      setCurrentPage('stepper');
    }
  }, [kvkkMetinId]);

  // logId ve currentPage değişimini izleyerek otomatik geçiş
  useEffect(() => {
    if (logId && currentPage === 'loading' && isVideoTimerFinished) {
      setCurrentPage('resultsReady');
    }
  }, [logId, currentPage, isVideoTimerFinished]);
  
  const handleShowResults = () => {
    setCurrentPage('results');
  };
  
  const handleRestart = () => {
    setShowResumePopup(false);
    setPopupMode('resume'); // Modu sıfırla
    setAnswers({});
    setCurrentStep(0);
    setAnsweredSteps([]);
    setCurrentPage('welcome');
    setConsent(''); // Onay kutusunu sıfırla
    setKvkkApproved(false); // KVKK onayını sıfırla
    setLogId(null); // logId'yi sıfırla
    // localStorage'ı tamamen temizle
    try {
      localStorage.clear(); // Tüm localStorage'ı temizle (expiry time dahil)
    } catch (error) {
    }
  };

  const handleResume = () => {
    setShowResumePopup(false);
    handleCompleteTest(answers); 
  };
  
  // Modal onay fonksiyonu
  const handleKvkkApprove = () => {
    setKvkkApproved(true);
    setConsent('accepted');
    setShowKvkkModal(false);
  };
  
  // Video yüklendiğinde yüklenme ekranını kapat
  const handleLoadingFinished = () => {
    if (currentPage === 'loading') {
      setIsVideoTimerFinished(true);
    }
  };

  useEffect(() => {
  }, [currentPage]);
  
  const renderPage = () => {
    if (showResumePopup) {
      return <ResumePopup onResume={handleResume} onRestart={handleRestart} mode={popupMode} />;
    }
    switch (currentPage) {
      case 'splash':
        return (
            <img src={splashImage} alt="Splash" style={{ maxWidth: '85vw', maxHeight: '85vh', objectFit: 'contain' }} />
        );
      case 'welcome':
        return (
          <WelcomePage
            onStart={handleStartTest}
            isLoading={isLoading}
            error={questionError}
            onRetry={fetchQuestions}
            showKvkkModal={showKvkkModal}
            setShowKvkkModal={setShowKvkkModal}
            consent={consent}
            setConsent={setConsent}
            kvkkApproved={kvkkApproved}
            setKvkkApproved={setKvkkApproved}
            kvkkMetinId={kvkkMetinId}
            setKvkkMetinId={setKvkkMetinId}
          />
        );
      case 'stepper':
        if (questions.length === 0) {
          return <LoadingPage ref={videoRef} />;
        }
        return (
          <StepperForm 
            questions={questions}
            answers={answers}
            setAnswers={setAnswers}
            currentStep={currentStep}
            setCurrentStep={setCurrentStep}
            answeredSteps={answeredSteps}
            setAnsweredSteps={setAnsweredSteps}
            onComplete={() => handleCompleteTest(answers)}
            onRestart={handleRestart}
          />
        );
      case 'loading':
        return <LoadingPage onLoadingFinished={handleLoadingFinished} ref={videoRef} />;
      case 'resultsReady':
        // Önce state'ten, yoksa localStorage'dan al
        const safeLogId = logId || localStorage.getItem('pillowLogId');
        console.log("ResultsReadyPage'e gelen logId:", safeLogId);
        return (
          <ResultsReadyPage
            onShowResults={handleShowResults}
            answers={answers}
            logId={safeLogId}
          />
        );
      case 'results':
        return (
          <ResultsPage recommendation={apiResult} onRestart={handleRestart} logId={apiResult && apiResult.log_id} answers={answers} />
        );
      default:
        return (
          <WelcomePage
            onStart={handleStartTest}
            isLoading={isLoading}
            error={questionError}
            onRetry={fetchQuestions}
            showKvkkModal={showKvkkModal}
            setShowKvkkModal={setShowKvkkModal}
            consent={consent}
            setConsent={setConsent}
            kvkkApproved={kvkkApproved}
            setKvkkApproved={setKvkkApproved}
            kvkkMetinId={kvkkMetinId}
            setKvkkMetinId={setKvkkMetinId}
          />
        );
    }
  };

  return (
    <div className="App">
      <ToastContainer 
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
      />
      {renderPage()}
      {showKvkkModal && (
        <KvkkPdfModal 
          onClose={() => setShowKvkkModal(false)}
          onApprove={handleKvkkApprove}
          onDecline={() => { setConsent('declined'); setKvkkApproved(false); }}
          logId={apiResult && apiResult.log_id}
          kvkkMetinId={kvkkMetinId}
        />
      )}
    </div>
  );
}

export default App; 