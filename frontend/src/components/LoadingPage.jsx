import React, { useRef, useEffect, useState } from 'react';
import './LoadingPage.css';
import loadingVideo from '../assets/loading-video.mp4';

const LoadingPage = React.forwardRef((props, ref) => {
  const videoRef = useRef();
  const [isMuted, setIsMuted] = useState(false); // Sesli başlasın
  const [showStatus, setShowStatus] = useState(false);
  const [statusText, setStatusText] = useState('');

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.muted = isMuted;
      videoRef.current.volume = isMuted ? 0 : 1.0;
    }
  }, [isMuted]);

  useEffect(() => {
    // Video bittiğinde otomatik olarak diğer sayfaya geç
    const handleEnded = () => {
      if (props.onLoadingFinished) props.onLoadingFinished();
    };
    const video = videoRef.current;
    if (video) {
      video.addEventListener('ended', handleEnded);
    }
    return () => {
      if (video) video.removeEventListener('ended', handleEnded);
    };
  }, [props.onLoadingFinished]);

  const handleSoundToggle = () => {
    setIsMuted((prev) => {
      const newMuted = !prev;
      setStatusText(newMuted ? 'Ses Kapalı' : 'Ses Açık');
      setShowStatus(true);
      setTimeout(() => setShowStatus(false), 1200);
      return newMuted;
    });
  };

  return (
    <div className="loading-page loading-centered">
      <div className="loading-video-wrapper">
        <video
          className="loading-video pointer-cursor"
          src={loadingVideo}
          autoPlay
          muted={isMuted}
          playsInline
          ref={videoRef}
          style={{ width: '100%', borderRadius: '20px', background: '#000' }}
          onClick={handleSoundToggle}
        ></video>
        <button className={`video-sound-toggle ${isMuted ? 'muted' : 'unmuted'}`} onClick={handleSoundToggle} tabIndex={-1} aria-label="Sesi Aç/Kapat">
          {isMuted ? <span role="img" aria-label="Ses Kapalı">🔇</span> : <span role="img" aria-label="Ses Açık">🔊</span>}
        </button>
        <div className="video-overlay-text">
          {isMuted ? 'Sesi Açmak İçin Videoya veya 🔇 butonuna basın' : 'Sesi Kapatmak İçin Videoya veya 🔊 butonuna basın'}
        </div>
        {showStatus && (
          <div className="video-status-popup">{statusText}</div>
        )}
      </div>
      <div className="loading-text">
        Size en uygun yastığı buluyoruz...
      </div>
    </div>
  );
});

export default LoadingPage; 