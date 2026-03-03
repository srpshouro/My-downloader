from flask import Flask, request, render_template, jsonify, Response, stream_with_context
import yt_dlp
import requests
import urllib.parse

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract():
    data = request.get_json()
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'status': 'error', 'message': 'URL is required'})
        
    # শুধুমাত্র yt-dlp ব্যবহার করা হচ্ছে
    ydl_opts = {
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
        # ইউটিউব বট এরর থেকে বাঁচতে মোবাইল ক্লায়েন্ট
        'extractor_args': {'youtube': {'player_client': ['android', 'ios']}}
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if 'entries' in info:
                info = info['entries'][0]
                
            direct_url = info.get('url')
            if not direct_url and 'requested_downloads' in info:
                direct_url = info['requested_downloads'][0].get('url')
                
            if direct_url:
                title = info.get('title', 'Video').replace('/', '_').replace('\\', '_')
                ext = info.get('ext', 'mp4')
                filename = f"{title}.{ext}"
                
                # সরাসরি লিংক না দিয়ে আমাদের সার্ভারের প্রক্সি লিংক দিচ্ছি
                encoded_url = urllib.parse.quote(direct_url, safe='')
                encoded_filename = urllib.parse.quote(filename, safe='')
                
                proxy_url = f"/stream?url={encoded_url}&name={encoded_filename}"
                
                return jsonify({
                    'status': 'success',
                    'title': title,
                    'proxy_url': proxy_url
                })
            else:
                return jsonify({'status': 'error', 'message': 'Could not extract direct link'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/stream')
def stream():
    """এই ফাংশনটি ভিডিওটি Vercel এ সেভ না করে সরাসরি ইউজারের ফোনে ডাউনলোড করে দিবে"""
    direct_url = request.args.get('url')
    filename = request.args.get('name', 'video.mp4')
    
    if not direct_url:
        return "No URL provided", 400
        
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # মেইন সার্ভার থেকে ভিডিও আনা হচ্ছে
        req = requests.get(direct_url, stream=True, headers=headers)
        
        # ইউজারের ফোনে সরাসরি ডাউনলোড হিসেবে পাঠানো হচ্ছে
        response = Response(stream_with_context(req.iter_content(chunk_size=1024*1024)), content_type=req.headers.get('content-type', 'video/mp4'))
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
