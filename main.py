import os
import requests
import time
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler  # টাইমারের জন্য যোগ করা হয়েছে

# ==================== CONFIGURATION ====================
GEMINI_API_KEY = os.environ.get("api_key")
FB_PAGE_ID = os.environ.get("fb_page_id")
FB_ACCESS_TOKEN = os.environ.get("fb_access_token")
# =======================================================

app = Flask(__name__)

@app.route('/')
def home():
    return "Facebook Auto-Post Bot is Running with Timer!"

# ১. জেমিনি থেকে কনটেন্ট জেনারেট করার ফাংশন
def generate_ai_content():
    if not GEMINI_API_KEY:
        print("❌ এরর: 'api_key' খুঁজে পাওয়া যায়নি!")
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = "ফেসবুক পেজের জন্য একটি সুন্দর শিক্ষণীয় বা মোтивнойেশনাল স্ট্যাটাস লেখো (২-৩ লাইনের মধ্যে, সাথে রিলেভেন্ট হ্যাশট্যাগ)। কোনো বাড়তি কথা বা ইন্ট্রো ছাড়া শুধু মেইন পোস্টটুকু দেবে।"
    
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            
            if 'candidates' in result:
                return result['candidates'][0]['content']['parts'][0]['text']
            
            if 'error' in result and result['error'].get('code') == 503:
                print(f"⚠️ গুগলের সার্ভার ব্যস্ত (Attempt {attempt + 1}/{max_retries})। ১০ সেকেন্ড পর আবার চেষ্টা করা হচ্ছে...")
                time.sleep(10)
                continue
            else:
                print(f"❌ জেমিনি রেসপন্স এরর! সম্পূর্ণ মেসেজ: {result}")
                break
        except Exception as e:
            print(f"❌ জেমিনি থেকে কনটেন্ট তৈরিতে সমস্যা: {e}")
            time.sleep(5)
            
    return None

# ২. ফেসবুকে পোস্ট করার ফাংশন
def post_to_facebook(message):
    if not FB_PAGE_ID or not FB_ACCESS_TOKEN:
        print("❌ এরর: ফেসবুক Page ID বা Access Token সেট করা নেই!")
        return

    url = f"https://graph.facebook.com/v25.0/{FB_PAGE_ID}/feed"
    payload = {
        'message': message,
        'access_token': FB_ACCESS_TOKEN
    }
    
    try:
        response = requests.post(url, data=payload)
        result = response.json()
        
        if 'id' in result:
            print("\n======================================")
            print(f"✅ ফেসবুকে সফলভাবে পোস্ট হয়েছে! পোস্ট আইডি: {result['id']}")
            print("======================================\n")
        else:
            print(f"❌ ফেসবুক পোস্ট এরর! মেসেজ: {result}")
    except Exception as e:
        print(f"❌ ফেসবুকের সাথে কানেক্ট করা যায়নি: {e}")

# ৩. মেইন টাস্ক যা টাইমার রান করবে
def auto_post_job():
    print("🕒 টাইমার ট্রিগার হয়েছে! নতুন পোস্ট তৈরি করা হচ্ছে...")
    ai_text = generate_ai_content()
    if ai_text:
        print(f"📝 জেমিনি যে লেখাটি তৈরি করেছে:\n\n{ai_text}\n")
        post_to_facebook(ai_text)
    else:
        print("❌ টেক্সট জেনারেট করা যায়নি।")

# ==================== TIMER SETUP ====================
# ব্যাকগ্রাউন্ড সিডিউলার সেটআপ
scheduler = BackgroundScheduler(daemon=True)

# এখানে hours=2 দেওয়া আছে, অর্থাৎ প্রতি ২ ঘণ্টা পর পর রান হবে। 
# আপনি চাইলে minutes=30 (৩০ মিনিট) বা hours=1 (১ ঘণ্টা) করে দিতে পারেন।
scheduler.add_job(auto_post_job, 'interval', minutes=3)
scheduler.start()
print("⏰ অটো-পোস্ট টাইমার সফলভাবে চালু হয়েছে (প্রতি ২ ঘণ্টা পর পর পোস্ট হবে)!")
# =====================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
