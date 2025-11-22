# 🤖 Cursor AI Guide - ScraperPawNear

## 📋 Proje Hakkında
Bu proje, çeşitli web sitelerinden kayıp hayvan ilanlarını scrape eder ve **SocialPublish** sistemine gönderir.

---

## 🏗️ Proje Yapısı

```
ScraperPawNear/
├── scrapers/              # Site-specific scraper modülleri
│   ├── base_scraper.py    # Base class
│   ├── gorenduyan_scraper.py
│   ├── petcim_scraper.py
│   ├── petlebi_scraper.py
│   └── scraper_manager.py # Tüm scraper'ları yönetir
├── data/                  # Scrape edilen veriler
│   ├── ilanlar.json       # Son durum
│   └── ilan_taramasi_*.json  # Tarihli kayıtlar
├── .github/workflows/     # GitHub Actions
│   └── scraper.yml        # Otomatik çalışma schedule
├── github_scraper.py      # Ana scraper script
├── send_telegram.py       # Telegram bildirimi
├── send_socialpublish.py  # ✨ SocialPublish webhook
└── requirements.txt       # Python dependencies
```

---

## 🔄 Sistem Akışı

```
1. GitHub Actions (Zamanlanmış - Her gün 12:00)
       ↓
2. Scraper Çalışır (github_scraper.py)
       ↓
3. Veriyi Kaydeder (data/ilan_taramasi_YYYY-MM-DD.json)
       ↓
4. SocialPublish'e POST (send_socialpublish.py)
       ↓
5. Otomatik Paylaşım (Facebook + Twitter + Instagram)
```

---

## 🚀 SocialPublish Entegrasyonu

### Nasıl Çalışır?

1. **Scraper:** İlanları toplar → JSON dosyası oluşturur
2. **Webhook:** JSON'u SocialPublish API'sine POST eder
3. **Auto Share:** SocialPublish aktif platformlarda paylaşır

### JSON Formatı (Scraper Output)
```json
[
  {
    "ilan_turu": "Kayıp",
    "baslik": "Köpeğim kayboldu acil aranıyor",
    "aciklama": "Detaylı açıklama...",
    "konum": "İstanbul / Kadıköy",
    "kategori": "Köpek",
    "gorsel": "https://example.com/image.jpg",
    "link": "https://...",
    "tarih1": "12 Saat Önce",
    "tarih2": "2025-11-22T10:30:00Z"
  }
]
```

---

## ⚙️ Kurulum

### 1. GitHub Secrets Tanımla

Repository → **Settings → Secrets and variables → Actions**

Ekle:
```
WEBHOOK_URL = https://your-app.railway.app/api/webhook/share
WEBHOOK_SECRET = your-secret-key-12345
TELEGRAM_BOT_TOKEN = (opsiyonel)
TELEGRAM_CHAT_ID = (opsiyonel)
```

### 2. Railway'de WEBHOOK_SECRET Tanımla

SocialPublish projesi → **Settings → Variables**:
```
WEBHOOK_SECRET = your-secret-key-12345
```

**⚠️ İkisi de aynı olmalı!**

---

## 🧪 Test

### Manuel Test (Lokal)
```bash
# 1. Dependencies yükle
pip install -r requirements.txt

# 2. Environment variables tanımla
export WEBHOOK_URL="https://your-app.railway.app/api/webhook/share"
export WEBHOOK_SECRET="your-secret-key"

# 3. Scraper çalıştır
python github_scraper.py

# 4. SocialPublish'e gönder
python send_socialpublish.py
```

### GitHub Actions'tan Manuel Test
```
Actions → "Günlük İlan Scraper" → Run workflow
```

---

## 📝 Kod Standartları

### Yeni Scraper Eklerken:
1. `scrapers/` altında yeni dosya oluştur
2. `base_scraper.py` den inherit et
3. `scraper_manager.py` ye ekle

Örnek:
```python
from .base_scraper import BaseScraper

class YeniSiteScraper(BaseScraper):
    def __init__(self):
        super().__init__("YeniSite")
    
    def scrape(self) -> list:
        # Scraping logic
        return ilanlar
```

### send_socialpublish.py Değiştirirken:
- ✅ JSON formatını değiştirme (SocialPublish uyumlu)
- ✅ Error handling ekle
- ✅ Timeout ayarla (varsayılan 60s)
- ✅ Güvenlik (WEBHOOK_SECRET) koru

---

## 🔧 Önemli Dosyalar

### `send_socialpublish.py`
**Amaç:** Scrape edilen ilanları SocialPublish'e POST et

**Değiştirilmemesi Gereken:**
- JSON format (baslik, gorsel, aciklama, konum zorunlu)
- Headers (X-Webhook-Secret)
- Endpoint (/api/webhook/share)

**Değiştirilebilir:**
- Timeout değeri
- Retry logic (eklenebilir)
- Loglama (geliştirilebilir)

### `.github/workflows/scraper.yml`
**Amaç:** GitHub Actions zamanlaması

**Schedule:**
```yaml
cron: '0 9 * * *'  # Her gün 09:00 UTC = 12:00 TR
```

**Adımlar:**
1. Scraper çalıştır
2. Verileri commit et
3. **SocialPublish'e gönder** ← Yeni eklendi
4. Telegram bildirimi (opsiyonel)

---

## 🐛 Sorun Giderme

### Problem: SocialPublish webhook çalışmıyor

