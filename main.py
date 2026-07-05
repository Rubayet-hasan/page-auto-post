import os
import requests
from flask import Flask

# ==================== CONFIGURATION ====================
# আপনার স্ক্রিনশটের চাবিটি (API Key) নিচে নিখুঁতভাবে বসানো হয়েছে
GEMINI_API_KEY = "AIzaSyAQ.Ab8RN6LG3WfN0fJEx6Ac17-SR5YaEuDajBELpVidBCBGNkxZbQ"
# =======================================================

app = Flask(__name__)

@app.route('/')
def home():
    return "Gemini AI Test Server is running successfully!"

def test_gemini():
    print("🤖 জেমিনি এআই টেস্ট শুরু হচ্ছে...")
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    # একটি সহজ টেস্ট প্রম্পট
    prompt = "বাংলাদেশ নিয়ে খুব সুন্দর ৪ লাইনের একটি কবিতা লেখো।"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        # যদি চাবি সঠিক থাকে তবে এখানে কবিতা প্রিন্ট হবে
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

# সার্ভার স্টার্ট হলেই প্রথমবার টেস্ট রান হবে
test_gemini()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
