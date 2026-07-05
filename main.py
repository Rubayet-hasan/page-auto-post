import os
import requests
import time
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

# ==================== CONFIGURATION ====================
# রেন্ডারের Environment Variables থেকে সিক্রেট কি-গুলো নেওয়া হচ্ছে
GEMINI_API_KEY = os.environ.get("api_key")
FB_PAGE_ID = os.environ.get("fb_page_id")
FB_ACCESS_TOKEN = os.environ.get("fb_access_token")
# =======================================================

app = Flask(__name__)

@app.route('/')
def home():
    return "Facebook Auto-Post Bot is Running with Timer & Instant Start!"

# ১. জেমিনি থেকে কনটেন্ট জেনারেট করার ফাংশন (with Auto-Retry)
def generate_ai_content():
    if not GEMINI_API_KEY:
        print("❌ এরর: রেন্ডারের Environment-এ 'api_key' খুঁজে পাওয়া যায়নি!")
        return None

    # জেমিনি ২.৫ ফ্ল্যাশ মডেলের অফিশিয়াল এন্ডপয়েন্ট
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    # বোটকে দেওয়া প্রম্পট
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
            
            # গুগলের সার্ভার ব্যস্ত (503 Error) থাকলে বোট সর্বোচ্চ ৫ বার অটোমেটিক ট্রাই করবে
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

# ২. ফেসবুকে টেক্সট পোস্ট করার ফাংশন (ফিক্সড এন্ডপয়েন্ট)
def post_to_facebook(message):
    if not FB_PAGE_ID or not FB_ACCESS_TOKEN:
        print("❌ এরর: ফেসবুক Page ID বা Access Token সেট করা নেই!")
        print("দয়া করে রেন্ডারের Environment ট্যাবে fb_page_id এবং fb_access_token সেট করুন।")
        return

    # ফিক্সড: ছবি ছাড়া টেক্সট পোস্ট করার জন্য /feed এন্ডপয়েন্ট ব্যবহার করা হয়েছে
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
    print("🕒 পোস্ট প্রসেস শুরু হচ্ছে...")
    ai_text = generate_ai_content()
    if ai_text:
        print(f"📝 জেমিনি যে লেখাটি তৈরি করেছে:\n\n{ai_text}\n")
        post_to_facebook(ai_text)
    else:
        print("❌ টেক্সট জেনارهট করা যায়নি বা খালি থাকায় ফেসবুকে পোস্ট করা যায়নি।")

# ==================== TIMER SETUP ====================
# ব্যাকগ্রাউন্ড সিডিউলার সেটআপ
scheduler = BackgroundScheduler(daemon=True)

# আপনার স্ক্রিনশট অনুযায়ী এখানে hours=10 (১০ ঘণ্টা) লুপ সেট করা হয়েছে। 
# আপনি চাইলে এটি পরিবর্তন করতে পারেন (যেমন: hours=2)
scheduler.add_job(auto_post_job, 'interval', hours=10)
scheduler.start()
print("⏰ ১০ ঘণ্টার অটো-পোস্ট লুপ ব্যাকগ্রাউন্ডে চালু হলো...")

# 🚀 বোট চালু হওয়ার সাথে সাথেই প্রথম পোস্টটি করার জন্য ফাংশনটি কল করা হলো
print("📢 বোট চালু হয়েছে, প্রথম পোস্ট ট্রাই করা হচ্ছে...")
auto_post_job()
print("⏳ পরবর্তী পোস্টের জন্য 10 ঘণ্টা অপেক্ষা করা হচ্ছে...")
# =====================================================

if __name__ == "__main__":
    # রেন্ডারের ডিফল্ট পোর্ট রিড করা হচ্ছে
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
