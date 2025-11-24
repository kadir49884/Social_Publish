"""
SocialPublish - Flask Backend API
Sosyal medya paylaşım sistemi
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests
import tempfile
import random
from social_publishers import FacebookPublisher, TwitterPublisher, InstagramPublisher
from werkzeug.utils import secure_filename

# Environment variables yükle
load_dotenv()

# Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Upload klasörü oluştur
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Hashtag havuzu (Türkçe karakterler normalize edilmiş)
HASHTAGS = [
    "#kayiphayvan", "#kayipkopek", "#kayipkedi", "#hayvankayip", 
    "#sokakhayvanlari", "#acilyardim", "#sahiplendir", "#hayvankoruma", 
    "#hayvansahiplenme", "#yardimcagrisi", "#petyardim", "#hayvansev", 
    "#hayvansever", "#kopekbulundu", "#kedibulundu", "#hayvanbulundu", 
    "#sosyalpet", "#petcommunity", "#pawnear", "#hayvansahipsizDEGIL", 
    "#patileripesinde", "#canlarimiziara", "#petalert", "#kayipelan", 
    "#acilduyuru", "#destekol", "#mahallename", "#sehiradi", 
    "#gorenbilenvarmi", "#hayvanlarayardim"
]

# Publishers
fb_publisher = FacebookPublisher()
tw_publisher = TwitterPublisher()
ig_publisher = InstagramPublisher()


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def normalize_turkish_chars(text: str) -> str:
    """Türkçe karakterleri İngilizce karşılıklarına çevir"""
    turkish_map = {
        'ç': 'c', 'Ç': 'C',
        'ğ': 'g', 'Ğ': 'G',
        'ı': 'i', 'İ': 'I',
        'ö': 'o', 'Ö': 'O',
        'ş': 's', 'Ş': 'S',
        'ü': 'u', 'Ü': 'U'
    }
    for tr_char, en_char in turkish_map.items():
        text = text.replace(tr_char, en_char)
    return text


def parse_custom_hashtags(hashtag_text: str) -> list:
    """Custom hashtag text'ini parse et ve Türkçe karakterleri normalize et"""
    import re
    # # ile başlayan kelimeleri bul (Türkçe karakterler dahil)
    hashtags = re.findall(r'#[\wçğıöşüÇĞİÖŞÜ]+', hashtag_text)
    # Türkçe karakterleri İngilizce'ye çevir
    normalized = [normalize_turkish_chars(tag) for tag in hashtags if len(tag) > 1]
    return normalized


def add_random_hashtags(message: str, count: int = 5, custom_hashtags: str = None) -> str:
    """Mesaja rastgele hashtag ekle"""
    if custom_hashtags:
        # Custom hashtag'leri parse et
        parsed_tags = parse_custom_hashtags(custom_hashtags)
        if parsed_tags:
            # Custom hashtag'lerden rastgele seç
            selected_tags = random.sample(parsed_tags, min(count, len(parsed_tags)))
        else:
            # Parse edilemezse default'a dön
            selected_tags = random.sample(HASHTAGS, min(count, len(HASHTAGS)))
    else:
        # Default hashtag havuzundan seç
        selected_tags = random.sample(HASHTAGS, min(count, len(HASHTAGS)))
    
    return f"{message}\n\n{' '.join(selected_tags)}"


def prepare_twitter_message(message: str, add_hashtags: bool = True, custom_hashtags: str = None) -> str:
    """Twitter için 270 karakter limitli mesaj hazırla (güvenli limit)"""
    TWITTER_LIMIT = 270
    
    if add_hashtags:
        # Hashtag'leri hazırla
        if custom_hashtags:
            parsed_tags = parse_custom_hashtags(custom_hashtags)
            selected_tags = random.sample(parsed_tags, min(5, len(parsed_tags))) if parsed_tags else random.sample(HASHTAGS, 5)
        else:
            selected_tags = random.sample(HASHTAGS, 5)
        
        hashtag_text = ' '.join(selected_tags)
        
        # Mesaj + hashtag'ler 280'i geçiyorsa kısalt
        full_message = f"{message}\n\n{hashtag_text}"
        
        if len(full_message) > TWITTER_LIMIT:
            # Hashtag'ler için yer ayır (en az 50 karakter)
            available_for_message = TWITTER_LIMIT - len(hashtag_text) - 5  # 5 = "\n\n" + "..."
            
            if available_for_message > 50:
                # Mesajı kısalt
                truncated_message = message[:available_for_message] + "..."
                return f"{truncated_message}\n\n{hashtag_text}"
            else:
                # Hashtag'ler çok uzunsa, daha az hashtag kullan
                while len(selected_tags) > 1 and len(full_message) > TWITTER_LIMIT:
                    selected_tags.pop()
                    hashtag_text = ' '.join(selected_tags)
                    full_message = f"{message}\n\n{hashtag_text}"
                
                # Hala uzunsa mesajı kısalt
                if len(full_message) > TWITTER_LIMIT:
                    available = TWITTER_LIMIT - len(hashtag_text) - 5
                    truncated = message[:available] + "..."
                    return f"{truncated}\n\n{hashtag_text}"
                
                return full_message
        
        return full_message
    else:
        # Hashtag yok, sadece mesaj
        if len(message) > TWITTER_LIMIT:
            return message[:TWITTER_LIMIT-3] + "..."
        return message


