from flask import Flask, request, render_template, jsonify
import yt_dlp
import requests

app = Flask(__name__)

def get_tiktok_url(url):
    """শুধুমাত্র টিকটকের জন্য বিশেষ API (যাতে IP ব্লক না হয় এবং Watermark না থাকে)"""
    try:
        api_url = f"https://www.tikwm.com/api/?url={url}"
        response = requests.get(api_url).json()
        
        if response.get('code') == 0:
            data = response['data']
            return {
                'status': 'success',
                'title': data.get('title', 'TikTok Video'),
                'thumbnail': data.get('cover', ''),
                'download_url': data.get('play', ''), 
                'platform': 'TikTok'
            }
        return {'status': 'error', 'message': 'TikTok video not found or private!'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def get_direct_url(url):
    """অন্যান্য সোশ্যাল মিডিয়ার জন্য yt-dlp"""
    
    # যদি টিকটকের লিংক হয়, তবে আমাদের স্পেশাল ফাংশনে পাঠাবে
    if 'tiktok.com' in url.lower():
        return get_tiktok_url(url)
        
    ydl_opts = {
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
        # ইউটিউবকে বোকা বানানোর জন্য Android Client ব্যবহার করছি
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios']
            }
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # প্লেলিস্ট হলে প্রথম ভিডিওর ইনফো নিবে
            if 'entries' in info:
                info = info['entries'][0]
                
            title = info.get('title', 'Social Media Video')
            thumbnail = info.get('thumbnail', '')
            platform = info.get('extractor_key', 'Unknown')
            
            direct_url = info.get('url')
            if not direct_url and 'requested_downloads' in info:
                direct_url = info['requested_downloads'][0].get('url')
                
            if direct_url:
                return {
                    'status': 'success',
                    'title': title,
                    'thumbnail': thumbnail,
                    'download_url': direct_url,
                    'platform': platform
                }
            else:
                return {'status': 'error', 'message': 'Direct link not found!'}
                
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'status': 'error', 'message': 'URL is required'})
    
    result = get_direct_url(url)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
