import React, { useState } from 'react';
import './ResultsPage.css';
import { API_ENDPOINTS } from '../config';
import dSleepLogo from '../assets/welcomelogo.png';

const ResultsPage = ({ recommendation, onRestart, logId, answers }) => {
  const [showPerfectMatchModal, setShowPerfectMatchModal] = useState(false);
  const [selectedPillow, setSelectedPillow] = useState(null);

  const handlePerfectMatchClick = (pillowName) => {
    setSelectedPillow(pillowName);
    setShowPerfectMatchModal(true);
  };

  const closePerfectMatchModal = () => {
    setShowPerfectMatchModal(false);
    setSelectedPillow(null);
  };

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

  // Diz Arası Yastık linkini sabitle (kullanıcı isteği)
  const kneePillowUrl = 'https://www.doquhome.com.tr/urun/diz-arasi-yastik-26-x-21-x-16-5-cm-beyaz';

  // Basit Türkçe karakter normalize + kontrol: diz arası / diz arasi / diz arası yastık
  const isKneePillow = (name) => {
    if (!name || typeof name !== 'string') return false;
    const lower = name.toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '');
    // remove punctuation/extra spaces for safety
    const cleaned = lower.replace(/[^a-z0-9\s]/g, ' ').replace(/\s+/g, ' ').trim();
    return cleaned.includes('diz arasi');
  };

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
          // Knee pillow ana listede gösterilmesin
          if (!pillow || !pillow.id || isKneePillow(pillow.isim)) return null;

          const pillowName = pillow.isim || "İsimsiz Yastık";
          const imageUrl = pillow.gorsel;
          const productUrl = pillow.link;

          // Kullanıcının yan üstü uyku pozisyonu seçip seçmediğini kontrol et
          const userSelectedYanUstu = answers && answers.uyku_pozisyonu && 
            (Array.isArray(answers.uyku_pozisyonu) ? 
              answers.uyku_pozisyonu.includes('Yan uyku pozisyonu') : 
              answers.uyku_pozisyonu === 'Yan uyku pozisyonu');

          // Yastığın yan üstü uyku pozisyonuna sahip olup olmadığını kontrol et
          const pillowHasYanUstu = pillow.uyku_pozisyonu && 
            pillow.uyku_pozisyonu.toLowerCase().includes('yan');

          // Mükemmel eşleşme etiketi gösterilecek mi?
          // Kullanıcının seçimi önemli değil, sadece yastığın yan uyku pozisyonuna sahip olup olmadığı önemli
          const showPerfectMatch = pillowHasYanUstu;

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
                {showPerfectMatch && (
                  <div 
                    className="perfect-match-badge clickable"
                    onClick={() => handlePerfectMatchClick(pillowName)}
                    title="Diz arası yastık önerisi için tıklayın"
                  >
                    <span className="star">⭐️</span>
                    Mükemmel Eşleşmeyi Tamamla
                  </div>
                )}
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

      {/* Mükemmel Eşleşme Modal */}
      {showPerfectMatchModal && (
        <div className="perfect-match-modal-overlay" onClick={closePerfectMatchModal}>
          <div className="perfect-match-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Mükemmel Eşleşmeyi Tamamla</h3>
              <button className="modal-close" onClick={closePerfectMatchModal}>×</button>
            </div>
            <div className="modal-content">
              <div className="pillow-suggestion">
                <h4>Seçtiğiniz Yastık: {selectedPillow}</h4>
                <p>Bu yastıkla birlikte kullanmanızı önerdiğimiz ürün ise 'Diz Arası Yastık':</p>
                <div className="diz-arasi-pillow">
                  <img 
                    src="https://www.doquhome.com.tr/idea/kl/05/myassets/products/672/diz-arasi-yastik04.jpg?revision=1751466969"
                    alt="Diz Arası Yastık"
                    onError={(e) => {
                      e.target.onerror = null;
                      e.target.style.display = 'none';
                    }}
                  />
                  <div className="pillow-info">
                    <h5>Diz Arası Yastık</h5>
                    <p>Yan uyku pozisyonunda bacaklarınız arasına yerleştirerek omurga hizasını korur ve daha rahat bir uyku sağlar.</p>
                    <a 
                      href={kneePillowUrl}
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="pillow-cta-button"
                      onClick={() => handleProductView('Diz Arası Yastık')}
                    >
                      Ürünü İncele
                      <span className="arrow-icon" style={{marginLeft: '8px', display: 'flex', alignItems: 'center'}}>
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
                      </span>
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultsPage; 