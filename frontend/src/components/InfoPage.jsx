import React from 'react';
import './InfoPage.css';
import infoLogo from '../assets/sidebarlogobig.png'; // Varsa, yoksa başka bir logo kullan

const InfoPage = ({ infoText, onClose }) => {
  return (
    <div className="info-page-container" onClick={e => e.stopPropagation()}>
      <button className="info-close-btn" onClick={onClose} aria-label="Kapat">×</button>
      <div className="info-header">
        <div className="info-logo-container">
          <img src={infoLogo} alt="Bilgi" className="info-logo" />
        </div>
        <div className="info-title">MasterMatch Bilgilendiriyor</div>
      </div>
      <div className="info-body">
        <div className="info-text">{infoText}</div>
      </div>
    </div>
  );
};

export default InfoPage; 