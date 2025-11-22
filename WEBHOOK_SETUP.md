# SocialPublish Webhook Entegrasyonu

## 🎯 Amaç
Scraper'ın bulduğu ilanları otomatik olarak SocialPublish'e göndermek ve Facebook, Twitter, Instagram'da paylaşmak.

---

## 📋 Kurulum Adımları

### 1. Railway'de Environment Variables Ekle

SocialPublish projesine git:
```
Settings → Variables
```

Ekle:
```
WEBHOOK_SECRET=your-super-secret-key-here-12345
```

**Not:** `WEBHOOK_SECRET` opsiyoneldir ama güvenlik için ekleyin.

---

### 2. GitHub Secrets Ekle

ScraperPawNear projesinde:
```
Settings → Secrets and variables → Actions → New repository secret
```

Eklenecekler:
```
WEBHOOK_URL = https://your-app.railway.app/api/webhook/share
WEBHOOK_SECRET = your-super-secret-key-here-12345
```

**Not:** Railway URL'inizi `https://your-app.railway.app` ile değiştirin.

---

## 🚀 Kullanım

### Otomatik (Zamanlanmış)
GitHub Actions her gün saat 12:00'de (TR saati) otomatik çalışır:
1. İlanları scrape eder
2. `data/ilan_taramasi_YYYY-MM-DD.json` dosyasına kaydeder
3. SocialPublish'e POST eder
4. Otomatik paylaşılır

### Manuel Test
GitHub Actions sekmesinde:
```
Actions → Günlük İlan Scraper → Run workflow
```

---

## 🔧 API Detayları

### Endpoint
```
POST /api/webhook/share
```

### Headers
```json
{
  "Content-Type": "application/json",
  "X-Webhook-Secret": "your-secret-key"
}
```

### Body (Tek İlan)
```json
{
  "baslik": "Köpeğim kayboldu",
  "gorsel": "https://example.com/image.jpg",
  "aciklama": "Açıklama metni",
  "konum": "İstanbul / Kadıköy",
  "kategori": "Köpek"
}
```

### Body (Çoklu İlan)
```json
[
  {
    "baslik": "İlan 1",
    "gorsel": "https://...",
    ...
  },
  {
    "baslik": "İlan 2",
    "gorsel": "https://...",
    ...
  }
]
```

### Response
```json
{
  "success": true,
  "total": 10,
  "success_count": 9,
  "failed_count": 1,
  "results": [...]
}
```

---

## ✅ Test

### 1. Manuel Test (Terminal)
```bash
cd ScraperPawNear
python send_socialpublish.py
```

### 2. cURL Test
```bash
curl -X POST https://your-app.railway.app/api/webhook/share \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: your-secret" \
  -d '{
    "baslik": "Test İlanı",
    "gorsel": "https://via.placeholder.com/600x400",
    "aciklama": "Test açıklaması",
    "konum": "Test / Lokasyon",
    "kategori": "Köpek"
  }'
```

---

## 🔒 Güvenlik

- ✅ `WEBHOOK_SECRET` kullanın (zorunlu değil ama önerilir)
- ✅ Railway'de HTTPS otomatik aktif
- ✅ GitHub Secrets güvenli şekilde saklanır
- ✅ Secret key'leri asla kodda yazmayın

---

## 📝 Notlar

1. **Hashtag'ler:** Webhook üzerinden gelen paylaşımlara otomatik hashtag eklenir
2. **Platformlar:** Aktif olan tüm platformlarda (Facebook, Twitter, Instagram) paylaşılır
3. **Rate Limit:** Çok fazla ilan varsa sırayla paylaşılır
4. **Error Handling:** Bir ilan hata verse bile diğerleri paylaşılmaya devam eder

---

## 🐛 Sorun Giderme

### Webhook çalışmıyor
1. Railway'deki `WEBHOOK_SECRET` doğru mu?
2. GitHub Secrets'taki `WEBHOOK_URL` doğru mu?
3. Railway app çalışıyor mu? (Health check: `/api/health`)

### Paylaşım yapılmıyor
1. Platform credentials (Facebook, Twitter, Instagram) Railway'de tanımlı mı?
2. Railway logs'a bakın: `Settings → Logs`
3. GitHub Actions logs'a bakın: `Actions → son workflow → logs`

---

## ✨ Gelecek İyileştirmeler

- [ ] Rate limiting (çok fazla ilan gelirse yavaşlat)
- [ ] Duplicate kontrolü (aynı ilan 2 kez paylaşılmasın)
- [ ] Öncelik sistemi (yeni ilanlar önce)
- [ ] Webhook retry mekanizması (başarısız olursa tekrar dene)

