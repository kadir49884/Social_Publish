# 📘 SocialPublish - Facebook Paylaşım Sistemi

Tek tuşla Facebook sayfanızda paylaşım yapın.

## 🚀 Kurulum

### 1. Gereksinimler
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. .env Dosyası
`.env` dosyası oluşturun:

```env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=dev-secret-key

# Facebook API
FACEBOOK_ACCESS_TOKEN=your_page_access_token
FACEBOOK_PAGE_ID=your_page_id
```

### 3. Çalıştırın
```bash
python app.py
```

Tarayıcıda: `http://localhost:5000`

## 📝 Kullanım

1. Mesajınızı yazın
2. İsterseniz görsel ekleyin
3. Paylaş butonuna tıklayın

## 🔑 Facebook Token Alma

1. https://developers.facebook.com/tools/explorer
2. App'inizi seçin
3. "Get User Access Token" → `pages_manage_posts` izni
4. Token Tool'da "Page Access Token" alın
5. Token + Page ID'yi .env'e ekleyin

## 📡 API

```bash
curl -X POST http://localhost:5000/api/publish \
  -F "message=Test mesajı" \
  -F "platforms=facebook"
```

## 📄 Lisans

MIT
