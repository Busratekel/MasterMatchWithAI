import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { API_ENDPOINTS } from '../config';
import './AdminPanel.css';
import AdminSettings from './AdminSettings';

const AdminPanel = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [authToken, setAuthToken] = useState('');
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [detailLog, setDetailLog] = useState(null);
  const [sortOrder, setSortOrder] = useState('desc'); // 'asc' veya 'desc'
  const [showPassword, setShowPassword] = useState(false); // Şifre göster/gizle
  const [activeTab, setActiveTab] = useState('logs'); // 'logs' veya 'settings'
  
  // Oturum süresi yönetimi (5 dakika = 300000 ms)
  const SESSION_TIMEOUT = 5 * 60 * 1000; // 5 dakika
  const [lastActivityTime, setLastActivityTime] = useState(Date.now());

  // Sayfa yüklendiğinde auth token ve kullanıcı adını kontrol et
  useEffect(() => {
    const savedToken = localStorage.getItem('adminAuthToken');
    const savedUsername = localStorage.getItem('adminUsername');
    const savedLoginTime = localStorage.getItem('adminLoginTime');
    
    // Oturum süresi kontrolü
    if (savedToken && savedLoginTime) {
      const loginTime = parseInt(savedLoginTime, 10);
      const currentTime = Date.now();
      const timeSinceLogin = currentTime - loginTime;
      
      if (timeSinceLogin > SESSION_TIMEOUT) {
        // Oturum süresi dolmuş
        localStorage.removeItem('adminAuthToken');
        localStorage.removeItem('adminLoginTime');
        toast.warning('Oturum süreniz doldu. Lütfen tekrar giriş yapın.');
      } else {
        setAuthToken(savedToken);
        setIsLoggedIn(true);
        setLastActivityTime(currentTime);
      }
    }
    
    if (savedUsername) {
      setUsername(savedUsername);
    }
    
    // Backend health check
    checkBackendHealth();
  }, [SESSION_TIMEOUT]);

  // Backend health check
  const checkBackendHealth = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.HEALTH || 'http://localhost:5001/api/health');
      if (!response.ok) {
        console.warn('Backend health check failed');
      }
    } catch (error) {
      console.warn('Backend sunucusuna bağlanılamıyor:', error);
    }
  };

  // Auth token set edildikten sonra data yükle
  useEffect(() => {
    if (authToken && isLoggedIn) {
      // Kısa bir delay ile data yükle (backend'in hazır olması için)
      const timer = setTimeout(() => {
        loadStatsWithToken(authToken);
        loadLogsWithToken(authToken);
      }, 500);
      
      return () => clearTimeout(timer);
    }
  }, [authToken, isLoggedIn]);

  // Oturum süresi kontrolü ve aktivite takibi
  useEffect(() => {
    if (!isLoggedIn) return;

    // Kullanıcı aktivitesini güncelle
    const updateActivity = () => {
      setLastActivityTime(Date.now());
      localStorage.setItem('adminLoginTime', Date.now().toString());
    };

    // Mouse ve klavye olaylarını dinle
    const events = ['mousedown', 'keydown', 'scroll', 'touchstart', 'click'];
    events.forEach(event => {
      window.addEventListener(event, updateActivity);
    });

    // Her dakika oturum kontrolü yap
    const checkSession = setInterval(() => {
      const currentTime = Date.now();
      const timeSinceActivity = currentTime - lastActivityTime;

      if (timeSinceActivity > SESSION_TIMEOUT) {
        // Oturum süresi dolmuş - otomatik çıkış yap
        setAuthToken('');
        setIsLoggedIn(false);
        localStorage.removeItem('adminAuthToken');
        localStorage.removeItem('adminLoginTime');
        setPassword('');
        setLogs([]);
        setStats(null);
        toast.warning('Oturum süreniz doldu. Lütfen tekrar giriş yapın.');
      }
    }, 60000); // Her 1 dakikada bir kontrol et

    // Cleanup
    return () => {
      events.forEach(event => {
        window.removeEventListener(event, updateActivity);
      });
      clearInterval(checkSession);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isLoggedIn, lastActivityTime, SESSION_TIMEOUT]);

  // Login fonksiyonu
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(API_ENDPOINTS.ADMIN_LOGIN || 'http://localhost:5001/api/admin/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      const result = await response.json();

      if (result.success) {
        // Basic auth token oluştur
        const token = btoa(`${username}:${password}`);
        const loginTime = Date.now();
        setAuthToken(token);
        setIsLoggedIn(true);
        setLastActivityTime(loginTime);
        localStorage.setItem('adminAuthToken', token);
        localStorage.setItem('adminUsername', username); // Kullanıcı adını kaydet
        localStorage.setItem('adminLoginTime', loginTime.toString()); // Login zamanını kaydet
        toast.success('Giriş başarılı!');
        
        // Token set edildikten sonra data yükle (setTimeout ile)
        setTimeout(() => {
          loadStatsWithToken(token);
          loadLogsWithToken(token);
        }, 100);
      } else {
        toast.error(result.error || 'Giriş başarısız!');
      }
    } catch (error) {
      toast.error('Bağlantı hatası!');
    } finally {
      setLoading(false);
    }
  };

  // Logout fonksiyonu
  const handleLogout = () => {
    setAuthToken('');
    setIsLoggedIn(false);
    localStorage.removeItem('adminAuthToken');
    localStorage.removeItem('adminLoginTime');
    // Kullanıcı adını silme - hatırlanacak
    setPassword(''); // Sadece şifreyi temizle
    setLogs([]);
    setStats(null);
    toast.success('Çıkış yapıldı!');
  };

  // İstatistikleri yükle
  const loadStats = async () => {
    if (!authToken) return;
    await loadStatsWithToken(authToken);
  };

  const loadStatsWithToken = async (token) => {
    try {
      const response = await fetch(API_ENDPOINTS.ADMIN_STATS || 'http://localhost:5001/api/admin/stats', {
        headers: {
          'Authorization': `Basic ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          // Token geçersiz, logout yap
          handleLogout();
          toast.error('Oturum süresi dolmuş. Lütfen tekrar giriş yapın.');
          return;
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      if (result.success) {
        setStats(result.stats);
      } else {
        console.error('Stats error:', result.error);
        toast.error(result.error || 'İstatistikler yüklenemedi');
      }
    } catch (error) {
      console.error('Stats yükleme hatası:', error);
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        toast.error('Backend sunucusuna bağlanılamıyor. Lütfen sunucunun çalıştığından emin olun.');
      } else {
        toast.error('İstatistikler yüklenemedi');
      }
    }
  };

  // Logları yükle
  const loadLogs = async (page = 1) => {
    if (!authToken) return;
    await loadLogsWithToken(authToken, page);
  };

  const loadLogsWithToken = async (token, page = 1) => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        per_page: '50',
      });

      if (searchTerm) params.append('search', searchTerm);
      if (dateFrom) params.append('date_from', dateFrom);
      if (dateTo) params.append('date_to', dateTo);

      const response = await fetch(
        `${API_ENDPOINTS.ADMIN_LOGS || 'http://localhost:5001/api/admin/logs'}?${params}`,
        {
          headers: {
            'Authorization': `Basic ${token}`,
          },
        }
      );

      if (!response.ok) {
        if (response.status === 401) {
          // Token geçersiz, logout yap
          handleLogout();
          toast.error('Oturum süresi dolmuş. Lütfen tekrar giriş yapın.');
          return;
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      if (result.success) {
        setLogs(result.logs);
        setCurrentPage(result.pagination.page);
        setTotalPages(result.pagination.pages);
      } else {
        console.error('Logs error:', result.error);
        toast.error(result.error || 'Loglar yüklenemedi!');
      }
    } catch (error) {
      console.error('Logs yükleme hatası:', error);
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        toast.error('Backend sunucusuna bağlanılamıyor. Lütfen sunucunun çalıştığından emin olun.');
      } else {
        toast.error('Bağlantı hatası!');
      }
    } finally {
      setLoading(false);
    }
  };

  // Arama ve filtreleme
  const handleSearch = () => {
    setCurrentPage(1);
    loadLogs(1);
  };

  // Sayfa değiştirme
  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
    loadLogs(newPage);
  };

  // Tarihi formatla
  const formatDate = (dateString) => {
    if (!dateString) return '-';
    
    try {
      const date = new Date(dateString);
      
      // Geçerli tarih kontrolü
      if (isNaN(date.getTime())) return '-';
      
      // Türkiye saati ile formatla
      return date.toLocaleString('tr-TR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        timeZone: 'Europe/Istanbul'
      });
    } catch (error) {
      console.error('Tarih formatlama hatası:', error);
      return '-';
    }
  };

  // Cevapları formatla
  const formatAnswers = (answers) => {
    if (!answers || typeof answers !== 'object') return '-';
    
    const formatted = Object.entries(answers).map(([key, value]) => {
      return `${key}: ${value}`;
    }).join(', ');
    
    return formatted.length > 40 ? formatted.substring(0, 40) + '...' : formatted;
  };

  // Detay modalını aç/kapat
  const openDetail = (log) => {
    setDetailLog(log);
    setShowDetailModal(true);
  };

  const closeDetail = () => {
    setShowDetailModal(false);
    setDetailLog(null);
  };

  // Tarih sıralama toggle
  const toggleSortOrder = () => {
    const newOrder = sortOrder === 'asc' ? 'desc' : 'asc';
    setSortOrder(newOrder);
    
    // Logları sırala
    const sortedLogs = [...logs].sort((a, b) => {
      const dateA = new Date(a.tarih);
      const dateB = new Date(b.tarih);
      
      if (newOrder === 'asc') {
        return dateA - dateB; // Eskiden yeniye
      } else {
        return dateB - dateA; // Yeniden eskiye
      }
    });
    
    setLogs(sortedLogs);
  };

  // Login formu
  if (!isLoggedIn) {
    return (
        <div className="admin-login">
          <h1>Admin Panel</h1>
          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label>Kullanıcı Adı:</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label>Şifre:</label>
              <div style={{ position: 'relative' }}>
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  style={{ width: '100%', paddingRight: '45px' }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{
                    position: 'absolute',
                    right: '10px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    fontSize: '20px',
                    padding: '0',
                    color: '#667eea',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: '30px',
                    height: '30px'
                  }}
                  title={showPassword ? "Şifreyi gizle" : "Şifreyi göster"}
                >
                  {showPassword ? '👁️' : '👁️‍🗨️'}
                </button>
              </div>
            </div>
            <button type="submit" disabled={loading}>
              {loading ? 'Giriş Yapılıyor...' : 'Giriş Yap'}
            </button>
          </form>
        </div>
    );
  }

  // Admin panel ana sayfası
  return (
    <div className="admin-container">
      <div className="admin-header">
        <h1>Admin Panel - Yastık Seçim Robotu</h1>
        <button onClick={handleLogout} className="logout-btn">
          Çıkış Yap
        </button>
      </div>

      {/* Tab Navigation */}
      <div className="admin-tabs">
        <button 
          className={`tab-btn ${activeTab === 'logs' ? 'active' : ''}`}
          onClick={() => setActiveTab('logs')}
        >
          📊 Kullanıcı Logları
        </button>
        <button 
          className={`tab-btn ${activeTab === 'settings' ? 'active' : ''}`}
          onClick={() => setActiveTab('settings')}
        >
          ⚙️ Ayarlar
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'logs' ? (
        <>
          {/* İstatistikler */}
      {stats && (
        <div className="admin-stats">
          <h2>İstatistikler</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <h3>Toplam Log</h3>
              <p>{stats.total_logs}</p>
            </div>
            <div className="stat-card">
              <h3>Email Veren</h3>
              <p>{stats.email_logs}</p>
            </div>
            <div className="stat-card">
              <h3>Bugünkü Loglar</h3>
              <p>{stats.today_logs}</p>
            </div>
            <div className="stat-card">
              <h3>Bu Haftaki Loglar</h3>
              <p>{stats.week_logs}</p>
            </div>
          </div>
        </div>
      )}

      {/* Filtreler */}
      <div className="admin-filters">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '20px', flexWrap: 'wrap' }}>
          <div style={{ flex: '1', minWidth: '300px' }}>
            <h2>Log Kayıtları</h2>
            <div className="filters-row">
              <input
                type="text"
                placeholder="Email, cevaplar veya yastıklar ara..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
              <input
                type="date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                placeholder="Başlangıç tarihi"
              />
              <input
                type="date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                placeholder="Bitiş tarihi"
              />
              <button onClick={handleSearch} disabled={loading}>
                {loading ? 'Yükleniyor...' : 'Ara'}
              </button>
            </div>
          </div>
          
          <div style={{ 
            background: 'linear-gradient(135deg, #f8f9ff 0%, #fff8f9 100%)',
            padding: '16px',
            borderRadius: '10px',
            border: '1px solid #e9ecef',
            minWidth: '280px',
            maxWidth: '350px'
          }}>
            <h3 style={{ 
              margin: '0 0 12px 0', 
              fontSize: '14px', 
              color: '#667eea',
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              ℹ️ Kolon Açıklamaları
            </h3>
            <div style={{ fontSize: '12px', lineHeight: '1.6', color: '#495057' }}>

              <div style={{ marginBottom: '8px' }}>
                <strong style={{ color: '#667eea' }}>Cevaplar:</strong> Kullanıcının yastık seçim robotuna verdiği cevaplar.
              </div>
              <div>
                <strong style={{ color: '#667eea' }}>Önerilen Yastıklar:</strong> Kullanıcının email bilgisi girip sonuçları mail ile aldıktan sonra robotun önerdiği yastıklar.
              </div>
              <div style={{ marginBottom: '8px' }}>
                <strong style={{ color: '#667eea' }}>İncelenen Ürünler:</strong> Önerilen yastıklardan hangi ürünleri incelediği
              </div>
              <div style={{ marginBottom: '8px' }}>
                <strong style={{ color: '#667eea' }}>İncelendi mi?:</strong> Kullanıcı ürün detaylarına baktı mı?
              </div>
              <div>
                <strong style={{ color: '#667eea' }}>Analiz Alındı mı?:</strong> Kullanıcı "Sonuçları Gör" butonuna tıkladı ama sonuçları email ile almadı.Bu sebeple de önerilen listeyi görmedi.
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Loglar tablosu */}
      <div className="admin-logs">
        {logs.length === 0 ? (
          <p>Log kaydı bulunamadı.</p>
        ) : (
          <>
            <div className="logs-table-container">
              <table className="logs-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th 
                      onClick={toggleSortOrder} 
                      style={{ cursor: 'pointer', userSelect: 'none' }}
                      title="Tarihe göre sırala"
                    >
                      Tarih {sortOrder === 'desc' ? '▼' : '▲'}
                    </th>
                    <th>Email</th>
                    <th>Cevaplar</th>
                    <th>Önerilen Yastıklar</th>
                    <th>İncelenen Ürünler</th>
                    <th>İncelendi mi?</th>
                    <th>Analiz Alındı mı?</th>
                    <th>IP</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log) => (
                    <tr key={log.id}>
                      <td>{log.id}</td>
                      <td>{formatDate(log.tarih)}</td>
                      <td>{log.email || '-'}</td>
                      <td title={formatAnswers(log.cevaplar)}>
                        <span
                          style={{ cursor: 'pointer', textDecoration: 'underline', textUnderlineOffset: '2px' }}
                          onClick={() => openDetail(log)}
                        >
                          {formatAnswers(log.cevaplar)}
                        </span>
                      </td>
                      <td>
                        {log.onerilen_yastiklar && log.onerilen_yastiklar.length > 0 ? (
                          <span
                            style={{ cursor: 'pointer', textDecoration: 'underline', textUnderlineOffset: '2px' }}
                            title={log.onerilen_yastiklar.join(', ')}
                            onClick={() => openDetail(log)}
                          >
                            {log.onerilen_yastiklar.join(', ').length > 35
                              ? log.onerilen_yastiklar.join(', ').slice(0, 35) + '...'
                              : log.onerilen_yastiklar.join(', ')}
                          </span>
                        ) : '-' }
                      </td>
                      <td>
                        {log.incelenen_urunler ? (
                          <span
                            style={{ cursor: 'pointer', textDecoration: 'underline', textUnderlineOffset: '2px', color: '#667eea' }}
                            title={log.incelenen_urunler}
                            onClick={() => openDetail(log)}
                          >
                            {log.incelenen_urunler.length > 25 
                              ? log.incelenen_urunler.slice(0, 25) + '...'
                              : log.incelenen_urunler}
                          </span>
                        ) : '-'}
                      </td>
                      <td>
                        <span style={{ 
                          padding: '4px 8px', 
                          borderRadius: '4px', 
                          fontSize: '12px',
                          fontWeight: 600,
                          background: log.incelendi_mi ? '#d4edda' : '#f8d7da',
                          color: log.incelendi_mi ? '#155724' : '#721c24'
                        }}>
                          {log.incelendi_mi ? '✓ Evet' : '✗ Hayır'}
                        </span>
                      </td>
                      <td>
                        <span style={{ 
                          padding: '4px 8px', 
                          borderRadius: '4px', 
                          fontSize: '12px',
                          fontWeight: 600,
                          background: log.analiz_alindi_mi ? '#d1ecf1' : '#fff3cd',
                          color: log.analiz_alindi_mi ? '#0c5460' : '#856404'
                        }}>
                          {log.analiz_alindi_mi ? '✓ Alındı' : '✗ Alınmadı'}
                        </span>
                      </td>
                      <td>{log.ip_adresi || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Sayfalama */}
            {totalPages > 1 && (
              <div className="pagination">
                <button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                >
                  Önceki
                </button>
                <span>
                  Sayfa {currentPage} / {totalPages}
                </span>
                <button
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                >
                  Sonraki
                </button>
              </div>
            )}
          </>
        )}
      </div>
      {showDetailModal && detailLog && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(102, 126, 234, 0.15)',
            backdropFilter: 'blur(4px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 2000,
            animation: 'fadeIn 0.2s ease'
          }}
          onClick={closeDetail}
        >
          <div
            style={{
              background: 'linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%)',
              borderRadius: 16,
              width: 'min(900px, 95vw)',
              maxHeight: '85vh',
              overflow: 'auto',
              padding: 32,
              boxShadow: '0 20px 60px rgba(102, 126, 234, 0.3)',
              border: '1px solid rgba(102, 126, 234, 0.1)',
              animation: 'slideUp 0.3s ease'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24, paddingBottom: 16, borderBottom: '2px solid #e9ecef' }}>
              <h2 style={{ 
                margin: 0, 
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                fontSize: '1.8rem',
                fontWeight: 700
              }}>
                📋 Kayıt Detayı (ID: {detailLog.id})
              </h2>
              <button 
                onClick={closeDetail} 
                style={{
                  background: 'linear-gradient(135deg, #dc3545 0%, #c82333 100%)',
                  color: 'white',
                  border: 'none',
                  padding: '10px 20px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: 600,
                  fontSize: '14px',
                  transition: 'all 0.3s ease',
                  boxShadow: '0 2px 6px rgba(220, 53, 69, 0.3)'
                }}
              >
                ✕ Kapat
              </button>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '160px 1fr', rowGap: 16, columnGap: 20 }}>
              <div style={{ fontWeight: 700, color: '#667eea', fontSize: '14px' }}>📧 Email</div>
              <div style={{ padding: '8px 12px', background: '#f8f9ff', borderRadius: '6px', border: '1px solid #e9ecef' }}>
                {detailLog.email || '-'}
              </div>
              
              <div style={{ fontWeight: 700, color: '#667eea', fontSize: '14px' }}>📅 Tarih</div>
              <div style={{ padding: '8px 12px', background: '#f8f9ff', borderRadius: '6px', border: '1px solid #e9ecef' }}>
                {formatDate(detailLog.tarih)}
              </div>
              
              <div style={{ fontWeight: 700, color: '#667eea', fontSize: '14px' }}>🌐 IP Adresi</div>
              <div style={{ padding: '8px 12px', background: '#f8f9ff', borderRadius: '6px', border: '1px solid #e9ecef' }}>
                {detailLog.ip_adresi || '-'}
              </div>
              
              <div style={{ fontWeight: 700, color: '#667eea', fontSize: '14px' }}>🔍 İncelenen Ürünler</div>
              <div style={{ padding: '8px 12px', background: '#f8f9ff', borderRadius: '6px', border: '1px solid #e9ecef' }}>
                {detailLog.incelenen_urunler || '-'}
              </div>
              
              <div style={{ fontWeight: 700, color: '#667eea', fontSize: '14px' }}>✓ İncelendi Mi?</div>
              <div style={{ padding: '8px 12px', background: '#f8f9ff', borderRadius: '6px', border: '1px solid #e9ecef' }}>
                <span style={{ 
                  padding: '4px 12px', 
                  borderRadius: '6px', 
                  fontSize: '13px',
                  fontWeight: 600,
                  background: detailLog.incelendi_mi ? '#d4edda' : '#f8d7da',
                  color: detailLog.incelendi_mi ? '#155724' : '#721c24'
                }}>
                  {detailLog.incelendi_mi ? '✓ Evet' : '✗ Hayır'}
                </span>
              </div>
              
              <div style={{ fontWeight: 700, color: '#667eea', fontSize: '14px' }}>📊 Analiz Sonucu Alındı Mı?</div>
              <div style={{ padding: '8px 12px', background: '#f8f9ff', borderRadius: '6px', border: '1px solid #e9ecef' }}>
                <span style={{ 
                  padding: '4px 12px', 
                  borderRadius: '6px', 
                  fontSize: '13px',
                  fontWeight: 600,
                  background: detailLog.analiz_alindi_mi ? '#d1ecf1' : '#fff3cd',
                  color: detailLog.analiz_alindi_mi ? '#0c5460' : '#856404'
                }}>
                  {detailLog.analiz_alindi_mi ? '✓ Alındı' : '✗ Alınmadı'}
                </span>
              </div>
              
              <div style={{ fontWeight: 700, color: '#667eea', alignSelf: 'start', fontSize: '14px' }}>💬 Cevaplar</div>
              <div style={{ 
                padding: '16px', 
                background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)', 
                borderRadius: 10,
                border: '1px solid #dee2e6',
                boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.05)'
              }}>
                {detailLog.cevaplar && Object.keys(detailLog.cevaplar).length > 0 ? (
                  <ul style={{ margin: 0, paddingLeft: 20, lineHeight: '1.8' }}>
                    {Object.entries(detailLog.cevaplar).map(([key, value], idx) => {
                      // Eğer value bir obje ise, JSON formatında göster
                      const displayValue = typeof value === 'object' && value !== null 
                        ? JSON.stringify(value, null, 2)
                        : String(value);
                      
                      return (
                        <li key={idx} style={{ 
                          marginBottom: '8px',
                          color: '#495057',
                          fontSize: '14px'
                        }}>
                          <strong style={{ color: '#667eea' }}>{key}:</strong>{' '}
                          {typeof value === 'object' && value !== null ? (
                            <pre style={{ 
                              display: 'inline', 
                              margin: 0, 
                              background: 'transparent',
                              fontFamily: 'inherit',
                              whiteSpace: 'pre-wrap'
                            }}>
                              {displayValue}
                            </pre>
                          ) : (
                            displayValue
                          )}
                        </li>
                      );
                    })}
                  </ul>
                ) : (
                  <span style={{ color: '#6c757d', fontStyle: 'italic' }}>Cevap yok</span>
                )}
              </div>
              
              <div style={{ fontWeight: 700, color: '#667eea', alignSelf: 'start', fontSize: '14px' }}>🛏️ Önerilen Yastıklar</div>
              <div style={{ padding: '12px', background: '#f8f9ff', borderRadius: '10px', border: '1px solid #e9ecef' }}>
                {detailLog.onerilen_yastiklar && detailLog.onerilen_yastiklar.length > 0 ? (
                  <ul style={{ margin: 0, paddingLeft: 20, lineHeight: '1.8' }}>
                    {detailLog.onerilen_yastiklar.map((p, idx) => (
                      <li key={idx} style={{ 
                        marginBottom: '6px',
                        color: '#495057',
                        fontSize: '14px'
                      }}>
                        {p}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <span style={{ color: '#6c757d', fontStyle: 'italic' }}>Henüz öneri yok</span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
        </>
      ) : (
        /* Settings Tab */
        <AdminSettings authToken={authToken} />
      )}
    </div>
  );
};

export default AdminPanel;
