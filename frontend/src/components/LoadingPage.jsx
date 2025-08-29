import React, { useRef, useEffect, useState } from 'react';
import './LoadingPage.css';
import loadingVideo from '../assets/loading-video.mp4';
import logo from '../assets/welcomelogo.png';
import dSleepLogo from '../assets/welcomelogo.png';

const LoadingPage = React.forwardRef((props, ref) => {
  const videoRef = useRef();
  const [isMuted, setIsMuted] = useState(true); // Autoplay için sessiz başla
  const [isPlaying, setIsPlaying] = useState(true); // Autoplay açık
  const [showStatus, setShowStatus] = useState(false);
  const [statusText, setStatusText] = useState('');

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.muted = isMuted;
      videoRef.current.defaultMuted = true;
      videoRef.current.playsInline = true;
      videoRef.current.setAttribute('muted', '');
      videoRef.current.setAttribute('playsinline', '');
      videoRef.current.volume = isMuted ? 0 : 1.0;
    }
  }, [isMuted]);

  useEffect(() => {
    if (videoRef.current) {
      if (isPlaying) {
        try {
          const p = videoRef.current.play();
          if (p && typeof p.then === 'function') p.catch(() => {});
        } catch (_) {}
      } else {
        videoRef.current.pause();
      }
    }
  }, [isPlaying]);

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

  const handlePlayToggle = () => {
    setIsPlaying((prev) => {
      const newPlaying = !prev;
      setStatusText(newPlaying ? 'Video Oynatılıyor' : 'Video Duraklatıldı');
      setShowStatus(true);
      setTimeout(() => setShowStatus(false), 1200);
      return newPlaying;
    });
  };

  return (
      <div className="loading-page loading-centered">
        <div className="loading-container">
          <div className="loading-left">
            <img src={logo} alt="Logo" className="loading-logo" />
            <div className="loading-text">
              Size en uygun yastığı buluyoruz...
            </div>
          </div>
          <div className="loading-right">
              <video
                className="loading-video pointer-cursor"
                src={loadingVideo}
                autoPlay
                muted={isMuted}
                playsInline
                ref={videoRef}
                onClick={handleSoundToggle}
                preload="auto"
              ></video>
              <button className={`loading-video-play-toggle ${isPlaying ? 'playing' : 'paused'}`} onClick={handlePlayToggle} tabIndex={-1} aria-label="Video Oynat/Duraklat">
                {isPlaying ? <span role="img" aria-label="Duraklat">⏸️</span> : <span role="img" aria-label="Oynat">▶️</span>}
              </button>
              <button className={`loading-video-sound-toggle ${isMuted ? 'muted' : 'unmuted'}`} onClick={handleSoundToggle} tabIndex={-1} aria-label="Sesi Aç/Kapat">
                {isMuted ? <span role="img" aria-label="Ses Kapalı">🔇</span> : <span role="img" aria-label="Ses Açık">🔊</span>}
              </button>
              <div className="loading-video-overlay-text">
                {isMuted ? '🔇 Ses Kapalı' : '🔊 Ses Açık'}
                <br />
                {isPlaying ? '⏸️ Video Oynatılıyor' : '▶️ Video Duraklatıldı'}
              </div>
              {showStatus && (
                <div className="loading-video-status-popup">{statusText}</div>
              )}
              <div className="loading-video-author-text">Fzt.Teoman GÜNDÜZ</div>
            </div>
          </div>
        </div>
  );
});

export default LoadingPage; 