**Kontrol Et:**
1. ✅ GitHub Secrets tanımlı mı?
   ```
   Settings → Secrets → WEBHOOK_URL, WEBHOOK_SECRET
   ```

2. ✅ Railway'de environment variable var mı?
   ```
   SocialPublish → Settings → Variables → WEBHOOK_SECRET
   ```

3. ✅ URL doğru mu?
   ```bash
   curl https://your-app.railway.app/api/health
   # Response: {"status": "healthy"}
   ```

4. ✅ Secret key eşleşiyor mu?
   - GitHub Secret == Railway Environment Variable

### Problem: İlanlar paylaşılmıyor

**Kontrol Et:**
1. Railway logs'a bak:
   ```
   SocialPublish → Settings → Logs
   ```

2. GitHub Actions logs'a bak:
   ```
   Actions → Son workflow → send_socialpublish.py logs
   ```

3. JSON formatı doğru mu?
   ```json
   {
     "baslik": "zorunlu",
     "gorsel": "zorunlu (URL)",
     "aciklama": "opsiyonel",
     "konum": "opsiyonel"
   }
   ```

### Problem: Rate limit / Too many requests

**Çözüm:**
`send_socialpublish.py` içinde batch gönderim ekle:
```python
# Tüm ilanları tek seferde gönder (varsayılan)
# Veya 10'ar 10'ar gönder:
for i in range(0, len(ilanlar), 10):
    batch = ilanlar[i:i+10]
    send_batch(batch)
    time.sleep(5)  # 5 saniye bekle
```

---

## 📚 API Referansı

### SocialPublish Webhook Endpoint

```http
POST /api/webhook/share
Host: your-app.railway.app
Content-Type: application/json
X-Webhook-Secret: your-secret-key

[
  {
    "baslik": "İlan başlığı",
    "gorsel": "https://image-url.jpg",
    "aciklama": "Detaylı açıklama",
    "konum": "Şehir / İlçe",
    "kategori": "Köpek veya Kedi"
  }
]
```

**Response:**
```json
{
  "success": true,
  "total": 10,
  "success_count": 9,
  "failed_count": 1,
  "results": [
    {
      "success": true,
      "ilan": "İlan başlığı...",
      "results": {
        "facebook": {"status": "success"},
        "twitter": {"status": "success"},
        "instagram": {"status": "success"}
      }
    }
  ]
}
```

---

## 🎯 Görevler

### ✅ Tamamlananlar:
- [x] GitHub Actions schedule kuruldu
- [x] Multi-site scraper yapısı
- [x] SocialPublish webhook entegrasyonu
- [x] Telegram bildirimi

### 🚧 Yapılabilir İyileştirmeler:
- [ ] Duplicate kontrolü (aynı ilan 2 kez paylaşılmasın)
- [ ] Rate limiting (saniyede max X ilan)
- [ ] Retry mekanizması (webhook başarısız olursa tekrar dene)
- [ ] İlan önceliklendirme (yeni ilanlar önce)
- [ ] Database entegrasyonu (paylaşılan ilanları takip et)

---

## 🤝 Katkı

### Yeni Site Scraper Eklemek:
1. `scrapers/yeni_site_scraper.py` oluştur
2. `BaseScraper` inherit et
3. `scraper_manager.py` ye kaydet
4. Test et: `python github_scraper.py`

### Webhook Geliştirmek:
1. **SocialPublish** projesinde `app.py` düzenle
2. `/api/webhook/share` endpoint'ini güncelle
3. Deploy et (Railway otomatik)
4. Bu projede test et: `python send_socialpublish.py`

---

## 📞 Destek

### Cursor AI'ya Sorular:
- "Yeni scraper nasıl eklenir?"
- "Webhook neden çalışmıyor?"
- "Rate limiting nasıl eklenir?"
- "JSON formatı nasıl olmalı?"

### Manuel:
1. `WEBHOOK_SETUP.md` - Detaylı kurulum
2. `scrapers/base_scraper.py` - Scraper base class
3. GitHub Actions logs - Çalışma geçmişi

---

## 🔐 Güvenlik Notları

⚠️ **Asla kodda yazmayın:**
- WEBHOOK_URL
- WEBHOOK_SECRET
- TELEGRAM_BOT_TOKEN

✅ **Her zaman kullanın:**
- GitHub Secrets (Actions için)
- Railway Environment Variables (Backend için)
- `.gitignore` (hassas dosyaları ignore et)

---

## 📈 Monitoring

### GitHub Actions Dashboard
```
Actions → Günlük İlan Scraper
```
- ✅ Yeşil: Başarılı
- ❌ Kırmızı: Hata var
- 🟡 Sarı: Çalışıyor

### Railway Logs
```
SocialPublish → Settings → Logs
```
Webhook geldiğinde göreceksin:
```
[INFO] Webhook received: 10 ilanlar
[OK] Facebook: success
[OK] Twitter: success
```

---

## 🎓 Quick Commands

```bash
# Test scraper
python github_scraper.py

# Test webhook
python send_socialpublish.py

# Check JSON
cat data/ilanlar.json | jq .

# Test SocialPublish health
curl https://your-app.railway.app/api/health
```

---

**🤖 Cursor AI'ya Not:** Bu proje scraping → webhook → auto-share pipeline'ı. Değişiklik yaparken `send_socialpublish.py` ve webhook endpoint (`/api/webhook/share`) uyumunu koru!

