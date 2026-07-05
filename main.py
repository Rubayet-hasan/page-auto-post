import os
import requests
import time
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

# ১. জেমিনি থেকে কনটেন্ট জেনারেট করার ফাংশন (with Auto-Retry)
def generate_ai_content():
    if not GEMINI_API_KEY:
        print("❌ এরর: রেন্ডারের Environment-এ 'api_key' খুঁজে পাওয়া যায়নি!")
        return None

    # জেমিনি ২.৫ ফ্ল্যাশ মডেলের অফিশিয়াল এন্ডপয়েন্ট
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    # বোটকে দেওয়া প্রম্পট
    prompt = "ফেসবুক পেজের জন্য একটি সুন্দর শিক্ষণীয় বা মোтивнойেশনাল স্ট্যাটাস লেখো (২-৩ লাইনের মধ্যে, সাথে রিলেভেন্ট হ্যাশট্যাগ)। কোনো বাড়তি কথা বা ইন্ট্রো ছাড়া শুধু মেইন পোস্টটুকু দেবে।"
    
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    # গুগলের সার্ভার ব্যস্ত (503 Error) থাকলে বোট সর্বোচ্চ ৫ বার অটোমেটিক ট্রাই করবে
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            
            if 'candidates' in result:
                return result['candidates'][0]['content']['parts'][0]['text']
            
            # যদি ৫0৩ এরর বা সার্ভার ডাউন থাকে
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
        print("দয়া করে রেন্ডারের Environment ট্যাবে fb_page_id এবং fb_access_token সেট করুন।")
        return

    # ফেসবুক গ্রাফ এপিআই লেটেস্ট ইউআরএল (v25.0)
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
            print(f"✅ ফেসবুকে সফলভাবে পোস্ট হয়েছে! পোস্ট আইডি: {result['id']}")
            print("======================================\n")
        else:
            print(f"❌ ফেসবুক পোস্ট এরর! মেসেজ: {result}")
    except Exception as e:
        print(f"❌ ফেসবুকের সাথে কানেক্ট করা যায়নি: {e}")

# বোট চালু হলেই রান শুরু হবে
print("🚀 ফেসবুক অটো-পোস্ট বোট স্টার্ট হচ্ছে...")
ai_text = generate_ai_content()
if ai_text:
    print(f"📝 জেমিনি যে লেখাটি তৈরি করেছে:\n\n{ai_text}\n")
    post_to_facebook(ai_text)
else:
    print("❌ টেক্সট জেনারেট করা যায়নি বা খালি থাকায় ফেসবুকে পোস্ট করা যায়নি।")

if __name__ == "__main__":
    # রেন্ডারের ডিফল্ট পোর্ট রিড করা হচ্ছে
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
