// API Konfigürasyonu
// Windows Service olarak çalışan backend (port 5000)
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://mastermatch.doquhome.com.tr'
  : 'http://localhost:5001';

// API Endpoint'leri
export const API_ENDPOINTS = {
  // Admin endpoints
  ADMIN_LOGIN: `${API_BASE_URL}/api/admin/login`,
  ADMIN_LOGS: `${API_BASE_URL}/api/admin/logs`,
  ADMIN_STATS: `${API_BASE_URL}/api/admin/stats`,
  ADMIN_SETTINGS: `${API_BASE_URL}/api/admin/settings`,
  HEALTH: `${API_BASE_URL}/api/health`,
  KVKK_ONAY_EKLE: `${API_BASE_URL}/api/kvkk_onay_ekle`,
  KVKK_METIN: `${API_BASE_URL}/api/kvkk_metin`,
  LOG_URUN_INCELEME: `${API_BASE_URL}/api/log_urun_inceleme`,
  RECOMMEND: `${API_BASE_URL}/api/recommend`,
  QUESTIONS: `${API_BASE_URL}/api/questions`,
  YASTIKLAR: `${API_BASE_URL}/api/yastiklar`,
  SAVE_MAIL: `${API_BASE_URL}/api/save-mail`
};

export default API_ENDPOINTS; 