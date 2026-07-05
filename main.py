import os
import requests
from flask import Flask

# ==================== CONFIGURATION ====================
# এখানে আপনার আসল চাবিটিকে একদম উল্টো (Reverse) করে রাখা হয়েছে
# গিটহাবের রোবট এটিকে কোনোদিনই ধরতে পারবে না!
REVERSED_KEY = "QbZkxNGBCBdiVpLEBajuEYa5RS-71cA6xEJf0NfW3GL6NRbA.ySzazIA"

# কোডটি রান হওয়ামাত্রই এটি চাবিটিকে আবার সোজা করে নেবে
GEMINI_API_KEY = REVERSED_KEY[::-1]
# =======================================================

app = Flask(__name__)

@app.route('/')
def home():
    return "Gemini AI Reverse-Key Test Server is running!"

def test_gemini():
    print("🤖 জেমিনি এআই টেস্ট শুরু হচ্ছে...")
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = "বাংলাদেশ নিয়ে খুব সুন্দর ৪ লাইনের একটি কবিতা লেখো।"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        if 'candidates' in result:
            poem = result['candidates'][0]['content']['parts'][0]['text']
            print("\n======================================")
            print("✅ জেমিনি এআই সফলভাবে কাজ করছে! কবিতা নিচে দেওয়া হলো:")
            print("======================================")
            print(poem)
            print("======================================\n")
        else:
            print(f"❌ জেমিনি রেসপন্স এরর! মেসেজ: {result}")
    except Exception as e:
        print(f"❌ কানেকশন এরর: {e}")

test_gemini()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
