import os
import requests
import time
from flask import Flask

GEMINI_API_KEY = os.environ.get("api_key")
FB_PAGE_ID = os.environ.get("fb_page_id")
FB_ACCESS_TOKEN = os.environ.get("fb_access_token")

app = Flask(__name__)

@app.route('/')
def home():
    return "Facebook Auto-Post Bot is Running Successfully!"

def generate_ai_content():
    if not GEMINI_API_KEY:
        print("❌ এরর: রেন্ডারের Environment-এ 'api_key' খুঁজে পাওয়া যায়নি!")
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = "ফেসবুক পেজের জন্য একটি সুন্দর শিক্ষণীয় বা মোティブেশনাল স্ট্যাটাস লেখো (২-৩ লাইনের মধ্যে, সাথে রিলেভেন্ট হ্যাশট্যাগ)। কোনো বাড়তি কথা বা ইন্ট্রো ছাড়া শুধু মেইন পোস্টটুকু দেবে।"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    for attempt in range(3):
        try:
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            if 'candidates' in result:
                return result['candidates'][0]['content']['parts'][0]['text']
            if 'error' in result and result['error'].get('code') == 503:
                print(f"⚠️ গুগলের সার্ভার ব্যস্ত। ১০ সেকেন্ড পর আবার চেষ্টা করা হচ্ছে...")
                time.sleep(10)
                continue
        except Exception as e:
            print(f"❌ জেমিনি এরর: {e}")
            time.sleep(5)
    return None

def post_to_facebook(message):
    if not FB_PAGE_ID or not FB_ACCESS_TOKEN:
        print("❌ এরর: ফেসবুক Page ID বা Access Token সেট করা নেই!")
        return

    # গ্রাফ এপিআই লেটেস্ট ভার্সন v25.0 ব্যবহার করা হচ্ছে
    url = f"https://graph.facebook.com/v25.0/{FB_PAGE_ID}/feed"
    payload = {
        'message': message,
        'access_token': FB_ACCESS_TOKEN
    }
    
    try:
        response = requests.post(url, data=payload)
        result = response.json()
        if 'id' in result:
            print(f"\n✅ ফেসবুকে সফলভাবে পোস্ট হয়েছে! পোস্ট আইডি: {result['id']}\n")
        else:
            print(f"❌ ফেসবুক পোস্ট এরর! মেসেজ: {result}")
    except Exception as e:
        print(f"❌ ফেসবুক কানেকশন এরর: {e}")

print("🚀 ফেসবুক বোট স্টার্ট হচ্ছে...")
ai_text = generate_ai_content()
if ai_text:
    print(f"📝 জেমিনির লেখা:\n{ai_text}\n")
    post_to_facebook(ai_text)
else:
    print("❌ টেক্সট খালি থাকায় ফেসবুকে পোস্ট করা যায়নি।")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
