import React, { useEffect, useState } from 'react';
import { pdfjs } from 'react-pdf';
import './ResumePopup.css'; // Popup stillerini tekrar kullanıyoruz
import '../pdf-styles/AnnotationLayer.css';
import '../pdf-styles/TextLayer.css';
import { API_ENDPOINTS } from '../config';

pdfjs.GlobalWorkerOptions.workerSrc = '/pdf.worker.js';

const KvkkPdfModal = ({ onClose, onApprove, onDecline, logId, kvkkMetinId }) => {
  const [kvkkText, setKvkkText] = useState('');
  const [loadingText, setLoadingText] = useState(false);

  useEffect(() => {
    setLoadingText(true);
    fetch(API_ENDPOINTS.KVKK_METIN)
      .then(res => res.json())
      .then(data => {
        setKvkkText(data.icerik || 'KVKK metni bulunamadı.');
        setLoadingText(false);
      })
      .catch(() => {
        setKvkkText('KVKK metni yüklenemedi.');
        setLoadingText(false);
      });
  }, []);

  const handleApprove = async () => {
    if (logId && kvkkMetinId) {
      await fetch(API_ENDPOINTS.KVKK_ONAY_EKLE, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          log_id: logId,
          kvkk_metin_id: kvkkMetinId,
          onay_durumu: true,
          onay_yontemi: 'popup'
        })
      });
    }
    if (onApprove) onApprove();
    onClose();
  };

  const handleDecline = () => {
    if (onDecline) onDecline();
    onClose();
  };

  return (
    <div className="popup-overlay" onClick={onClose}>
      <div className="popup-content" onClick={e => e.stopPropagation()}>
        <h2 className="popup-title">Açık Rıza Metni</h2>
        <div className="kvkk-scroll">
          {loadingText ? <div>Yükleniyor...</div> :
            <pre className="kvkk-text">{kvkkText}</pre>
          }
        </div>
        <div className="kvkk-modal-buttons-row">
          <button className="kvkk-approve-button" onClick={handleApprove}>
            Kabul Et
          </button>
          <button className="kvkk-close-button" onClick={handleDecline}>Reddet</button>
        </div>
      </div>
    </div>
  );
};

export default KvkkPdfModal; 