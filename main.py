import os
import requests
from flask import Flask

# ==================== CONFIGURATION ====================
# রেন্ডারের Environment Variables থেকে সিক্রেট কি-গুলো নেওয়া হচ্ছে
GEMINI_API_KEY = os.environ.get("api_key")
FB_PAGE_ID = os.environ.get("fb_page_id")
FB_ACCESS_TOKEN = os.environ.get("fb_access_token")
# =======================================================

app = Flask(__name__)

@app.route('/')
def home():
    return "Facebook Auto-Post Bot is Running Successfully!"

# ১. জেমিনি থেকে কনটেন্ট জেনারেট করার ফাংশন
def generate_ai_content():
    if not GEMINI_API_KEY:
        print("❌ এরর: রেন্ডারের Environment-এ 'api_key' খুঁজে পাওয়া যায়নি!")
        return None

    # জেমিনি ২.৫ ফ্ল্যাশ মডেলের সঠিক অফিশিয়াল এন্ডপয়েন্ট
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    # বোটকে দেওয়া প্রম্পট
    prompt = "ফেসবুক পেজের জন্য একটি সুন্দর শিক্ষণীয় বা মোটিভেশনাল স্ট্যাটাস লেখো (২-৩ লাইনের মধ্যে, সাথে রিলেভেন্ট হ্যাশট্যাগ)। কোনো বাড়তি কথা বা ইন্ট্রো ছাড়া শুধু মেইন পোস্টটুকু দেবে।"
    
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        if 'candidates' in result:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            print(f"❌ জেমিনি রেসপন্স এরর! সম্পূর্ণ মেসেজ: {result}")
    except Exception as e:
        print(f"❌ জেমিনি থেকে কনটেন্ট তৈরিতে সমস্যা: {e}")
    return None

# ২. ফেসবুকে পোস্ট করার ফাংশন
def post_to_facebook(message):
    if not FB_PAGE_ID or not FB_ACCESS_TOKEN:
        print("❌ এরর: ফেসবুক Page ID বা Access Token সেট করা নেই!")
        print("দয়া করে রেন্ডারের Environment ট্যাবে fb_page_id এবং fb_access_token সেট করুন।")
        return

    # ফেসবুক গ্রাফ এপিআই ইউআরএল
    url = f"https://graph.facebook.com/v18.0/{FB_PAGE_ID}/feed"
    payload = {
        'message': message,
        'access_token': FB_ACCESS_TOKEN
    }
    
    try:
        response = requests.post(url, data=payload)
        result = response.json()
        
        if 'id' in result:
            print("\n======================================")
            print(f"✅ ফেসবুকে সফলভাবে পোস্ট হয়েছে! পোস্ট আইডি: {result['id']}")
            print("======================================\n")
        else:
            print(f"❌ ফেসবুক পোস্ট এরর! মেসেজ: {result}")
    except Exception as e:
        print(f"❌ ফেসবুকের সাথে কানেক্ট করা যায়নি: {e}")

# বোট চালু হলেই টেস্ট রান শুরু হবে
print("🚀 ফেসবুক অটো-পোস্ট বোট স্টার্ট হচ্ছে...")
ai_text = generate_ai_content()
if ai_text:
    print(f"📝 জেমিনি যে লেখাটি তৈরি করেছে:\n\n{ai_text}\n")
    post_to_facebook(ai_text)
else:
    print("❌ জেনারেট করা টেক্সট খালি থাকায় ফেসবুকে পোস্ট করা যায়নি।")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
