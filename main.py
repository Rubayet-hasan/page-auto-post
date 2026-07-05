import os
import time
import requests
from datetime import datetime
import pytz
from threading import Thread
from flask import Flask

# ==================== CONFIGURATION ====================
# আপনার ফেসবুক পেজ আইডি এবং মেটা অ্যাপের তথ্য
FB_PAGE_ID = "1096048570267653"
APP_ID = "1711935760121284"              # আপনার মেটা অ্যাপ আইডি এখানে দিন
APP_SECRET = "01911065"      # আপনার মেটা অ্যাপ সিক্রেট এখানে দিন
SHORT_TOKEN = "EAAYUZCxrcPcQBRwco1ab7DqRoN6ZCPriCRzNN6yoFAhsqZAAvaafRRmZBztty8otazQ2TAmG5xCHoLUGC2WMFPLUK9jjxMYJTytFQktc9rx27JZAWXMQ0VauXlk6LIZAcdqu5rxvPg5snNPgYZCGMCmq0e3I7sPDBGasFKVdbZCM6lmnsspj2J9ZAFgPuEcaaEGGwUgZC1S2k7Moiw0g8BhbbDNnPVCLRMjP3Ms3WuvJVZBrOFPRclhIt3c4IDIM6gNForFZAGnkVu7pkKzklZB3l0Tze"  # গ্রাফ এক্সপ্লোরার থেকে পাওয়া টোকেন দিন

GEMINI_API_KEY = os.environ.get("AQ.Ab8RN6KDm0FDEDwnh-vAsuzj8nVpvJGO43B92X7i-aBB9WMiaA")
# =======================================================

app = Flask(__name__)

@app.route('/')
def home():
    return "Ariyan_bot is running successfully and active!"

def get_long_lived_page_token():
    """কোড নিজেই ফেসবুক থেকে আজীবন মেয়াদি পেজ টোকেন বের করে নেবে"""
    print("🔑 ফেসবুক থেকে দীর্ঘমেয়াদি পেজ টোকেন নেওয়ার চেষ্টা করা হচ্ছে...")
    try:
        # ধাপ ১: শর্ট টোকেনকে ৬০ দিনের লং-লাইভ ইউজার টোকেনে রূপান্তর
        user_url = f"https://graph.facebook.com/v20.0/oauth/access_token?grant_type=fb_exchange_token&client_id={APP_ID}&client_secret={APP_SECRET}&fb_exchange_token={SHORT_TOKEN}"
        user_res = requests.get(user_url).json()
        long_user_token = user_res.get('access_token')
        
        if not long_user_token:
            print(f"❌ ইউজার টোকেন রূপান্তর ব্যর্থ: {user_res}")
            return SHORT_TOKEN
            
        # ধাপ ২: লং-লাইভ ইউজার টোকেন দিয়ে আজীবনের পেজ এক্সেস টোকেন নেওয়া
        page_url = f"https://graph.facebook.com/v20.0/me/accounts?access_token={long_user_token}"
        page_res = requests.get(page_url).json()
        
        if 'data' in page_res:
            for page in page_res['data']:
                if str(page['id']) == str(FB_PAGE_ID):
                    print("✅ আজীবন মেয়াদি পেজ এক্সেস টোকেন সফলভাবে সংগ্রহ করা হয়েছে!")
                    return page['access_token']
        print(f"❌ পেজ টোকেন পাওয়া যায়নি, তালিকা: {page_res}")
        return long_user_token
    except Exception as e:
        print(f"❌ টোকেন জেনারেট করতে এরর: {e}")
        return SHORT_TOKEN

def get_bangla_mood_prompt():
    tz = pytz.timezone('Asia/Dhaka')
    current_hour = datetime.now(tz).hour
    if 5 <= current_hour < 12:
        return "সকালবেলা নিয়ে একটি সুন্দর আবেগঘন বা অনুপ্রেরণামূলক ফেসবুক পোস্ট এবং একটি বাস্তবসম্মত ইমেজ প্রম্পট তৈরি করো।"
    elif 12 <= current_hour < 18:
        return "দুপুর বা বিকেলবেলা নিয়ে অলসতা, আড্ডা বা সুন্দর কোনো অনুভূতি প্রকাশ করে একটি ফেসবুক পোস্ট এবং একটি বাস্তবসম্মত ইমেজ প্রম্পট তৈরি করো।"
    else:
        return "রাত বা গভীর রাতের একাকীত্ব, নীরবতা বা সুন্দর কোনো অনুভূতি নিয়ে একটি ফেসবুক পোস্ট এবং একটি বাস্তবসম্মত ইমেজ প্রম্পট তৈরি করো।"

