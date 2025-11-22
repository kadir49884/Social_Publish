# 🔗 Webhook API Dokümantasyonu

## Genel Bakış

SocialPublish, dış sistemlerden (scraper, bot, vb.) gelen ilanları otomatik olarak sosyal medyada paylaşmak için webhook endpoint'i sağlar.

---

## 📍 Endpoint

```
POST /api/webhook/share
```

---

## 🔐 Güvenlik

### Environment Variable
Railway'de tanımlanmalı:
```
WEBHOOK_SECRET=your-super-secret-key-12345
```

### Request Header
```http
X-Webhook-Secret: your-super-secret-key-12345
```

**Not:** Secret key opsiyoneldir ama production için şiddetle tavsiye edilir.

---

## 📥 Request

### Headers
```http
Content-Type: application/json
X-Webhook-Secret: your-secret-key
```

### Body Format

#### Tek İlan
```json
{
  "baslik": "Köpeğim kayboldu acil aranıyor",
  "gorsel": "https://example.com/image.jpg",
  "aciklama": "Detaylı açıklama metni",
  "konum": "İstanbul / Kadıköy",
  "kategori": "Köpek"
}
```

#### Çoklu İlan (Array)
```json
[
  {
    "baslik": "İlan 1",
    "gorsel": "https://...",
    "aciklama": "...",
    "konum": "...",
    "kategori": "Köpek"
  },
  {
    "baslik": "İlan 2",
    "gorsel": "https://...",
    "aciklama": "...",
    "konum": "...",
    "kategori": "Kedi"
  }
]
```

### Zorunlu Alanlar
| Alan | Tip | Açıklama |
|------|-----|----------|
| `baslik` | string | Paylaşım başlığı |
| `gorsel` | string | Görsel URL'si (https://) |

### Opsiyonel Alanlar
| Alan | Tip | Açıklama |
|------|-----|----------|
| `aciklama` | string | Detaylı açıklama |
| `konum` | string | Konum bilgisi (Şehir / İlçe) |
| `kategori` | string | Kategori (Köpek, Kedi, vb.) |

---

## 📤 Response

### Başarılı (200 OK)
```json
{
  "success": true,
  "total": 10,
  "success_count": 9,
  "failed_count": 1,
  "results": [
    {
      "success": true,
      "ilan": "Köpeğim kayboldu acil aranıyor...",
      "results": {
        "facebook": {
          "status": "success",
          "post_id": "123456789",
          "platform": "facebook"
        },
        "twitter": {
          "status": "success",
          "post_id": "987654321",
          "platform": "twitter"
        },
        "instagram": {
          "status": "success",
          "post_id": "456789123",
          "platform": "instagram"
        }
      }
    }
  ]
}
```

### Hata Durumları

#### 401 Unauthorized
```json
{
  "success": false,
  "error": "Unauthorized: Invalid webhook secret"
}
```

#### 400 Bad Request
```json
{
  "success": false,
  "error": "No JSON data provided"
}
```

#### 500 Internal Server Error
```json
{
  "success": false,
  "error": "Exception: ..."
}
```

---

## 🎯 Davranış

### Otomatik Özellikler
1. **Hashtag Ekleme:** Her paylaşıma otomatik 5 rastgele hashtag eklenir
2. **Multi-Platform:** Aktif olan tüm platformlarda paylaşılır
3. **Error Resilience:** Bir ilan hata verse bile diğerleri paylaşılır

### Platform Aktiflik
Webhook sadece **yapılandırılmış** platformlarda paylaşır:
- ✅ Facebook (FACEBOOK_ACCESS_TOKEN varsa)
- ✅ Twitter (TWITTER_API_KEY varsa)
- ✅ Instagram (INSTAGRAM_ACCESS_TOKEN varsa)

---

## 🧪 Test

### cURL
```bash
curl -X POST https://your-app.railway.app/api/webhook/share \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: your-secret-key" \
  -d '{
    "baslik": "Test İlanı",
    "gorsel": "https://picsum.photos/600/400",
    "aciklama": "Bu bir test ilanıdır",
    "konum": "Test / Lokasyon",
    "kategori": "Köpek"
  }'
```