@app.route('/')
def index():
    """Ana sayfa - JSON paylaşım sayfası"""
    return send_from_directory('public', 'index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """API sağlık kontrolü - GitHub Actions için"""
    from datetime import datetime
    return jsonify({
        "status": "healthy",
        "service": "SocialPublish API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/api/platforms', methods=['GET'])
def get_platforms():
    """Desteklenen platformları listele"""
    platforms = {
        'facebook': {
            'name': 'Facebook',
            'enabled': bool(os.getenv('FACEBOOK_ACCESS_TOKEN')),
            'icon': '📘'
        },
        'twitter': {
            'name': 'Twitter',
            'enabled': bool(os.getenv('TWITTER_API_KEY') and os.getenv('TWITTER_ACCESS_TOKEN')),
            'icon': '𝕏'
        },
        'instagram': {
            'name': 'Instagram',
            'enabled': bool(os.getenv('INSTAGRAM_ACCESS_TOKEN')),
            'icon': '📷'
        }
    }
    return jsonify(platforms)


@app.route('/api/publish', methods=['POST'])
def publish():
    """
    Sosyal medyada paylaşım yap (Manuel dosya upload ile)
    
    Form Data:
    - message: str (zorunlu)
    - image: file (zorunlu)
    - platforms: JSON array string (opsiyonel)
    """
    try:
        message = request.form.get('message')
        
        if not message:
            return jsonify({
                "success": False,
                "error": "Message is required"
            }), 400
        
        # Platform seçimi
        platforms_str = request.form.get('platforms', '[]')
        try:
            import json
            selected_platforms = json.loads(platforms_str)
        except:
            selected_platforms = ['facebook']
        
        if not selected_platforms:
            selected_platforms = ['facebook']
        
        # Dosya upload
        image_path = None
        image_url = None
        
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(image_path)
        
        if not image_path:
            return jsonify({
                "success": False,
                "error": "Image is required"
            }), 400
        
        # Hashtag kontrolü
        add_hashtags = request.form.get('add_hashtags', 'true').lower() == 'true'
        custom_hashtags = request.form.get('custom_hashtags', None)
        
        # Facebook ve Instagram için tam mesaj
        message_with_tags = add_random_hashtags(message, custom_hashtags=custom_hashtags) if add_hashtags else message
        
        # Twitter için 280 karakter limitli mesaj
        twitter_message = prepare_twitter_message(message, add_hashtags, custom_hashtags)
        
        results = {}
        
        # Seçili platformlarda paylaş
        if 'facebook' in selected_platforms:
            fb_result = fb_publisher.publish(
                message=message_with_tags,
                image_path=image_path
            )
            results['facebook'] = fb_result
        
        if 'twitter' in selected_platforms:
            tw_result = tw_publisher.publish(
                message=twitter_message,  # Twitter'a özel 280 karakter limiti
                image_path=image_path
            )
            results['twitter'] = tw_result
        
        if 'instagram' in selected_platforms:
            # Instagram için dosyayı upload edip URL alalım (geçici çözüm)
            # Production'da S3/Cloudinary gibi servis kullanılmalı
            ig_result = {
                "status": "error",
                "message": "Instagram manuel dosya upload desteklemiyor. Lütfen görsel URL kullanın (JSON modu).",
                "platform": "instagram"
            }
            results['instagram'] = ig_result
        
        # Temp dosyayı sil
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except:
                pass
        
        # Başarı kontrolü
        success = any(r.get('status') == 'success' for r in results.values())
        
        return jsonify({
            "success": success,
            "message": "Paylaşımlar tamamlandı",
            "results": results
        }), 200 if success else 207
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/publish/json', methods=['POST'])
def publish_json():
    """
    JSON formatında veri al, seçili platformlarda paylaş
    
    Request Body (JSON):
    {
        "baslik": "Paylaşım başlığı",
        "gorsel": "https://example.com/image.jpg",
        "aciklama": "Opsiyonel açıklama",
        "konum": "Opsiyonel konum",
        "platforms": ["facebook", "twitter"]  // optional
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "JSON data is required"
            }), 400
        
        # Zorunlu alanlar
        baslik = data.get('baslik')
        gorsel_url = data.get('gorsel')
        
        if not baslik or not gorsel_url:
            return jsonify({
                "success": False,
                "error": "baslik ve gorsel alanları zorunludur"
            }), 400
        
            # Platform seçimi
        selected_platforms = data.get('platforms', ['facebook', 'twitter', 'instagram'])
        if isinstance(selected_platforms, str):
            selected_platforms = [selected_platforms]
        
        # Opsiyonel alanlar
        aciklama = data.get('aciklama', '')
        konum = data.get('konum', '')
        
        # Mesajı oluştur
        message = baslik
        if aciklama:
            message += f"\n\n{aciklama}"
        if konum:
            message += f"\n\n📍 {konum}"
        
        # Hashtag kontrolü
        add_hashtags = data.get('add_hashtags', True)
        custom_hashtags = data.get('custom_hashtags', None)
        
        # Facebook ve Instagram için tam mesaj
        message_with_tags = add_random_hashtags(message, custom_hashtags=custom_hashtags) if add_hashtags else message
        
        # Twitter için 280 karakter limitli mesaj
        twitter_message = prepare_twitter_message(message, add_hashtags, custom_hashtags)
        
        # Görseli indir
        try:
            img_response = requests.get(gorsel_url, timeout=10)
            img_response.raise_for_status()
            
            # Orijinal dosya uzantısını bul
            import mimetypes
            from PIL import Image
            import io
            
            content_type = img_response.headers.get('Content-Type', 'image/jpeg')
            extension = mimetypes.guess_extension(content_type) or '.jpg'
            
            # Desteklenmeyen formatları dönüştür (WebP, BMP, TIFF)
            unsupported_formats = ['.webp', '.bmp', '.tiff', '.tif']
            needs_conversion = extension.lower() in unsupported_formats and 'instagram' in selected_platforms
            
            if needs_conversion:
                # Instagram için JPEG'e dönüştür
                img = Image.open(io.BytesIO(img_response.content))
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Transparency varsa beyaz background ekle
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # JPEG olarak kaydet (yüksek kalite)
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                img.save(temp_file.name, 'JPEG', quality=95, optimize=True)
                temp_file.close()
            else:
                # Orijinal formatta kaydet
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=extension)
                temp_file.write(img_response.content)
                temp_file.close()
            
            results = {}
            
            # Seçili platformlarda paylaş
            if 'facebook' in selected_platforms:
                fb_result = fb_publisher.publish(
                    message=message_with_tags,
                    image_path=temp_file.name
                )
                results['facebook'] = fb_result
                print(f"✅ Facebook: {fb_result}")
            
            if 'twitter' in selected_platforms:
                tw_result = tw_publisher.publish(
                    message=twitter_message,  # Twitter'a özel 280 karakter limiti
                    image_path=temp_file.name
                )
                results['twitter'] = tw_result
                print(f"🐦 Twitter: {tw_result}")
            
            if 'instagram' in selected_platforms:
                ig_result = ig_publisher.publish(
                    message=message_with_tags,
                    image_path=gorsel_url  # Instagram URL istiyor, lokal path değil
                )
                results['instagram'] = ig_result
                print(f"📷 Instagram: {ig_result}")
            
            # Temp dosyayı sil
            try:
                os.remove(temp_file.name)
            except:
                pass
            
            # Başarı kontrolü
            success = any(r.get('status') == 'success' for r in results.values())
            
            return jsonify({
                "success": success,
                "results": results
            }), 200 if success else 400
            
        except requests.exceptions.RequestException as e:
            return jsonify({
                "success": False,
                "error": f"Görsel indirilemedi: {str(e)}"
            }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# Static files
@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('static', filename)


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 SocialPublish API Başlatılıyor...")
    print("=" * 60)
    
    # Railway için port
    port = int(os.getenv('PORT', 5000))
    
    print(f"📍 Port: {port}")
    print(f"📡 API: /api/publish")
    print("=" * 60)
    
    # Platform durumunu kontrol et
    print("\n🔍 Platform Durumu:")
    print(f"  Facebook: {'✅' if os.getenv('FACEBOOK_ACCESS_TOKEN') else '❌ (API anahtarı eksik)'}")
    print("\n" + "=" * 60 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('FLASK_DEBUG', 'False') == 'True'
    )

