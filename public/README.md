# 🚀 SocialPublish - Facebook JSON Paylaşım

Bu sayfa ile JSON formatında veri göndererek Facebook'ta otomatik paylaşım yapabilirsiniz.

## 📝 Kullanım

1. **JSON Formatı:**
```json
{
  "ilan_turu": "Kayıp",
  "baslik": "Köpeğim zeyna kayboldu acil aranıyor",
  "aciklama": "Köpeğim zeyna kocaeli körfez ilimtepe mahallesinden kaybolmuştur",
  "konum": "Kocaeli / Körfez",
  "tarih1": "22 Saat Önce",
  "tarih2": "2025-11-21T11:12:23Z",
  "kategori": "Köpek",
  "gorsel": "https://www.gorenduyan.com/images/ad/2025/11/21/202511211405-23370-36104.jpg",
  "link": "https://www.gorenduyan.com/kopegim-zeyna-kayboldu-acil-araniyor-21084"
}
```

2. **Zorunlu Alanlar:**
   - `baslik`: Facebook'ta paylaşılacak başlık
   - `gorsel`: Görsel URL'si

3. **Opsiyonel Alanlar:**
   - `aciklama`: Açıklama metni
   - `konum`: Konum bilgisi
   - Diğer alanlar önizleme için kullanılabilir

## 🔧 Backend Kurulumu

Bu sayfa çalışması için backend API'ye ihtiyaç duyar:

1. **Backend'i başlatın:**
```bash
cd ..
python app.py
```

2. **API URL'sini güncelleyin:**
   - `public/index.html` dosyasında `API_URL` değişkenini güncelleyin
   - Geliştirme: `http://localhost:5000`
   - Production: Kendi backend URL'nizi yazın

## 🌐 GitHub Pages

Bu sayfa GitHub Pages üzerinden yayınlanabilir:

1. GitHub Repo → Settings → Pages
2. Source: **Deploy from a branch**
3. Branch: **main** / **Folder: /public**
4. Save

**Sayfanız hazır:** `https://kadir49884.github.io/Social_Publish/`

## ⚠️ Önemli Notlar

- Backend API'nin çalışır durumda olması gerekir
- CORS ayarları düzgün yapılmalıdır
- Facebook Access Token geçerli olmalıdır
- Görsel URL'leri public olmalıdır

## 🔐 Güvenlik

- `.env` dosyasını asla GitHub'a yüklemeyin
- Access Token'ları güvende tutun
- Backend'i production'da HTTPS ile kullanın

---

Made with ❤️ by SocialPublish

