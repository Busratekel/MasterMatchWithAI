import React from 'react';
import './ResumePopup.css';

const ResumePopup = ({ onResume, onRestart, mode = 'resume' }) => {
  const isRestartOnly = mode === 'restart_only';

  // "Çıkış" butonu için yönlendirme fonksiyonu
  const handleExitClick = () => {
    window.location.href = 'https://www.doquhome.com.tr/kategori/yastik';
  };

  return (
    <div className="popup-overlay">
      <div className="popup-content">
        <h2 className="popup-title">
          {isRestartOnly ? "Teste Tekrar Başlamak İster misiniz?" : "Kaldığınız Yerden Devam Edin"}
        </h2>
        <p className="popup-text">
          {isRestartOnly 
            ? "Sonuçları görüntülediniz. Dilerseniz testi yeniden başlatabilir veya ana sayfaya dönebilirsiniz." 
            : "Görünüşe göre yarım kalmış bir testiniz var. Testinize devam edebilir veya yeniden başlayabilirsiniz."
          }
        </p>
        <div className="popup-buttons">
          {isRestartOnly ? (
            <>
              {/* "restart_only" modunda gösterilecek butonlar */}
              <button className="btn btn-secondary" onClick={handleExitClick}>
                Testi Sonlandır
              </button>
              <button className="btn btn-primary" onClick={onRestart}>
                Yeniden Başla
              </button>
            </>
          ) : (
            <>
              {/* Normal "resume" modunda gösterilecek butonlar */}
              <button className="btn btn-secondary" onClick={onRestart}>
                Yeniden Başla
              </button>
              <button className="btn btn-primary" onClick={onResume}>
                Devam Et
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResumePopup; 