"""
SocialPublish - Flask Backend API
Sosyal medya paylaşım sistemi
"""
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests
import tempfile
from social_publishers import FacebookPublisher
from werkzeug.utils import secure_filename

# Environment variables yükle
load_dotenv()

# Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Upload klasörü oluştur
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Facebook Publisher
fb_publisher = FacebookPublisher()


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Ana sayfa"""
    return render_template('index.html')


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
        }
    }
    return jsonify(platforms)


@app.route('/api/publish', methods=['POST'])
def publish():
    """
    Sosyal medyada paylaşım yap
    
    Request Body:
    {
        "message": "Paylaşılacak mesaj",
        "platforms": ["facebook", "twitter"],  // optional, default: all
        "image": file  // optional
    }
    """
    try:
        # Form data al
        message = request.form.get('message')
        
        if not message:
            return jsonify({
                "success": False,
                "error": "Message is required"
            }), 400
        
        # Platform seçimi (sadece Facebook)
        platforms_str = request.form.get('platforms', '')
        if platforms_str and 'facebook' in platforms_str:
            platforms = ['facebook']
        else:
            platforms = ['facebook']
        
        # Dosya upload
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(image_path)
        
        # Facebook'ta paylaş
        result = fb_publisher.publish(
            message=message,
            image_path=image_path
        )
        
        results = {'facebook': result}
        
        # Başarı durumu kontrolü
        success = any(r.get('status') == 'success' for r in results.values())
        
        response = {
            "success": success,
            "message": "Paylaşımlar tamamlandı",
            "results": results
        }
        
        # Temp dosyayı sil
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except:
                pass
        
        return jsonify(response), 200 if success else 207  # 207 = Multi-Status
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/publish/json', methods=['POST'])
def publish_json():
    """
    JSON formatında veri al, başlık + görsel Facebook'ta paylaş
    
    Request Body (JSON):
    {
        "baslik": "Paylaşım başlığı",
        "gorsel": "https://example.com/image.jpg",
        "aciklama": "Opsiyonel açıklama",
        "konum": "Opsiyonel konum"
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
        
        # Opsiyonel alanlar
        aciklama = data.get('aciklama', '')
        konum = data.get('konum', '')
        
        # Mesajı oluştur
        message = baslik
        if aciklama:
            message += f"\n\n{aciklama}"
        if konum:
            message += f"\n\n📍 {konum}"
        
        # Görseli indir
        try:
            img_response = requests.get(gorsel_url, timeout=10)
            img_response.raise_for_status()
            
            # Geçici dosya oluştur
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            temp_file.write(img_response.content)
            temp_file.close()
            
            # Facebook'ta paylaş
            result = fb_publisher.publish(
                message=message,
                image_path=temp_file.name
            )
            
            # Temp dosyayı sil
            try:
                os.remove(temp_file.name)
            except:
                pass
            
            success = result.get('status') == 'success'
            
            return jsonify({
                "success": success,
                "result": result
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
    print(f"📍 URL: http://localhost:5000")
    print(f"📡 API: http://localhost:5000/api/publish")
    print("=" * 60)
    
    # Platform durumunu kontrol et
    print("\n🔍 Platform Durumu:")
    print(f"  Facebook: {'✅' if os.getenv('FACEBOOK_ACCESS_TOKEN') else '❌ (API anahtarı eksik)'}")
    print("\n" + "=" * 60 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=os.getenv('FLASK_DEBUG', 'True') == 'True'
    )