def generate_content_with_gemini():
    print("🤖 জেমিনি এআই দিয়ে কন্টেন্ট জেনারেট করা হচ্ছে...")
    mood_instruction = get_bangla_mood_prompt()
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""
    তুমি একজন দক্ষ সোশ্যাল মিডিয়া ম্যানেজার। {mood_instruction}
    পোস্টটি অবশ্যই সম্পূর্ণ বাংলায় সাবলীল ভাষায় হতে হবে (কোনো ইংরেজি বা রোমান বাংলা নয়)।
    পোস্টে সুন্দর কিছু ইমোজি ও মানানসই হ্যাশট্যাগ ব্যবহার করবে।
    একদম শেষে ছবির জন্য ইংরেজিতে একটি হাই-রেজোলিউশন ও রিয়ালিস্টিক ইমেজ জেনারেশন প্রম্পট লিখে দেবে।
    
    আউটপুট ফরম্যাট হুবহু নিচের মতো হতে হবে:
    CAPTION: [এখানে পুরো বাংলা পোস্টটি লিখবে]
    IMAGE_PROMPT: [এখানে ছবির জন্য ইংরেজি প্রম্পটটি লিখবে]
    """
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        if 'candidates' not in result:
            print(f"❌ জেমিনি রেসপন্স এরর: {result}")
            return None, None
            
        text_output = result['candidates'][0]['content']['parts'][0]['text']
        caption = text_output.split("CAPTION:")[1].split("IMAGE_PROMPT:")[0].strip()
        image_prompt = text_output.split("IMAGE_PROMPT:")[1].strip()
        return caption, image_prompt
    except Exception as e:
        print(f"❌ জেমিনি প্রসেসিং এরর: {e}")
        return "আজকের দিনটি চমৎকার কাটুক! 🌟 #bangla #post", "A beautiful cinematic dramatic scenery"

def generate_image_with_pollinations(image_prompt):
    print("🎨 ছবি জেনারেট করা হচ্ছে...")
    base_url = "https://image.pollinations.ai/p/"
    encoded_prompt = requests.utils.quote(image_prompt)
    return f"{base_url}{encoded_prompt}?width=1080&height=1080&nologo=true"

def post_to_facebook(caption, image_url, token):
    print("📤 ফেসবুকে পোস্ট আপলোড করা হচ্ছে...")
    url = f"https://graph.facebook.com/v20.0/{FB_PAGE_ID}/photos"
    payload = {
        'caption': caption,
        'url': image_url,
        'access_token': token
    }
    response = requests.post(url, data=payload)
    res_data = response.json()
    if "id" in res_data:
        print(f"✅ সফলভাবে ফেসবুক পেজে পোস্ট করা হয়েছে! পোস্ট আইডি: {res_data['id']}")
    else:
        print(f"❌ ফেসবুক এরর: {res_data}")

def run_bot_task():
    try:
        # রান হওয়ার সময় প্রতিবার কোড নিজেই তাজা টোকেন জেনারেট করবে
        dynamic_token = get_long_lived_page_token()
        caption, img_prompt = generate_content_with_gemini()
        if caption and img_prompt:
            img_url = generate_image_with_pollinations(img_prompt)
            post_to_facebook(caption, img_url, dynamic_token)
    except Exception as e:
        print(f"❌ পোস্টিং টাস্কে এরর: {e}")

def bot_loop():
    while True:
        print("🕒 ৩ ঘণ্টার বিরতি শুরু হলো...")
        time.sleep(10800)
        print("⏳ বিরতি শেষ, নতুন পোস্টের কাজ শুরু হচ্ছে...")
        run_bot_task()

print("🔄 সার্ভার স্টার্ট হচ্ছে, প্রথম পোস্টটি রান করা হচ্ছে...")
run_bot_task()

t = Thread(target=bot_loop)
t.daemon = True
t.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
