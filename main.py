import os
import requests
import time
import threading
from flask import Flask

# ==================== CONFIGURATION ====================
GEMINI_API_KEY = os.environ.get("api_key")
FB_PAGE_ID = os.environ.get("fb_page_id")
FB_ACCESS_TOKEN = os.environ.get("fb_access_token")
HISTORY_FILE = "posted_history.txt"
INTERVAL_HOURS = 10  # প্রতি ১০ ঘণ্টা পর পর পোস্ট হবে
# =======================================================

app = Flask(__name__)

@app.route('/')
def home():
    return f"Facebook AI Post Bot is Running! Posting every {INTERVAL_HOURS} hours."

def get_posted_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def save_to_history(text):
    first_line = text.split("\n")[0][:50].strip()
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(first_line + "\n")

def generate_ai_content():
    if not GEMINI_API_KEY:
        print("❌ এরর: রেন্ডারের Environment-এ 'api_key' খুঁজে পাওয়া যায়নি!", flush=True)
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = (
        "তুমি একটি ফেসবুক পেজের জন্য কনটেন্ট লিখবে। পেজটি মূলত বাংলা নাটক (Bangla Natok), নাটকের রিভিউ, "
        "মজার ডায়ালগ এবং আবেগঘন নাটকের সিন নিয়ে। বাংলা নাটকের দর্শক পছন্দ করবে এমন একটি সুন্দর, ইউনিক এবং আকর্ষণীয় "
        "ক্যাপশন বা স্ট্যাটাস লেখো (২-৩ লাইনের মধ্যে)। সাথে অবশ্যই রিলেভেন্ট হ্যাশট্যাগ (যেমন: #BanglaNatok #Natok) দেবে। "
        "কোনো ভূমিকা বা বাড়তি কথা ছাড়া শুধু মূল ফেসবুক পোস্টটুকু দেবে।"
    )
    
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    history = get_posted_history()
    max_retries = 5
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            
            if 'candidates' in result:
                ai_text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                match_line = ai_text.split("\n")[0][:50].strip()
                if match_line in history:
                    print(f"⚠️ জেমিনি পুরাতন পোস্ট তৈরি করেছে! আবার চেষ্টা করা হচ্ছে (Attempt {attempt + 1})...", flush=True)
                    time.sleep(2)
                    continue
                return ai_text
            
            if 'error' in result and result['error'].get('code') == 503:
                print(f"⚠️ গুগল সার্ভার ব্যস্ত। ১০ সেকেন্ড পর আবার চেষ্টা করা হচ্ছে...", flush=True)
                time.sleep(10)
                continue
            else:
                print(f"❌ এপিআই অ্যাক্সেস এরর! ডিটেইলস: {result}", flush=True)
                break
        except Exception as e:
            print(f"❌ জেমিনি এপিআই কানেকশনে সমস্যা: {e}", flush=True)
            time.sleep(5)
            
    return None

def post_to_facebook(message):
    if not FB_PAGE_ID or not FB_ACCESS_TOKEN:
        print("❌ এরর: ফেসবুক সেটিংস বা টোকেন মিসিং!", flush=True)
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
            print("\n======================================", flush=True)
            print(f"✅ ফেসবুকে সফলভাবে পোস্ট হয়েছে! পোস্ট আইডি: {result['id']}", flush=True)
            print("======================================\n", flush=True)
            save_to_history(message)
        else:
            print(f"❌ ফেসবুক পোস্ট এরর! মেসেজ: {result}", flush=True)
    except Exception as e:
        print(f"❌ ফেসবুক কানেকশন এরর: {e}", flush=True)

def auto_post_loop():
    # রেন্ডার সার্ভার পুরোপুরি রেডি হওয়ার জন্য ৫ সেকেন্ড ওয়েট করবে
    time.sleep(5)
    print("🚀 ১০ ঘণ্টার অটো-পোস্ট লুপ ব্যাকগ্রাউন্ডে চালু হলো...", flush=True)
    print("📢 বোট চালু হয়েছে, প্রথম পোস্ট ট্রাই করা হচ্ছে...", flush=True)
    
    ai_text = generate_ai_content()
    if ai_text:
        post_to_facebook(ai_text)
    
    while True:
        print(f"⏳ পরবর্তী পোস্টের জন্য {INTERVAL_HOURS} ঘণ্টা অপেক্ষা করা হচ্ছে...", flush=True)
        time.sleep(INTERVAL_HOURS * 3600)
        print("⏰ ১০ ঘণ্টা পূর্ণ হয়েছে! নতুন পোস্ট তৈরি করা হচ্ছে...", flush=True)
        ai_text = generate_ai_content()
        if ai_text:
            print(f"📝 ஜেমিনির নতুন স্ট্যাটাস:\n\n{ai_text}\n", flush=True)
            post_to_facebook(ai_text)

# gunicorn এর জন্য থ্রেডটি এখানে হ্যান্ডেল করা হয়েছে
threading.Thread(target=auto_post_loop, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
