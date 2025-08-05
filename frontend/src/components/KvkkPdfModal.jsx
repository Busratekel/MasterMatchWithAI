import React, { useEffect, useState } from 'react';
import { pdfjs } from 'react-pdf';
import './ResumePopup.css'; // Popup stillerini tekrar kullanıyoruz
import '../pdf-styles/AnnotationLayer.css';
import '../pdf-styles/TextLayer.css';
import { API_ENDPOINTS } from '../config';

pdfjs.GlobalWorkerOptions.workerSrc = '/pdf.worker.js';

const KvkkPdfModal = ({ onClose, onApprove, logId, kvkkMetinId }) => {
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

  return (
    <div className="popup-overlay" onClick={onClose}>
      <div className="popup-content" style={{ maxWidth: 700, width: '95%', minHeight: 500 }} onClick={e => e.stopPropagation()}>
        <h2 className="popup-title">Açık Rıza Metni</h2>
        <div style={{height: 400, marginBottom: 24, display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#fff', position: 'relative'}}>
          {loadingText ? <div>Yükleniyor...</div> :
            <pre style={{whiteSpace: 'pre-wrap', textAlign: 'left', fontSize: 16, padding: 16, background: 'none', width: '100%', height: '100%', overflow: 'auto'}}>{kvkkText}</pre>
          }
        </div>
        <div className="kvkk-modal-buttons-row">
          <button className="kvkk-approve-button" onClick={handleApprove}>
            Kabul Et
          </button>
          <button className="kvkk-close-button" onClick={onClose}>Reddet</button>
        </div>
      </div>
    </div>
  );
};

export default KvkkPdfModal; 