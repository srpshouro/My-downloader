from flask import Flask, request, render_template, jsonify
import yt_dlp

app = Flask(__name__)

def get_direct_url(url):
    """সার্ভারে ডাউনলোড না করে সরাসরি ভিডিওর লিংক বের করার ফাংশন"""
    ydl_opts = {
        'skip_download': True, # ভিডিও সার্ভারে সেভ হবে না
        'quiet': True,
        'no_warnings': True,
        'format': 'best'
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
            
            # ডাইরেক্ট ডাউনলোড লিংক বের করা
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
