import React from 'react';
import './StepperForm.css';
import dSleepLogo from '../assets/welcomelogo.png';

const StepSidebar = ({ questions, currentStep, answeredSteps, answers, onStepClick, onRestart }) => {

  const isStepAnswered = (stepIndex) => {
    const question = questions[stepIndex];
    if (!question) return false;
    const answer = answers && question && question.id ? answers[question.id] : undefined;
    if (question.type === 'checkbox') {
      return Array.isArray(answer) && answer.length > 0;
    }
    if (question.type === 'bmi_age') {
      return answer && answer.yas_gercek !== undefined && answer.yas_gercek !== "";
    }
    return !!answer;
  };

  return (
    <div className="stepper-sidebar">
                <img src={dSleepLogo} alt="Logo" className="sidebar-logo" />

        {/* Yeni Progress Bar */}
        <div className="new-progress-container">
          <div className="new-progress-bar">
            <div 
              className="new-progress-fill"
              style={{ 
                width: questions.length > 0 ? `${(answeredSteps.length / questions.length) * 100}%` : '0%' 
              }}
            ></div>
          </div>
          <div className="new-progress-text">
            %{questions.length > 0 ? Math.round((answeredSteps.length / questions.length) * 100) : 0}
          </div>
        </div>

        
      
      <div className="sidebar-content">
        <ol className="steps-list-plain">
          {questions.map((q, index) => {
            const isActive = index === currentStep;
            const isClickable = answeredSteps.includes(index) || isActive;
            const isLast = index === questions.length - 1;
            const isAnswered = isStepAnswered(index);
            return (
              <li
                key={q.id}
                className={`step-plain-item${isActive ? ' active' : ''}${isClickable ? '' : ' not-clickable'}${!isLast ? ' with-underline' : ''}`}
                onClick={() => isClickable && onStepClick(index)}
              >
                <span className="step-check-mark-left">
                  {isAnswered ? "✔" : (index + 1).toString().padStart(2, '0')}
                </span>
                <span className="step-plain-text">{q.question}</span>
              </li>
            );
          })}
        </ol>
      </div>

      <div className="sidebar-footer">
        <button className="btn-restart-sidebar" onClick={onRestart}>
          Teste Yeniden Başla
        </button>
      </div>
    </div>
  );
};

export default StepSidebar; 