import React, { useRef, useEffect, useState, useCallback } from 'react';
import './LoadingPage.css';
import loadingVideo from '../assets/loading-video.mp4';
import loadingVideoBaseline from '../assets/loading-video-baseline-audio.mp4';
import logo from '../assets/welcomelogo.png';
import dSleepLogo from '../assets/welcomelogo.png';

const LoadingPage = React.forwardRef((props, ref) => {
  const videoRef = useRef();
  const [isMuted, setIsMuted] = useState(true); // Autoplay'in güvenilir başlaması için sessiz başla
  const [isPlaying, setIsPlaying] = useState(true); // Sayfa açılır açılmaz play() denensin
  const [showStatus, setShowStatus] = useState(false);
  const [statusText, setStatusText] = useState('');
  const [videoDurationMs, setVideoDurationMs] = useState(0);
  const fallbackTimerRef = useRef(null);
  const [hasTerminated, setHasTerminated] = useState(false);
  const timerStartTimeRef = useRef(null);
  const timerRemainingMsRef = useRef(null);

  const clearFallbackTimer = useCallback(() => {
    if (fallbackTimerRef.current) {
      clearTimeout(fallbackTimerRef.current);
      fallbackTimerRef.current = null;
    }
    timerStartTimeRef.current = null;
    timerRemainingMsRef.current = null;
  }, []);

  const finishLoading = useCallback(() => {
    setHasTerminated((prev) => {
      if (prev) return prev;
      clearFallbackTimer();
      try {
        if (props.onLoadingFinished) props.onLoadingFinished();
      } catch (_) {}
      return true;
    });
  }, [clearFallbackTimer, props.onLoadingFinished]);

  const scheduleFallbackTimer = useCallback((ms) => {
    clearFallbackTimer();
    timerRemainingMsRef.current = ms;
    timerStartTimeRef.current = Date.now();
    fallbackTimerRef.current = setTimeout(() => {
      // Timer sadece video oynatılıyorsa çalışsın (video durdurulmuşsa geçiş yapma)
      const video = videoRef.current;
      if (video && !video.paused) {
        finishLoading();
      }
    }, Math.max(2000, ms));
  }, [clearFallbackTimer, finishLoading]);

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.muted = isMuted;
      videoRef.current.defaultMuted = isMuted;
      videoRef.current.playsInline = true;
      videoRef.current.setAttribute('muted', '');
      videoRef.current.setAttribute('playsinline', '');
      videoRef.current.setAttribute('webkit-playsinline', 'true');
      videoRef.current.volume = isMuted ? 0 : 1.0;
    }
  }, [isMuted]);

  useEffect(() => {
    if (hasTerminated) return;
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
  }, [isPlaying, hasTerminated]);

  useEffect(() => {
    if (hasTerminated) {
      return () => clearFallbackTimer();
    }
    // Video olayları ve fail-safe geçiş
    const scheduleFallback = (ms) => {
      scheduleFallbackTimer(ms);
    };
    const handleEnded = () => { setIsPlaying(false); finishLoading(); };
    const handlePlay = () => { setIsPlaying(true); };
    const handlePause = () => setIsPlaying(false);
    const handleTimeUpdate = () => {
      try {
        const v = videoRef.current;
        if (!v || !isFinite(v.duration) || v.duration <= 0) return;
        if (v.currentTime >= v.duration - 0.2) {
          handleEnded();
        }
      } catch(_) {}
    };
    const handleLoadedMeta = () => {
      if (hasTerminated) return;
      try {
        const v = videoRef.current;
        if (!v) return;
        const ms = isFinite(v.duration) && v.duration > 0 ? Math.ceil(v.duration * 1000) : 8000;
        setVideoDurationMs(ms);
        const p = v.play && v.play();
        if (p && typeof p.then === 'function') p.catch(() => {});
        // Fallback'ı sadece metadata geldikten sonra planla (erken geçişi önlemek için)
        scheduleFallback(ms + 500);
      } catch(_) {}
    };
    const video = videoRef.current;
    if (video) {
      video.addEventListener('ended', handleEnded);
      video.addEventListener('play', handlePlay);
      video.addEventListener('pause', handlePause);
      video.addEventListener('timeupdate', handleTimeUpdate);
      video.addEventListener('loadedmetadata', handleLoadedMeta);
      // Metadata hiç gelmezse geniş bir üst sınır koy (20 sn)
      scheduleFallback(20000);
    } else {
      scheduleFallback(20000);
    }
    return () => {
      clearFallbackTimer();
      if (video) {
        video.removeEventListener('ended', handleEnded);
        video.removeEventListener('play', handlePlay);
        video.removeEventListener('pause', handlePause);
        video.removeEventListener('timeupdate', handleTimeUpdate);
        video.removeEventListener('loadedmetadata', handleLoadedMeta);
      }
    };
  }, [props.onLoadingFinished, hasTerminated, clearFallbackTimer, scheduleFallbackTimer, finishLoading]);

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
      
      if (newPlaying) {
        // Video oynatılıyor - kalan süreye göre timer'ı yeniden başlat
        if (timerRemainingMsRef.current && timerStartTimeRef.current) {
          const elapsed = Date.now() - timerStartTimeRef.current;
          const remaining = Math.max(0, timerRemainingMsRef.current - elapsed);
          if (remaining > 0) {
            scheduleFallbackTimer(remaining);
          }
        } else if (videoDurationMs > 0) {
          // İlk kez oynatılıyorsa video süresine göre başlat
          scheduleFallbackTimer(videoDurationMs + 500);
        }
      } else {
        // Video durduruldu - timer'ı durdur ama kalan süreyi sakla
        if (fallbackTimerRef.current && timerStartTimeRef.current && timerRemainingMsRef.current) {
          const elapsed = Date.now() - timerStartTimeRef.current;
          timerRemainingMsRef.current = Math.max(0, timerRemainingMsRef.current - elapsed);
          clearTimeout(fallbackTimerRef.current);
          fallbackTimerRef.current = null;
          timerStartTimeRef.current = null;
        }
      }
      
      return newPlaying;
    });
  };

  const handleSkip = () => {
    try {
      setIsPlaying(false);
      if (videoRef.current) {
        videoRef.current.pause();
      }
    } catch (_) {}
    finishLoading();
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
                src={loadingVideoBaseline}
                autoPlay
                muted={isMuted}
                playsInline
                ref={videoRef}
                onClick={handleSoundToggle}
                onLoadedMetadata={() => { try { videoRef.current && videoRef.current.play && videoRef.current.play(); } catch(_){} }}
                onCanPlay={() => { try { videoRef.current && videoRef.current.play && videoRef.current.play(); } catch(_){} }}
                preload="auto"
                poster={logo}
              >
                <source src={loadingVideoBaseline} type="video/mp4" />
                <source src={loadingVideo} type="video/mp4" />
              </video>
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
              <button
                type="button"
                className="loading-skip-button"
                onClick={handleSkip}
                aria-label="Analiz sonuçlarına geç"
              >
                Geç
              </button>
            </div>
          </div>
        </div>
  );
});

export default LoadingPage; 