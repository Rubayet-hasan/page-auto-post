import os
import requests
from flask import Flask

# ==================== CONFIGURATION ====================
# কোডের ভেতর কোনো চাবি নেই! এটি সরাসরি রেন্ডারের এনভায়রনমেন্ট থেকে চাবিটি টেনে নেবে।
# গিটহাব এখন আর কিছুই ধরতে পারবে না।
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
# =======================================================

app = Flask(__name__)

@app.route('/')
def home():
    return "Gemini AI Test Server is running successfully!"

def test_gemini():
    print("🤖 জেমিনি এআই টেস্ট শুরু হচ্ছে...")
    
    if not GEMINI_API_KEY:
        print("❌ এরর: রেন্ডারের Environment Variables-এ GEMINI_API_KEY পাওয়া যায়নি!")
        return

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
