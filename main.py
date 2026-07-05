import os
import requests
import time
import threading
import json
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
    return f"Facebook AI Photo & Caption Post Bot is Running! Posting every {INTERVAL_HOURS} hours."

def get_posted_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def save_to_history(text):
    first_line = text.split("\n")[0][:50].strip()
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(first_line + "\n")

# জেমিনি থেকে ক্যাপশন এবং ছবির লিংক একসাথে JSON আকারে বের করার ফাংশন
def generate_ai_photo_content():
    if not GEMINI_API_KEY:
        print("❌ এরর: 'api_key' খুঁজে পাওয়া যায়নি!", flush=True)
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    # জেমিনিকে JSON ফরম্যাটে ডেটা দিতে বাধ্য করার প্রম্পট
    prompt = (
        "তুমি একটি ফেসবুক পেজের জন্য শুধু ১টি একক (single) পোস্ট তৈরি করবে। "
        "পেজটি মূলত বাংলা নাটক (Bangla Natok), নাটকের রিভিউ বা মজার ডায়ালগ নিয়ে। "
        "তুমি আমাকে একটি রেডিমেড আকর্ষণীয় ক্যাপশন (২-৩ লাইনের মধ্যে, সাথে হ্যাশট্যাগ) দেবে "
        "এবং ইন্টারনেট থেকে অ্যাক্সেস করা যায় এমন একটি সুন্দর পাবলিক বাংলা নাটকের ছবির ডিরেক্ট লিংক (Image URL) খুঁজে দেবে। "
        "ছবিটি যেন অবশ্যই কোনো নাটকের দৃশ্য বা পোস্টার সম্পর্কিত সরাসরি ইমেজ লিংক (.jpg বা .png) হয়। "
        "কোনো বাড়তি কথা বা ভূমিকা ছাড়া সম্পূর্ণ উত্তরটি একটি নিখুঁত JSON ফরম্যাটে দেবে, যেন আমি সহজেই কোড দিয়ে রিড করতে পারি। "
        "JSON ফরম্যাটটি হুবহু নিচের মতো হবে:\n"
        "{\n"
        '  "caption": "এখানে সুন্দর নাটকের ক্যাপশন এবং হ্যাশট্যাগ থাকবে",\n'
        '  "image_url": "এখানে সরাসরি ছবির ডিরেক্ট লিংক থাকবে"\n'
        "}"
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
                raw_text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # জেমিনির টেক্সট থেকে অনেক সময় মার্কডাউন ```json কেটে পিওর টেক্সট নেওয়া
                if raw_text.startswith("```json"):
                    raw_text = raw_text.replace("```json", "").replace("```", "").strip()
                elif raw_text.startswith("```"):
                    raw_text = raw_text.replace("```", "").strip()
                
                # JSON পার্স করা
                parsed_data = json.loads(raw_text)
                caption = parsed_data.get("caption", "").strip()
                image_url = parsed_data.get("image_url", "").strip()
                
                if not caption or not image_url:
                    continue
                
                # ডুপ্লিকেট পোস্ট চেক
                match_line = caption.split("\n")[0][:50].strip()
                if match_line in history:
                    print("⚠️ জেমিনি পুরাতন পোস্ট তৈরি করেছে! আবার চেষ্টা করা হচ্ছে...", flush=True)
                    time.sleep(2)
                    continue
                    
                return caption, image_url
            
            if 'error' in result and result['error'].get('code') == 503:
                print("⚠️ গুগল সার্ভার ব্যস্ত। ১০ সেকেন্ড পর আবার চেষ্টা করা হচ্ছে...", flush=True)
                time.sleep(10)
                continue
        except Exception as e:
            print(f"❌ জেমিনি এপিআই বা JSON পার্সিং সমস্যা: {e}", flush=True)
            time.sleep(5)
            
    return None

# ফেসবুকে ছবি এবং ক্যাপশন একসাথে আপロード করার ফাংশন
def post_photo_to_facebook(caption, image_url):
    if not FB_PAGE_ID or not FB_ACCESS_TOKEN:
        print("❌ এরর: ফেসবুক সেটিংস বা টোকেন মিসিং!", flush=True)
        return

    # ফেসবুকে ছবি পোস্ট করার অফিশিয়াল এন্ডপয়েন্ট (/photos)
    url = f"https://graph.facebook.com/v25.0/{FB_PAGE_ID}/photos"
    payload = {
        'url': image_url,
        'caption': caption,
        'access_token': FB_ACCESS_TOKEN
    }
    
    try:
        response = requests.post(url, data=payload)
        result = response.json()
        
        # সফলভাবে ছবি পোস্ট হলে ফেসবুক একটি post_id বা id রিটার্ন করে
        if 'id' in result:
            print("\n======================================", flush=True)
            print(f"✅ ফেসবুকে সফলভাবে ছবিসহ পোস্ট হয়েছে! পোস্ট আইডি: {result['id']}", flush=True)
            print(f"🖼️ আপলোড হওয়া ছবির লিংক: {image_url}", flush=True)
            print("======================================\n", flush=True)
            save_to_history(caption)
        else:
            print(f"❌ ফেসবুক ফটো পোস্ট এরর! মেসেজ: {result}", flush=True)
            print("💡 টিপস: আপনার টোকেনে 'pages_manage_posts' পারমিশন অ্যাড করা থাকতে হবে।", flush=True)
    except Exception as e:
        print(f"❌ ফেসবুক কানেকশন এরর: {e}", flush=True)

def auto_post_loop():
    time.sleep(5)
    print("🚀 ১০ ঘণ্টার অটো-ফটো পোস্ট লুপ ব্যাকগ্রাউন্ডে চালু হলো...", flush=True)
    print("📢 বোট চালু হয়েছে, প্রথম ছবিসহ পোস্ট ট্রাই করা হচ্ছে...", flush=True)
    
    ai_data = generate_ai_photo_content()
    if ai_data:
        caption, image_url = ai_data
        post_photo_to_facebook(caption, image_url)
    
    while True:
        print(f"⏳ পরবর্তী পোস্টের জন্য {INTERVAL_HOURS} ঘণ্টা অপেক্ষা করা হচ্ছে...", flush=True)
        time.sleep(INTERVAL_HOURS * 3600)
        print("⏰ ১০ ঘণ্টা পূর্ণ হয়েছে! নতুন ছবি ও ক্যাপশন তৈরি করা হচ্ছে...", flush=True)
        ai_data = generate_ai_photo_content()
        if ai_data:
            caption, image_url = ai_data
            print(f"📝 নতুন ক্যাপশন:\n{caption}\n", flush=True)
            post_photo_to_facebook(caption, image_url)

threading.Thread(target=auto_post_loop, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
