from flask import Flask, request, jsonify
import requests
import os
import time
from collections import defaultdict

app = Flask(__name__)

# Rate limiting
rate_limits = defaultdict(list)

def rate_limit(max_requests=100, window=900):
    def decorator(f):
        def decorated_function(*args, **kwargs):
            client_ip = request.remote_addr
            now = time.time()
            
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

# CloudFlare bypass headers
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

def get_google_bot_headers():
    headers = get_headers()
    headers.update({
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
        'From': 'googlebot(at)googlebot.com',
    })
    return headers

# API bilgisi ekle
def add_api_info(data):
    if isinstance(data, dict):
        data['api_sahibi'] = '@rinexdestek'
        data['api_surum'] = '3.7'
        data['not'] = 'BU APİLER BEDAVADIR, PARAYLA SATILMASI SUÇTUR'
    return data

# ============ ANA API ENDPOINT'LERİ ============

@app.route('/api/tc.php', methods=['GET'])
@rate_limit()
def tc_api():
    """TC ile sorgulama - /api/tc.php?tc=12345678901"""
    tc = request.args.get('tc', '').strip()
    
    if not tc:
        return jsonify({
            'success': False,
            'message': 'TC parametresi gerekli',
            'usage': '/api/tc.php?tc=TC_NUMARASI',
            'example': '/api/tc.php?tc=12345678901',
            'api_sahibi': '@rinexdestek',
            'api_surum': '3.7'
        }), 400
    
    try:
        response = requests.get(
            f'https://arastir.vip/api/tc.php?tc={tc}',
            headers=get_google_bot_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json() if response.text else {}
            return jsonify(add_api_info(data))
        else:
            return jsonify({
                'success': False,
                'error': f'API yanıt vermedi (HTTP {response.status_code})',
                'tc': tc,
                'api_sahibi': '@rinexdestek',
                'api_surum': '3.7'
            }), response.status_code
            
    except requests.Timeout:
        return jsonify({
            'success': False,
            'error': 'API zaman aşımına uğradı',
            'tc': tc,
            'api_sahibi': '@rinexdestek',
            'api_surum': '3.7'
        }), 504
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'tc': tc,
            'api_sahibi': '@rinexdestek',
            'api_surum': '3.7'
        }), 500

@app.route('/api/adsoyad.php', methods=['GET'])
@rate_limit()
def adsoyad_api():
    """Ad-Soyad ile sorgulama - /api/adsoyad.php?adi=ali&soyadi=yılmaz"""
    adi = request.args.get('adi', '').strip()
    soyadi = request.args.get('soyadi', '').strip()
    il = request.args.get('il', '').strip()
    ilce = request.args.get('ilce', '').strip()
    
    if not adi and not soyadi:
        return jsonify({
            'success': False,
            'message': 'Ad veya soyad parametresi gerekli',
            'usage': '/api/adsoyad.php?adi=AD&soyadi=SOYAD&il=IL&ilce=ILCE',
            'example': '/api/adsoyad.php?adi=ali&soyadi=yılmaz&il=istanbul',
            'api_sahibi': '@rinexdestek',
            'api_surum': '3.7'
        }), 400
    
    try:
        url = f'https://arastir.vip/api/adsoyad.php?adi={adi}&soyadi={soyadi}&il={il}&ilce={ilce}'
        response = requests.get(url, headers=get_google_bot_headers(), timeout=10)
        
        if response.status_code == 200:
            data = response.json() if response.text else {}
            return jsonify(add_api_info(data))
        else:
            return jsonify({
                'success': False,
                'error': f'API yanıt vermedi (HTTP {response.status_code})',
                'api_sahibi': '@rinexdestek',
                'api_surum': '3.7'
            }), response.status_code
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'api_sahibi': '@rinexdestek',
            'api_surum': '3.7'
        }), 500

@app.route('/api/adres.php', methods=['GET'])
@rate_limit()
def adres_api():
    """Adres sorgulama - /api/adres.php?tc=12345678901"""
    tc = request.args.get('tc', '').strip()
    
    if not tc:
        return jsonify({
            'success': False,
            'message': 'TC parametresi gerekli',
            'usage': '/api/adres.php?tc=TC_NUMARASI',
            'example': '/api/adres.php?tc=12345678901',
            'api_sahibi': '@rinexdestek',
            'api_surum': '3.7'
        }), 400
    
    try:
        response = requests.get(
            f'https://arastir.vip/api/adres.php?tc={tc}',
            headers=get_google_bot_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json() if response.text else {}
            return jsonify(add_api_info(data))
        else:
            return jsonify({
                'success': False,
                'error': f'API yanıt vermedi (HTTP {response.status_code})',
                'tc': tc,
                'api_sahibi': '@rinexdestek',
                'api_surum': '3.7'
            }), response.status_code
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'tc': tc,
            'api_sahibi': '@rinexdestek',
            'api_surum': '3.7'
        }), 500

@app.route('/api/gsmtc.php', methods=['GET'])
@rate_limit()
def gsmtc_api():
    """GSM ile TC sorgulama - /api/gsmtc.php?gsm=5551234567"""
    gsm = request.args.get('gsm', '').strip()
    
    if not gsm:
        return jsonify({
            'success': False,
            'message': 'GSM parametresi gerekli',
            'usage': '/api/gsmtc.php?gsm=GSM_NUMARASI',
            'example': '/api/gsmtc.php?gsm=5551234567',
            'api_sahibi': '@rinexdestek',
            'api_surum': '3.7'
        }), 400
    
    try:
        response = requests.get(
            f'https://arastir.vip/api/gsmtc.php?gsm={gsm}',
            headers=get_google_bot_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json() if response.text else {}
            return jsonify(add_api_info(data))
        else:
            return jsonify({
                'success': False,
                'error': f'API yanıt vermedi (HTTP {response.status_code})',
                'gsm': gsm,
                'api_sahibi': '@rinexdestek',
                'api_surum': '3.7'
            }), response.status_code
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'gsm': gsm,
            'api_sahibi': '@rinexdestek',
            'api_surum': '3.7'
        }), 500

