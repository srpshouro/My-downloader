from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# 🚀 এটি হলো আপনার নিজস্ব API Endpoint
@app.route('/alldown', methods=['GET'])
def alldown():
    url = request.args.get('url')
    
    if not url:
        return jsonify({
            "creator": "Your Name (Admin)",
            "status": False,
            "message": "URL is missing! Usage: /alldown?url=YOUR_LINK"
        }), 400

    try:
        # --- TIKTOK API LOGIC ---
        if 'tiktok.com' in url.lower():
            api_url = f"https://www.tikwm.com/api/?url={url}"
            res = requests.get(api_url).json()
            
            if res.get('code') == 0:
                data = res['data']
                return jsonify({
                    "creator": "Your Name (Admin)",
                    "status": True,
                    "platform": "TikTok",
                    "title": data.get('title', 'TikTok Video'),
                    "watermark_free_video": data.get('play', ''),
                    "audio_link": data.get('music', '')
                })
            else:
                return jsonify({"status": False, "message": "TikTok video not found!"})

        # --- YOUTUBE, FACEBOOK, INSTAGRAM LOGIC ---
        else:
            # আমরা ব্যাকএন্ডে Cobalt API ব্যবহার করছি, কিন্তু ইউজার সেটা বুঝবে না
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            payload = {
                "url": url,
                "filenamePattern": "classic"
            }
            
            res = requests.post('https://api.cobalt.tools/api/json', json=payload, headers=headers).json()
            
            if res.get('status') == 'error':
                return jsonify({
                    "creator": "Your Name (Admin)",
                    "status": False,
                    "message": "Video is private or unsupported."
                })
                
            return jsonify({
                "creator": "Your Name (Admin)",
                "status": True,
                "platform": "YouTube/FB/Insta",
                "download_link": res.get('url', '')
            })

    except Exception as e:
        return jsonify({
            "creator": "Your Name (Admin)",
            "status": False,
            "message": f"Server Error: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