### Python
```python
import requests

url = "https://your-app.railway.app/api/webhook/share"
headers = {
    "Content-Type": "application/json",
    "X-Webhook-Secret": "your-secret-key"
}
data = {
    "baslik": "Test İlanı",
    "gorsel": "https://picsum.photos/600/400",
    "aciklama": "Test açıklaması",
    "konum": "İstanbul / Kadıköy",
    "kategori": "Köpek"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

### JavaScript (Node.js)
```javascript
const fetch = require('node-fetch');

const url = 'https://your-app.railway.app/api/webhook/share';
const headers = {
  'Content-Type': 'application/json',
  'X-Webhook-Secret': 'your-secret-key'
};
const data = {
  baslik: 'Test İlanı',
  gorsel: 'https://picsum.photos/600/400',
  aciklama: 'Test açıklaması',
  konum: 'İstanbul / Kadıköy',
  kategori: 'Köpek'
};

fetch(url, {
  method: 'POST',
  headers: headers,
  body: JSON.stringify(data)
})
  .then(res => res.json())
  .then(json => console.log(json));
```

---

## 📊 Rate Limiting

Şu anda rate limiting yok, ancak önerilir:
- **Önerilen:** Max 100 ilan/dakika
- **Batch:** Büyük veri setlerini 10'ar 10'ar gönderin

---

## 🔧 Troubleshooting

### Webhook çağrılıyor ama paylaşım yapılmıyor

**Kontrol listesi:**
1. ✅ Platform credentials Railway'de tanımlı mı?
   ```
   Settings → Variables
   FACEBOOK_ACCESS_TOKEN = ...
   TWITTER_API_KEY = ...
   INSTAGRAM_ACCESS_TOKEN = ...
   ```

2. ✅ Görsel URL'si erişilebilir mi?
   ```bash
   curl -I https://image-url.jpg
   # HTTP/1.1 200 OK olmalı
   ```

3. ✅ Railway logs kontrol et:
   ```
   Settings → Logs
   ```

### 401 Unauthorized

**Sebep:** Secret key eşleşmiyor

**Çözüm:**
1. Railway'deki `WEBHOOK_SECRET` değerini kontrol et
2. Request header'ındaki `X-Webhook-Secret` ile karşılaştır
3. İkisi de tam olarak aynı olmalı

### 500 Internal Server Error

**Sebep:** Görsel indirilemedi veya platform hatası

**Çözüm:**
1. Görsel URL'sini test et (tarayıcıda açılıyor mu?)
2. Railway logs'a bak (detaylı hata mesajı var)
3. Platform credentials'ları kontrol et

---

## 🎓 Best Practices

### ✅ Yapılması Gerekenler
- Secret key kullan (güvenlik)
- HTTPS kullan (Railway otomatik sağlar)
- Görselleri optimize et (max 5MB)
- Error handling ekle (retry logic)

### ❌ Yapılmaması Gerekenler
- HTTP kullanma (sadece HTTPS)
- Secret key'i kodda yazma (env var kullan)
- Çok büyük görseller gönderme (>10MB)
- Saniyede 100+ ilan gönderme (rate limit)

---

## 📈 Monitoring

### Health Check
```bash
curl https://your-app.railway.app/api/health
```

Response:
```json
{
  "status": "healthy",
  "service": "SocialPublish API",
  "version": "1.0.0"
}
```

### Platform Status
```bash
curl https://your-app.railway.app/api/platforms
```

Response:
```json
{
  "facebook": {
    "name": "Facebook",
    "enabled": true,
    "icon": "📘"
  },
  "twitter": {
    "name": "Twitter",
    "enabled": true,
    "icon": "𝕏"
  },
  "instagram": {
    "name": "Instagram",
    "enabled": false,
    "icon": "📷"
  }
}
```

---

## 🔄 Gelecek Özellikler

- [ ] Rate limiting (throttling)
- [ ] Duplicate detection (aynı ilan 2 kez paylaşılmasın)
- [ ] Webhook retry logic (başarısız olursa tekrar dene)
- [ ] Scheduled posting (belirli saatte paylaş)
- [ ] Analytics (kaç ilan paylaşıldı, engagement, vb.)

---

## 📞 Destek

### API Hatası İçin
Railway logs kontrol et:
```
SocialPublish → Settings → Logs
```

### Platform Credentials
Environment variables kontrol et:
```
SocialPublish → Settings → Variables
```

---

**Railway URL:** https://your-app.railway.app  
**Webhook Endpoint:** `POST /api/webhook/share`  
**Health Check:** `GET /api/health`