@app.route('/api/tcgsm.php', methods=['GET'])
@rate_limit()
def tcgsm_api():
    """TC ile GSM sorgulama - /api/tcgsm.php?tc=12345678901"""
    tc = request.args.get('tc', '').strip()
    
    if not tc:
        return jsonify({
            'success': False,
            'message': 'TC parametresi gerekli',
            'usage': '/api/tcgsm.php?tc=TC_NUMARASI',
            'example': '/api/tcgsm.php?tc=12345678901',
            'api_sahibi': '@rinexdestek',
            'api_surum': '3.7'
        }), 400
    
    try:
        response = requests.get(
            f'https://arastir.vip/api/tcgsm.php?tc={tc}',
            headers=get_google_bot_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json() if response.text else {}
            return jsonify(add_api_info(data))
        else:
            return jsonify({
                'success': False,
                'error': f'API yanıt vermedi (HTTP {response.status_code})',
                'tc': tc,
                'api_sahibi': '@rinexdestek',
                'api_surum': '3.7'
            }), response.status_code
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'tc': tc,
            'api_sahibi': '@rinexdestek',
            'api_surum': '3.7'
        }), 500

@app.route('/api/sulale.php', methods=['GET'])
@rate_limit()
def sulale_api():
    """Sülale sorgulama - /api/sulale.php?tc=12345678901"""
    tc = request.args.get('tc', '').strip()
    
    if not tc:
        return jsonify({
            'success': False,
            'message': 'TC parametresi gerekli',
            'usage': '/api/sulale.php?tc=TC_NUMARASI',
            'example': '/api/sulale.php?tc=12345678901',
            'api_sahibi': '@rinexdestek',
            'api_surum': '3.7'
        }), 400
    
    try:
        response = requests.get(
            f'https://arastir.vip/api/sulale.php?tc={tc}',
            headers=get_google_bot_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json() if response.text else {}
            return jsonify(add_api_info(data))
        else:
            return jsonify({
                'success': False,
                'error': f'API yanıt vermedi (HTTP {response.status_code})',
                'tc': tc,
                'api_sahibi': '@rinexdestek',
                'api_surum': '3.7'
            }), response.status_code
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'tc': tc,
            'api_sahibi': '@rinexdestek',
            'api_surum': '3.7'
        }), 500

# ============ ANA SAYFA ============
@app.route('/')
def home():
    return jsonify({
        'api_adi': 'rinex API Servisi',
        'api_sahibi': '@rinexdestek',
        'api_surum': '3.7',
        'not': 'BU APİLER BEDAVADIR, PARAYLA SATILMASI SUÇTUR',
        'endpoints': [
            {
                'path': '/api/tc.php',
                'method': 'GET',
                'params': {'tc': 'TC kimlik numarası'},
                'ornek': '/api/tc.php?tc=12345678901',
                'aciklama': 'TC ile kişi bilgilerini getirir'
            },
            {
                'path': '/api/adsoyad.php',
                'method': 'GET',
                'params': {'adi': 'Ad', 'soyadi': 'Soyad', 'il': 'İl', 'ilce': 'İlçe'},
                'ornek': '/api/adsoyad.php?adi=ali&soyadi=yılmaz&il=istanbul',
                'aciklama': 'Ad-Soyad ile kişi sorgular'
            },
            {
                'path': '/api/adres.php',
                'method': 'GET',
                'params': {'tc': 'TC kimlik numarası'},
                'ornek': '/api/adres.php?tc=12345678901',
                'aciklama': 'TC ile adres bilgilerini getirir'
            },
            {
                'path': '/api/gsmtc.php',
                'method': 'GET',
                'params': {'gsm': 'GSM numarası'},
                'ornek': '/api/gsmtc.php?gsm=5551234567',
                'aciklama': 'GSM ile TC kimlik sorgular'
            },
            {
                'path': '/api/tcgsm.php',
                'method': 'GET',
                'params': {'tc': 'TC kimlik numarası'},
                'ornek': '/api/tcgsm.php?tc=12345678901',
                'aciklama': 'TC ile GSM numarası sorgular'
            },
            {
                'path': '/api/sulale.php',
                'method': 'GET',
                'params': {'tc': 'TC kimlik numarası'},
                'ornek': '/api/sulale.php?tc=12345678901',
                'aciklama': 'TC ile sülale bilgilerini getirir'
            }
        ],
        'ornek_kullanim': {
            'python': """
import requests

# TC sorgulama
response = requests.get('https://api-domain.com/api/tc.php?tc=12345678901')
print(response.json())

# GSM sorgulama
response = requests.get('https://api-domain.com/api/gsmtc.php?gsm=5551234567')
print(response.json())
            """,
            'javascript': """
// TC sorgulama
fetch('https://api-domain.com/api/tc.php?tc=12345678901')
  .then(response => response.json())
  .then(data => console.log(data));
            """
        }
    })

@app.route('/health')
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
    print("\n📌 Kullanım Örnekleri:")
    print(f"  TC sorgula: http://localhost:{port}/api/tc.php?tc=12345678901")
    print(f"  GSM sorgula: http://localhost:{port}/api/gsmtc.php?gsm=5551234567")
    print(f"  Adres sorgula: http://localhost:{port}/api/adres.php?tc=12345678901")
    print("=" * 50)
    app.run(host='0.0.0.0', port=port, debug=False)
