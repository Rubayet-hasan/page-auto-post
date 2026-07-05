import os
import requests
from flask import Flask

# ==================== CONFIGURATION ====================
# এখানে শুধু আপনার জেমিনি কি (Key) বসিয়ে দিন
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
# =======================================================

app = Flask(__name__)

@app.route('/')
def home():
    return "Gemini AI Test Server is running!"

def test_gemini():
    print("🤖 জেমিনি এআই টেস্ট শুরু হচ্ছে...")
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    # জেমিনিকে একটি সহজ বাংলা কবিতা লিখতে বলা হলো
    prompt = "বাংলাদেশ নিয়ে খুব সুন্দর ৪ লাইনের একটি বাংলা কবিতা লেখো।"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        # যদি চাবি ঠিক থাকে, তবে জেমিনি সুন্দর আউটপুট দেবে
        if 'candidates' in result:
            poem = result['candidates'][0]['content']['parts'][0]['text']
            print("\n======================================")
            print("✅ জেমিনি এআই সফলভাবে কাজ করছে! কবিতা নিচে দেওয়া হলো:")
            print("======================================")
            print(poem)
            print("======================================\n")
        else:
            print(f"❌ জেমিনি চাবিতে সমস্যা আছে! মেসার্জ: {result}")
    except Exception as e:
        print(f"❌ কানেকশন এরর: {e}")

# সার্ভার চালু হওয়ার সাথে সাথেই টেস্ট রান হবে
test_gemini()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
