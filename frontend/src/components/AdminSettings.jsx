import React, { useState, useEffect } from 'react';
import './AdminSettings.css';
import { API_ENDPOINTS } from '../config';

const AdminSettings = ({ authToken }) => {
  const [settings, setSettings] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState(''); // 'success' veya 'error'
  const [originalAdEnabled, setOriginalAdEnabled] = useState(null); // AD_ENABLED'ın orijinal değeri

  // Ayarları yükle
  useEffect(() => {
    if (authToken) {
      fetchSettings();
    }
  }, [authToken]);

  const fetchSettings = async () => {
    if (!authToken) {
      setMessage('❌ Giriş bilgileri bulunamadı. Lütfen yeniden giriş yapın.');
      setMessageType('error');
      setLoading(false);
      return;
    }
    
    try {
      setLoading(true);
      const response = await fetch(API_ENDPOINTS.ADMIN_SETTINGS, {
        headers: {
          'Authorization': `Basic ${authToken}`
        }
      });

      const data = await response.json();
      if (data.success) {
        setSettings(data.settings);
        // AD_ENABLED'ın orijinal değerini kaydet
        if (data.settings.AD_ENABLED) {
          setOriginalAdEnabled(data.settings.AD_ENABLED.value);
        }
      } else {
        setMessage('Ayarlar yüklenemedi');
        setMessageType('error');
      }
    } catch (error) {
      console.error('Ayar yükleme hatası:', error);
      setMessage('Ayarlar yüklenirken hata oluştu');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: {
        ...prev[key],
        value: value
      }
    }));
  };

  const handleSave = async () => {
    if (!authToken) {
      setMessage('❌ Giriş bilgileri bulunamadı. Lütfen yeniden giriş yapın.');
      setMessageType('error');
      return;
    }
    
    try {
      setSaving(true);
      setMessage('');

      // Sadece value'ları gönder
      const settingsToSend = {};
      Object.keys(settings).forEach(key => {
        settingsToSend[key] = settings[key].value;
      });

      const response = await fetch(API_ENDPOINTS.ADMIN_SETTINGS, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Basic ${authToken}`
        },
        body: JSON.stringify({ settings: settingsToSend })
      });

      const data = await response.json();
      if (data.success) {
        // AD_ENABLED değişti mi kontrol et
        const currentAdEnabled = settingsToSend.AD_ENABLED;
        const adEnabledChanged = originalAdEnabled !== null && originalAdEnabled !== currentAdEnabled;
        
        if (adEnabledChanged) {
          setMessage('✓ Ayarlar kaydedildi. Authentication yöntemi değişti, lütfen yeniden giriş yapın.');
          setMessageType('success');
          // 2 saniye sonra logout yap
          setTimeout(() => {
            localStorage.removeItem('adminAuthToken');
            localStorage.removeItem('adminLoginTime');
            window.location.reload();
          }, 2000);
        } else {
          setMessage('✓ Ayarlar başarıyla kaydedildi');
          setMessageType('success');
          // Mesajı 3 saniye sonra temizle
          setTimeout(() => setMessage(''), 3000);
        }
      } else {
        setMessage('✗ Ayarlar kaydedilemedi');
        setMessageType('error');
        setTimeout(() => setMessage(''), 5000);
      }
    } catch (error) {
      console.error('Ayar kaydetme hatası:', error);
      setMessage('✗ Kaydetme sırasında hata oluştu');
      setMessageType('error');
      setTimeout(() => setMessage(''), 5000);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="admin-settings">
        <h2>Ayarlar</h2>
        <div className="settings-loading">Yükleniyor...</div>
      </div>
    );
  }

  return (
    <div className="admin-settings">
      <h2>🔧 Sistem Ayarları</h2>
      
      {message && (
        <div className={`settings-message ${messageType}`}>
          {message}
        </div>
      )}

      <div className="settings-sections">
        {/* Active Directory Ayarları */}
        <div className="settings-section">
          <h3>Active Directory Ayarları</h3>
          
          <div className="setting-item">
            <label>
              <input
                type="checkbox"
                checked={settings.AD_ENABLED?.value === 'True' || settings.AD_ENABLED?.value === 'true'}
                onChange={(e) => handleChange('AD_ENABLED', e.target.checked ? 'True' : 'False')}
              />
              <span className="setting-label">Active Directory Kullan</span>
            </label>
            <p className="setting-description">
              Aktif edildiğinde kullanıcılar AD hesaplarıyla giriş yapabilir
            </p>
          </div>

          {settings.AD_ENABLED?.value === 'True' || settings.AD_ENABLED?.value === 'true' ? (
            <>
              <div className="setting-item">
                <label>
                  <span className="setting-label">AD Sunucu Adresi</span>
                  <input
                    type="text"
                    value={settings.AD_SERVER?.value || ''}
                    onChange={(e) => handleChange('AD_SERVER', e.target.value)}
                    placeholder="örn: 10.16.1.55"
                  />
                </label>
              </div>

              <div className="setting-item">
                <label>
                  <span className="setting-label">AD Port</span>
                  <input
                    type="number"
                    value={settings.AD_PORT?.value || '389'}
                    onChange={(e) => handleChange('AD_PORT', e.target.value)}
                    placeholder="389"
                  />
                </label>
              </div>

              <div className="setting-item">
                <label>
                  <span className="setting-label">Domain</span>
                  <input
                    type="text"
                    value={settings.AD_DOMAIN?.value || ''}
                    onChange={(e) => handleChange('AD_DOMAIN', e.target.value)}
                    placeholder="örn: doqu"
                  />
                </label>
              </div>

              <div className="setting-item">
                <label>
                  <span className="setting-label">Base DN</span>
                  <input
                    type="text"
                    value={settings.AD_BASE_DN?.value || ''}
                    onChange={(e) => handleChange('AD_BASE_DN', e.target.value)}
                    placeholder="örn: DC=doqu,DC=local"
                  />
                </label>
              </div>

              <div className="setting-item">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.AD_USE_SSL?.value === 'True' || settings.AD_USE_SSL?.value === 'true'}
                    onChange={(e) => handleChange('AD_USE_SSL', e.target.checked ? 'True' : 'False')}
                  />
                  <span className="setting-label">SSL Kullan</span>
                </label>
              </div>

              <div className="setting-item">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.AD_USE_TLS?.value === 'True' || settings.AD_USE_TLS?.value === 'true'}
                    onChange={(e) => handleChange('AD_USE_TLS', e.target.checked ? 'True' : 'False')}
                  />
                  <span className="setting-label">TLS Kullan</span>
                </label>
              </div>

              <div className="setting-item">
                <label>
                  <span className="setting-label">Yetkili Grup (Opsiyonel)</span>
                  <input
                    type="text"
                    value={settings.AD_AUTHORIZED_GROUP?.value || ''}
                    onChange={(e) => handleChange('AD_AUTHORIZED_GROUP', e.target.value)}
                    placeholder="Boş bırakılırsa tüm kullanıcılar giriş yapabilir"
                  />
                </label>
                <p className="setting-description">
                  Sadece belirli bir AD grubundaki kullanıcıların giriş yapmasını sağlar
                </p>
              </div>
            </>
          ) : (
            <div className="setting-info">
              <p>ℹ️ Active Directory kapalı. Basit admin girişi kullanılıyor.</p>
            </div>
          )}
        </div>
      </div>

      <div className="settings-actions">
        <button 
          onClick={handleSave} 
          disabled={saving}
          className="btn-save"
        >
          {saving ? 'Kaydediliyor...' : '💾 Kaydet'}
        </button>
        <button 
          onClick={fetchSettings} 
          disabled={saving}
          className="btn-reset"
        >
          🔄 Yenile
        </button>
      </div>
    </div>
  );
};

export default AdminSettings;

