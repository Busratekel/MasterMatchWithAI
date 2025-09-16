import React, { useEffect, useRef } from 'react';
import './StepperForm.css';
import StepSidebar from './StepSidebar';
import StepContent from './StepContent';
import InfoPage from './InfoPage';
import LoadingPage from './LoadingPage';

const isMobile = typeof window !== 'undefined' && window.innerWidth <= 700;

const StepperForm = ({
  questions,
  answers,
  setAnswers,
  currentStep,
  setCurrentStep,
  answeredSteps,
  setAnsweredSteps,
  onComplete,
  onRestart,
}) => {
  const [showInfo, setShowInfo] = React.useState(false);
  const [infoText, setInfoText] = React.useState('');
  const infoTimer = useRef(null);
  const contentTopRef = useRef(null);
  
  useEffect(() => {
    // Adım değiştiğinde önceki bilgiyi hemen gizle
    setShowInfo(false);
    clearTimeout(infoTimer.current);

    // 1 saniye sonra yenisini göstermek için zamanlayıcı kur
    infoTimer.current = setTimeout(() => {
      const currentQuestion = questions[currentStep];
      if (currentQuestion && currentQuestion.info) {
        setInfoText(currentQuestion.info);
        setShowInfo(true);
        // 8 saniye sonra otomatik kapansın
        setTimeout(() => {
          setShowInfo(false);
          setInfoText('');
        }, 8000);
      }
    }, 1000); // 1 saniye gecikme

    // Komponentten ayrılınca zamanlayıcıyı temizle
    return () => {
      clearTimeout(infoTimer.current);
    };
  }, [currentStep, questions]);

  // Adım değiştiğinde üst kısma kaydır (mobil ve desktop)
  useEffect(() => {
    // Render tamamlandıktan hemen sonra çalışsın
    const id = requestAnimationFrame(() => {
      try {
        if (contentTopRef.current && typeof contentTopRef.current.scrollTo === 'function') {
          contentTopRef.current.scrollTo({ top: 0, behavior: 'smooth' });
        }
      } catch (_) {}
      try {
        if (typeof window !== 'undefined' && typeof window.scrollTo === 'function') {
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }
      } catch (_) {}
      try {
        const el = document.scrollingElement || document.documentElement || document.body;
        if (el && typeof el.scrollTo === 'function') {
          el.scrollTo({ top: 0, behavior: 'smooth' });
        }
      } catch (_) {}
    });
    return () => cancelAnimationFrame(id);
  }, [currentStep]);
  
  const handleAnswerChange = React.useCallback((questionId, clickedOption) => {
    let newAnswers = { ...answers };

    const question = questions.find(q => q.id === questionId);
    // Eğer checkbox tipi ve array geliyorsa, direkt kaydet
    if (question && question.type === 'checkbox' && Array.isArray(clickedOption)) {
      newAnswers[questionId] = clickedOption;
      setAnswers(newAnswers);
      if (!answeredSteps.includes(currentStep)) {
        setAnsweredSteps([...answeredSteps, currentStep]);
      }
      return;
    }

    // Eski mantık (diğer tipler için)
    if (!questions.find(q => q.id === questionId)) {
      newAnswers[questionId] = clickedOption;
      setAnswers(newAnswers);
      return;
    }

    if (question.type !== 'checkbox') {
      if (typeof clickedOption === 'object' && clickedOption !== null && !Array.isArray(clickedOption)) {
        const currentAnswer = newAnswers[questionId] || {};
        const mergedAnswer = { ...currentAnswer, ...clickedOption };
        if (JSON.stringify(currentAnswer) === JSON.stringify(mergedAnswer)) {
          return;
        }
        newAnswers[questionId] = mergedAnswer;
      } else {
        if (newAnswers[questionId] === clickedOption) {
          return;
        }
        newAnswers[questionId] = clickedOption;
      }
    } else {
      const currentSelection = Array.isArray(answers[questionId]) ? answers[questionId] : [];
      let nextSelection = [];
      const normalOptions = question.options.filter(opt => !['Hepsi', 'Hiçbir ağrı hissetmiyorum','Hareketli Uyku Pozisyonu'].includes(opt));

      if (clickedOption === 'Hepsi') {
        const allSelected = normalOptions.length > 0 && normalOptions.every(opt => currentSelection.includes(opt));
        nextSelection = allSelected ? [] : [...normalOptions];
      } else if (clickedOption === 'Hiçbir ağrı hissetmiyorum') {
        nextSelection = currentSelection.includes(clickedOption) ? [] : [clickedOption];
      } else {
        let tempSelection = currentSelection.filter(opt => opt !== 'Hiçbir ağrı hissetmiyorum');
        if (tempSelection.includes(clickedOption)) {
          nextSelection = tempSelection.filter(item => item !== clickedOption);
        } else {
          nextSelection = [...tempSelection, clickedOption];
        }
      }
      if (JSON.stringify(currentSelection.sort()) === JSON.stringify(nextSelection.sort())) {
        return;
      }
      newAnswers[questionId] = nextSelection;
    }

    setAnswers(newAnswers);

    if (!answeredSteps.includes(currentStep)) {
      setAnsweredSteps([...answeredSteps, currentStep]);
    }
  }, [answers, questions, currentStep, answeredSteps, setAnswers, setAnsweredSteps]);
  
  const handleNext = React.useCallback(() => {
    if (currentStep < questions.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  }, [currentStep, questions.length, setCurrentStep]);

  const handlePrevious = React.useCallback(() => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  }, [currentStep, setCurrentStep]);

  const canProceed = React.useMemo(() => {
    if (!questions || questions.length === 0) return false;
    const currentQuestion = questions[currentStep];
    if (!currentQuestion) return false;
    const answer = answers[currentQuestion.id];
    if (currentQuestion.id === 'bmi_age') {
      // Yaş 0-7 ise sadece yaş seçiliyse ilerlenebilsin, 8+ ise hem yaş hem vki gereksin
      if (answer && answer.yas_gercek !== undefined && answer.yas_gercek !== "") {
        if (Number(answer.yas_gercek) <= 7) {
          return true;
        } else {
          return !!answer.vki;
        }
      }
      return false;
    }
    if (currentQuestion.type === 'checkbox') {
      return answer && answer.length > 0;
    }
    return !!answer;
  }, [questions, currentStep, answers]);
  
  const isTestComplete = React.useMemo(() => {
      if (!questions || questions.length === 0) return false;
      return questions.every(q => {
          const answer = answers[q.id];
          if (q.type === 'checkbox') {
              return answer && answer.length > 0;
          }
          return !!answer;
      });
  }, [questions, answers]);

  /*const handleStepClick = React.useCallback((step) => {
    if(answeredSteps.includes(step) || step === currentStep) {
      setCurrentStep(step);
    }
  }, [answeredSteps, currentStep, setCurrentStep]);*/

  const handleCloseInfo = () => {
    clearTimeout(infoTimer.current);
    setShowInfo(false);
  };
  
  if (!questions || questions.length === 0) {
    return <LoadingPage />;
  }

  const currentQuestion = questions[currentStep];

  return (
      <div className="stepper-center-row">
        {!isMobile && (
          <StepSidebar
            questions={questions}
            currentStep={currentStep}
            answeredSteps={answeredSteps}
            answers={answers}
            onStepClick={step => {
              if(answeredSteps.includes(step) || step === currentStep) {
                setCurrentStep(step);
              }
            }}
            onRestart={onRestart}
          />
        )}
        <div className="stepper-content-card" ref={contentTopRef}>
          {currentQuestion ? (
            <StepContent
              question={currentQuestion}
              answer={answers[currentQuestion.id]}
              onAnswerChange={handleAnswerChange}
              answers={answers}
            />
          ) : (
            <div className="all-questions-answered">
              <p>Tüm soruları cevapladınız.</p>
              <p>Sonuçları görmek için lütfen "Testi Tamamla" butonuna tıklayın.</p>
            </div>
          )}
          <div className="form-navigation">
            <div className="form-nav-left">
              <button
                className="btn btn-secondary"
                onClick={handlePrevious}
                disabled={currentStep === 0}
              >
                &lt; GERİ
              </button>
            </div>
            
            {/* Soru göstergeleri */}
            <div className="question-indicators">
              {questions.map((_, index) => (
                <div
                  key={index}
                  className={`question-indicator ${
                    index === currentStep ? 'active' : ''
                  } ${answeredSteps.includes(index) ? 'answered' : ''}`}
                  onClick={() => {
                    if (answeredSteps.includes(index) || index === currentStep) {
                      setCurrentStep(index);
                    }
                  }}
                >
                  {answeredSteps.includes(index) ? '✓' : index + 1}
                </div>
              ))}
            </div>
            
            <div className="form-nav-right">
              {currentStep < questions.length - 1 ? (
                <button
                  className="btn"
                  onClick={handleNext}
                  disabled={!canProceed}
                >
                  İLERİ &gt;
                </button>
              ) : (
                <button
                  className="btn btn-complete"
                  onClick={onComplete}
                  disabled={!isTestComplete}
                >
                  Analizi Tamamla
                </button>
              )}
            </div>
          </div>
          {showInfo && <InfoPage infoText={infoText} onClose={handleCloseInfo} />}
        </div>
      </div>
  );
};

export default StepperForm; 