import React from 'react';
import './ResultsPage.css';
import { API_ENDPOINTS } from '../config';
import dSleepLogo from '../assets/sidebarlogo.png';

const ResultsPage = ({ recommendation, onRestart, logId, answers }) => {
  if (!recommendation) {
    return (
      <div className="results-page-container">
        <div className="results-content">
          <h2 className="results-title">Yükleniyor...</h2>
        </div>
      </div>
    );
  }

  if (!Array.isArray(recommendation.recommendations) || recommendation.recommendations.length === 0) {
    return (
      <div className="results-page-container">
        <div className="results-content">
          <h2 className="results-title">Üzgünüz!</h2>
          <p className="results-subtitle">
            Girdiğiniz kriterlere uygun bir yastık bulunamadı. Lütfen seçiminizi gözden geçirip tekrar deneyin.
          </p>
          <button onClick={onRestart} className="restart-button">
            Teste Tekrar Başla
          </button>
        </div>
      </div>
    );
  }

  // Ürün inceleme logu gönder
  const handleProductView = (urunIsmi) => {
    if (!logId) {
      return;
    }
    fetch(API_ENDPOINTS.LOG_URUN_INCELEME, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ log_id: logId, urun_ismi: urunIsmi })
    })
      .then(res => res.json().then(data => {
      }))
      .catch(err => {
      });
  };

  return (
    <div className="results-page-container">
      <div className="results-header">
        <img src={dSleepLogo} alt="d-Sleep Logo" className="results-logo" />
        <h2 className="results-subtitle">
          Seçimlerinize En Uygun Yastıkları Sizler İçin Listeledik.
        </h2>
      </div>

      <div className="recommendations-list">
        {recommendation.recommendations.map((pillow) => {
          if (!pillow || !pillow.id) return null;

          const pillowName = pillow.isim || "İsimsiz Yastık";
          const imageUrl = pillow.gorsel;
          const productUrl = pillow.link;

          return (
            <div key={pillow.id} className="pillow-card-new">
              <div className="pillow-image-container-new">
                <img
                  src={imageUrl}
                  alt={pillowName}
                  className="pillow-image-new"
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.src = `https://via.placeholder.com/250x250.png?text=Görsel+Yok`;
                  }}
                />
              </div>
              <div className="pillow-info-new">
                <h3 className="pillow-name-new">{pillowName}</h3>
                <a
                  href={productUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="pillow-cta-button"
                  onClick={e => {
                    e.preventDefault();
                    handleProductView(pillowName);
                    window.open(productUrl, '_blank');
                  }}
                >
                  Ürünü İncele
                  <span className="arrow-icon" style={{marginLeft: '8px', display: 'flex', alignItems: 'center'}}>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
                  </span>
                </a>
              </div>
            </div>
          );
        })}
      </div>
      <div className="bottom-buttons-container">
        <button onClick={onRestart} className="pillow-cta-button">
          Teste Tekrar Başla
        </button>
        <button
          onClick={() => window.location.href = "https://www.doquhome.com.tr/"}
          className="pillow-cta-button"
        >
          Testi Sonlandır
        </button>
      </div>
    </div>
  );
};

export default ResultsPage; 