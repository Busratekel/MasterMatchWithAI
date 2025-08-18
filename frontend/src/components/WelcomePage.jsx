import React, { useRef, useState } from 'react';
import './WelcomePage.css';
import { API_ENDPOINTS } from '../config';
import girisVideo from '../assets/girisekrani.mp4';
import logo from '../assets/welcomelogo.png';

const WelcomePage = ({ onStart, isLoading, error, onRetry, showKvkkModal, setShowKvkkModal, consent, setConsent, kvkkApproved, setKvkkApproved, kvkkMetinId, setKvkkMetinId }) => {
  const videoRef = useRef(null);
  const [isMuted, setIsMuted] = useState(true); // Başlangıçta sessiz
  const [isPlaying, setIsPlaying] = useState(true);
  const [showStatus, setShowStatus] = useState(false);
  const [statusText, setStatusText] = useState('');
  const [isEnded, setIsEnded] = useState(false);

  const handlePlayToggle = () => {
    if (videoRef.current) {
      if (isEnded) {
        videoRef.current.currentTime = 0;
        videoRef.current.play();
        setIsPlaying(true);
        setIsEnded(false);
        setStatusText('Video Oynatılıyor');
      } else {
        if (videoRef.current.paused) {
          videoRef.current.play();
          setIsPlaying(true);
          setStatusText('Video Oynatılıyor');
        } else {
          videoRef.current.pause();
          setIsPlaying(false);
          setStatusText('Video Duraklatıldı');
        }
      }
      setShowStatus(true);
      setTimeout(() => setShowStatus(false), 1200);
    }
  };

  const handleSoundToggle = (e) => {
    e.stopPropagation();
    if (videoRef.current) {
      const newMuted = !videoRef.current.muted;
      videoRef.current.muted = newMuted;
      setIsMuted(newMuted);
      videoRef.current.volume = newMuted ? 0 : 1.0;
      setStatusText(newMuted ? 'Ses Kapalı' : 'Ses Açık');
      setShowStatus(true);
      setTimeout(() => setShowStatus(false), 1200);
    }
  };

  const handleEnded = () => {
    setIsEnded(true);
    setIsPlaying(false);
  };
  
  const handleKvkkClick = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(API_ENDPOINTS.KVKK_METIN);
      const data = await response.json();
      if (data && data.id) {
        setKvkkMetinId(data.id);
        setShowKvkkModal(true);
      } else {
        alert('KVKK metni bulunamadı.');
      }
    } catch (err) {
      alert('KVKK metni yüklenemedi.');
    }
  };

  const handleStart = async () => {
    if (consent === 'accepted' && !isLoading && !error) {
      const logId = await onStart();
      if (logId && kvkkMetinId) {
        await fetch(API_ENDPOINTS.KVKK_ONAY_EKLE, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            log_id: logId,
            kvkk_metin_id: kvkkMetinId,
            onay_durumu: 'kabul',
            onay_yontemi: 'popup'
          })
        });
      }
    }
  };
  
  const renderActionButton = () => {
    if (error) {
      return (
        <div className="action-container">
          <p className="error-message">{error}</p>
          <button className="retry-button" onClick={onRetry} disabled={isLoading}>
            {isLoading ? 'Deneniyor...' : 'Yeniden Dene'}
          </button>
        </div>
      );
    }

    return (
      <div className="action-container">
        <button
          className="start-button"
          onClick={handleStart}
          disabled={consent !== 'accepted' || isLoading}
        >
          Hemen Teste Başlayın!
          <span className="big-animated-arrow">→</span>
        </button>
      </div>
    );
  };

  return (
    <div className="welcome-page-background">
      <div className="welcome-container video-layout">
        <div className="welcome-left">
          <img src={logo} alt="Logo" className="welcome-logo" />
          <p className="description">
            Doğru bir uyku için yapmanız gereken doğru bir seçim...
            <br />
            Yastık seçimi nasıl yapılmalı? 
            <br />
            İyi bir yatak hangi özelliklerde olmalı?
            <br />
            <br />
            İhtiyaçlarınızı anlamak ve size en uygun yatağı önerebilmek 
            <br />
            amacıyla bir test hazırladık. Kişisel vücut datalarınıza göre
            <br />
            cevap vereceğiniz testin sonucunda, cevapları 
            <br />
            değerlendiren algoritmamız 
            <br />
            size en uygun yatağı önerecektir.
            <br />
            <strong>MasterMatch</strong> ile zinde ve rahat bir uyku için lütfen soruları 
            <br />
            eksiksiz ve doğru yanıtlayın.
          </p>
          <div className="kvkk-container">
            Açık rıza metni için<button type="button" className="consent-link" onClick={handleKvkkClick} style={{background: 'none', border: 'none', color: 'inherit', padding: 0, textDecoration: 'underline', cursor: 'pointer'}}>
                tıklayınız.*
            </button>
          </div>
          <div className="consent-options">
            <label>
              <input 
                type="radio" 
                name="consent" 
                value="accepted"
                checked={consent === 'accepted'}
                onClick={() => {
                  if (!kvkkApproved) setShowKvkkModal(true);
                  else setConsent('accepted');
                }}
                readOnly
              />
              Okudum, kabul ediyorum.
            </label>
            <label>
              <input 
                type="radio" 
                name="consent" 
                value="declined"
                checked={consent === 'declined'}
                onChange={(e) => setConsent(e.target.value)} 
              />
              Kabul etmiyorum.
            </label>
          </div>
          {renderActionButton()}
        </div>
        <div className="welcome-video-absolute">
            <video
              ref={videoRef}
              src={girisVideo}
              autoPlay
              muted={isMuted}
              controls={false}
              className="welcome-video pointer-cursor"
              playsInline
              onEnded={handleEnded}
            />
            <button className={`welcome-video-play-toggle ${isPlaying ? 'playing' : 'paused'}`} onClick={handlePlayToggle} tabIndex={-1} aria-label="Video Oynat/Durdur">
              {isPlaying ? <span role="img" aria-label="Duraklat">⏸️</span> : <span role="img" aria-label="Oynat">▶️</span>}
            </button>
            <button className={`welcome-video-sound-toggle ${isMuted ? 'muted' : 'unmuted'}`} onClick={handleSoundToggle} tabIndex={-1} aria-label="Sesi Aç/Kapat">
              {isMuted ? <span role="img" aria-label="Ses Kapalı">🔇</span> : <span role="img" aria-label="Ses Açık">🔊</span>}
            </button>
            <div className="welcome-video-overlay-text">
              {isMuted ? '🔇 Ses Kapalı' : '🔊 Ses Açık'}
              <br />
              {isPlaying ? '⏸️ Video Oynatılıyor' : '▶️ Video Duraklatıldı'}
            </div>
            {showStatus && (
              <div className="welcome-video-status-popup">{statusText}</div>
            )}
            <div className="welcome-video-author-text">Fzt.Teoman GÜNDÜZ</div>
        </div>
        </div>
      </div>
  );
};

export default WelcomePage; 