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
app = Flask(__name__, static_folder='static')
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Upload klasörü oluştur
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Hashtag havuzu
HASHTAGS = [
    "#kayıphayvan", "#kayıpköpek", "#kayıpkedi", "#hayvankayıp", 
    "#sokakhayvanları", "#acilyardım", "#sahiplendir", "#hayvankoruma", 
    "#hayvansahiplenme", "#yardımçağrısı", "#petyardım", "#hayvansev", 
    "#hayvansever", "#köpekbulundu", "#kedibulundu", "#hayvanbulundu", 
    "#sosyalpet", "#petcommunity", "#pawnear", "#hayvansahipsizdeğil", 
    "#patileripeşinde", "#canlarimiziara", "#petalert", "#kayıpelan", 
    "#acilduyuru", "#destekol", "#mahallename", "#şehiradı", 
    "#görenbilenvarmı", "#hayvanlarayardım"
]

# Publishers
fb_publisher = FacebookPublisher()
tw_publisher = TwitterPublisher()
ig_publisher = InstagramPublisher()


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def add_random_hashtags(message: str, count: int = 5) -> str:
    """Mesaja rastgele hashtag ekle"""
    selected_tags = random.sample(HASHTAGS, min(count, len(HASHTAGS)))
    return f"{message}\n\n{' '.join(selected_tags)}"


@app.route('/')
def index():
    """Ana sayfa - JSON paylaşım sayfası"""
    return send_from_directory('public', 'index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "SocialPublish API",
        "version": "1.0.0"
    })


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
        
        # Rastgele hashtag ekle
        message_with_tags = add_random_hashtags(message)
        
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
                message=message_with_tags,
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
        
        # Rastgele hashtag ekle
        message_with_tags = add_random_hashtags(message)
        
        # Görseli indir
        try:
            img_response = requests.get(gorsel_url, timeout=10)
            img_response.raise_for_status()
            
            # Geçici dosya oluştur
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
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
                    message=message_with_tags,
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

