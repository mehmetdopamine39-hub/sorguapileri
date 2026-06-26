from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time
from collections import defaultdict
import json
import sys
import os

# Flask uygulamasını oluştur
app = Flask(__name__)
CORS(app)

# Rate limiting - CloudFlare koruması
rate_limits = defaultdict(list)

def rate_limit(max_requests=100, window=900):  # 15 dakika = 900 saniye
    def decorator(f):
        def decorated_function(*args, **kwargs):
            client_ip = request.remote_addr
            now = time.time()
            
            # Eski istekleri temizle
            rate_limits[client_ip] = [t for t in rate_limits[client_ip] if now - t < window]
            
            if len(rate_limits[client_ip]) >= max_requests:
                return jsonify({
                    'error': 'Çok fazla istek gönderildi, lütfen daha sonra tekrar deneyin.',
                    'api_sahibi': '@rinexdestek',
                    'api_surum': '3.7'
                }), 429
            
            rate_limits[client_ip].append(now)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# En güçlü CloudFlare koruması bypass - Headers
def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://www.google.com/',
        'Dnt': '1',
        'Connection': 'keep-alive'
    }

# Google Bot gibi davranan headers
def get_google_bot_headers():
    headers = get_headers()
    headers.update({
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
        'From': 'googlebot(at)googlebot.com',
        'Accept-Language': 'en-US,en;q=0.9'
    })
    return headers

# API yanıtına eklenecek bilgiler
def add_api_info(data):
    if isinstance(data, dict):
        data['api_sahibi'] = '@rinexdestek'
        data['api_surum'] = '3.7'
        data['not'] = 'BU APİLER BEDAVADIR, PARAYLA SATILMASI SUÇTUR'
    return data

# API endpoint'leri
@app.route('/api/tc/<tc>', methods=['GET'])
def get_tc_info(tc):
    try:
        response = requests.get(
            f'https://arastir.vip/api/tc.php?tc={tc}',
            headers=get_google_bot_headers(),
            timeout=10
        )
        data = response.json() if response.text else {}
        return jsonify(add_api_info(data))
    except Exception as e:
        return jsonify({'error': 'API hatası', 'detay': str(e), 'api_sahibi': '@rinexdestek', 'api_surum': '3.7'}), 500

@app.route('/api/adsoyad', methods=['GET'])
def get_adsoyad_info():
    try:
        adi = request.args.get('adi', '')
        soyadi = request.args.get('soyadi', '')
        il = request.args.get('il', '')
        ilce = request.args.get('ilce', '')
        
        response = requests.get(
            f'https://arastir.vip/api/adsoyad.php?adi={adi}&soyadi={soyadi}&il={il}&ilce={ilce}',
            headers=get_google_bot_headers(),
            timeout=10
        )
        data = response.json() if response.text else {}
        return jsonify(add_api_info(data))
    except Exception as e:
        return jsonify({'error': 'API hatası', 'detay': str(e), 'api_sahibi': '@rinexdestek', 'api_surum': '3.7'}), 500

@app.route('/api/adres/<tc>', methods=['GET'])
def get_adres_info(tc):
    try:
        response = requests.get(
            f'https://arastir.vip/api/adres.php?tc={tc}',
            headers=get_google_bot_headers(),
            timeout=10
        )
        data = response.json() if response.text else {}
        return jsonify(add_api_info(data))
    except Exception as e:
        return jsonify({'error': 'API hatası', 'detay': str(e), 'api_sahibi': '@rinexdestek', 'api_surum': '3.7'}), 500

@app.route('/api/gsmtc/<gsm>', methods=['GET'])
def get_gsmtc_info(gsm):
    try:
        response = requests.get(
            f'https://arastir.vip/api/gsmtc.php?gsm={gsm}',
            headers=get_google_bot_headers(),
            timeout=10
        )
        data = response.json() if response.text else {}
        return jsonify(add_api_info(data))
    except Exception as e:
        return jsonify({'error': 'API hatası', 'detay': str(e), 'api_sahibi': '@rinexdestek', 'api_surum': '3.7'}), 500

@app.route('/api/tcgsm/<tc>', methods=['GET'])
def get_tcgsm_info(tc):
    try:
        response = requests.get(
            f'https://arastir.vip/api/tcgsm.php?tc={tc}',
            headers=get_google_bot_headers(),
            timeout=10
        )
        data = response.json() if response.text else {}
        return jsonify(add_api_info(data))
    except Exception as e:
        return jsonify({'error': 'API hatası', 'detay': str(e), 'api_sahibi': '@rinexdestek', 'api_surum': '3.7'}), 500

@app.route('/api/sulale/<tc>', methods=['GET'])
def get_sulale_info(tc):
    try:
        response = requests.get(
            f'https://arastir.vip/api/sulale.php?tc={tc}',
            headers=get_google_bot_headers(),
            timeout=10
        )
        data = response.json() if response.text else {}
        return jsonify(add_api_info(data))
    except Exception as e:
        return jsonify({'error': 'API hatası', 'detay': str(e), 'api_sahibi': '@rinexdestek', 'api_surum': '3.7'}), 500

# Ana sayfa
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'api_adi': 'rinex API Servisi',
        'api_sahibi': '@rinexdestek',
        'api_surum': '3.7',
        'not': 'BU APİLER BEDAVADIR, PARAYLA SATILMASI SUÇTUR',
        'endpoints': [
            {
                'path': '/api/tc/<tc>',
                'method': 'GET',
                'ornek': 'https://api-domain.com/api/tc/12345678901',
                'aciklama': 'TC kimlik numarası ile kişi bilgilerini getirir'
            },
            {
                'path': '/api/adsoyad?adi=&soyadi=&il=&ilce=',
                'method': 'GET',
                'ornek': 'https://api-domain.com/api/adsoyad?adi=ali&soyadi=yılmaz&il=istanbul&ilce=kadıköy',
                'aciklama': 'Ad, soyad, il ve ilçe bilgileri ile kişi sorgular'
            },
            {
                'path': '/api/adres/<tc>',
                'method': 'GET',
                'ornek': 'https://api-domain.com/api/adres/12345678901',
                'aciklama': 'TC kimlik ile adres bilgilerini getirir'
            },
            {
                'path': '/api/gsmtc/<gsm>',
                'method': 'GET',
                'ornek': 'https://api-domain.com/api/gsmtc/5551234567',
                'aciklama': 'GSM numarası ile TC kimlik sorgular'
            },
            {
                'path': '/api/tcgsm/<tc>',
                'method': 'GET',
                'ornek': 'https://api-domain.com/api/tcgsm/12345678901',
                'aciklama': 'TC kimlik ile GSM numarası sorgular'
            },
            {
                'path': '/api/sulale/<tc>',
                'method': 'GET',
                'ornek': 'https://api-domain.com/api/sulale/12345678901',
                'aciklama': 'TC kimlik ile sülale/akraba bilgilerini getirir'
            }
        ]
    })

# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'api_sahibi': '@rinexdestek'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("=" * 50)
    print("🚀 rinex API Servisi Başlatılıyor...")
    print("👤 API Sahibi: @rinexdestek")
    print("📦 API Sürüm: 3.7")
    print("⚠️ BU APİLER BEDAVADIR, PARAYLA SATILMASI SUÇTUR")
    print("=" * 50)
    print(f"🌐 Sunucu http://0.0.0.0:{port} adresinde çalışıyor...")
    app.run(host='0.0.0.0', port=port, debug=False)
