import os
import requests
from flask import Flask

# ==================== CONFIGURATION ====================
GEMINI_API_KEY = os.environ.get("api_key")
# =======================================================

app = Flask(__name__)

@app.route('/')
def home():
    return "Gemini AI Production Server is running successfully!"

def test_gemini():
    print("🤖 জেমিনি এআই টেস্ট শুরু হচ্ছে...")
    
    if not GEMINI_API_KEY:
        print("❌ এরর: রেন্ডারের Environment-এ 'api_key' খুঁজে পাওয়া যায়নি!")
        return

    # এখানে আমরা লেটেস্ট gemini-1.5-flash-latest মডেলটি ব্যবহার করছি যা ৪০০ এরর দেবে না
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
    
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
            # যদি তাও সমস্যা হয়, আমরা ব্যাকআপ হিসেবে gemini-2.5-flash ট্রাই করব স্বয়ংক্রিয়ভাবে
            print("🔄 মডেল পরিবর্তন করে gemini-2.5-flash ট্রাই করা হচ্ছে...")
            backup_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
            backup_response = requests.post(backup_url, headers=headers, json=data)
            backup_result = backup_response.json()
            
            if 'candidates' in backup_result:
                poem = backup_result['candidates'][0]['content']['parts'][0]['text']
                print("\n======================================")
                print("✅ জেমিনি ২.৫ সফলভাবে কাজ করছে! কবিতা নিচে দেওয়া হলো:")
                print("======================================")
                print(poem)
                print("======================================\n")
            else:
                print(f"❌ জেমিনি রেসপন্স এরর! সম্পূর্ণ মেসেজ: {backup_result}")
    except Exception as e:
        print(f"❌ কানেকশন এরর: {e}")

test_gemini()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
