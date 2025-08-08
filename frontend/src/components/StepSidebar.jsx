import React from 'react';
import './StepperForm.css';
import dSleepLogo from '../assets/sidebarlogo.png';

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
      <div className="sidebar-header">
        <img src={dSleepLogo} alt="Logo" className="sidebar-logo" />
      </div>

      {/* Progress Bar */}
      <div className="sidebar-progress-bar-container">
        <div
          className="sidebar-progress-bar"
          style={{ width: questions.length > 0 ? `${Math.max((answeredSteps.length / questions.length) * 100, answeredSteps.length > 0 ? 8 : 0)}%` : '0%' }}
        />
      </div>
      {/* Progress Bar Yüzdelik */}
      <div className="sidebar-progress-percent" style={{textAlign: 'center', fontWeight: 700, color: '#1976d2', marginTop: 10, fontSize: 24}}>
        %{questions.length > 0 ? Math.round((answeredSteps.length / questions.length) * 100) : 0}
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
                  {isAnswered ? "✔" : index + 1}
                </span>
                <span className="step-plain-text">{q.question}</span>
              </li>
            );
          })}
        </ol>
      </div>

      <div className="sidebar-footer">
        <button className="btn-restart-sidebar" onClick={onRestart}>
          <span role="img" aria-label="restart">♻️</span>
          Teste Yeniden Başla
        </button>
      </div>
    </div>
  );
};

export default StepSidebar; 