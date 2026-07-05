import os
import time
import requests
from datetime import datetime
import pytz
from threading import Thread
from flask import Flask

# ==================== CONFIGURATION ====================
FB_PAGE_ID = os.environ.get("FB_PAGE_ID", "1096048570267653")
FB_PAGE_TOKEN = os.environ.get("FB_PAGE_TOKEN", "EAAYUZCxrcPcQBR6HUyQXY3EdSEJ5xz6w5yNGPN3lOkPAZB11WQPCWXZCspCJoS5R7o7fxSLYbJlu9ZCuImMpw0UjbwV0d6T2Nu3L6PK0MUTTlmJbVrMTzpNM26wcZAM3tzaPOw4DfdyfWRR0kaZCYu7SWALmb6OeaLW74rArPFJXCf8VZB5Csxs3ILFUrPcT0CZBwoTzfpY8")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6KDm0FDEDwnh-vAsuzj8nVpvJGO43B92X7i-aBB9WMiaA")
# =======================================================

app = Flask(__name__)

@app.route('/')
def home():
    return "Ariyan_bot is running successfully and active!"

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
    
    prompt = f"""
    তুমি একজন দক্ষ সোশ্যাল মিডিয়া ম্যানেজার। {mood_instruction}
    পোস্টটি অবশ্যই সম্পূর্ণ বাংলায় সাবলীল ভাষায় হতে হবে (কোনো ইংরেজি বা রোমান বাংলা নয়)।
    পোস্টে সুন্দর কিছু ইমোজি ও মানানসই হ্যাশট্যাগ ব্যবহার করবে।
    একদম শেষে ছবির জন্য ইংরেজিতে একটি হাই-রেজোলিউশন ও রিয়ালিস্টিক ইমেজ জেনারেশন প্রম্পট লিখে দেবে।
    
    আউটপুট ফরম্যাট হুবহু নিচের মতো হতে হবে:
    CAPTION: [এখানে পুরো বাংলা পোস্টটি লিখবে]
    IMAGE_PROMPT: [এখানে ছবির জন্য ইংরেজি প্রম্পটটি লিখবে]
    """
    
    # এরর এড়াতে নতুন এবং অল্টারনেটিভ জেমিনি গেটওয়ে ইউআরএল ব্যবহার করা হয়েছে
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        if 'candidates' in result:
            text_output = result['candidates'][0]['content']['parts'][0]['text']
            caption = text_output.split("CAPTION:")[1].split("IMAGE_PROMPT:")[0].strip()
            image_prompt = text_output.split("IMAGE_PROMPT:")[1].strip()
            return caption, image_prompt
        else:
            # ব্যাকআপ সিস্টেম যদি এপিআই ইউআরএল কাজ না করে
            print("⚠️ সরাসরি এপিআই ব্যর্থ, ব্যাকআপ সার্ভার ব্যবহার করা হচ্ছে...")
            backup_url = f"https://open-api.lycoris.workers.dev/v1/chat/completions"
            backup_headers = {"Authorization": f"Bearer {GEMINI_API_KEY}", "Content-Type": "application/json"}
            backup_data = {
                "model": "gemini-1.5-flash",
                "messages": [{"role": "user", "content": prompt}]
            }
            res = requests.post(backup_url, headers=backup_headers, json=backup_data)
            text_output = res.json()['choices'][0]['message']['content']
            caption = text_output.split("CAPTION:")[1].split("IMAGE_PROMPT:")[0].strip()
            image_prompt = text_output.split("IMAGE_PROMPT:")[1].strip()
            return caption, image_prompt
    except Exception as e:
        print(f"❌ জেমিনি প্রসেসিং এরর: {e}")
        return "শুভ দিন! আপনাদের সবার সময় সুন্দর কাটুক। ✨ #goodvibes", "A beautiful cinematic dramatic scenery, highly detailed, 8k resolution"

def generate_image_with_pollinations(image_prompt):
    print("🎨 ছবি জেনারেট করা হচ্ছে...")
    base_url = "https://image.pollinations.ai/p/"
    encoded_prompt = requests.utils.quote(image_prompt)
    return f"{base_url}{encoded_prompt}?width=1080&height=1080&nologo=true"

def post_to_facebook(caption, image_url):
    print("📤 ফেসবুকে পোস্ট আপলোড করা হচ্ছে...")
    url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/photos"
    payload = {
        'caption': caption,
        'url': image_url,
        'access_token': FB_PAGE_TOKEN
    }
    response = requests.post(url, data=payload)
    res_data = response.json()
    if "id" in res_data:
        print(f"✅ সফলভাবে ফেসবুক পেজে পোস্ট করা হয়েছে! পোস্ট আইডি: {res_data['id']}")
    else:
        print(f"❌ ফেসবুক এরর: {res_data}")

def run_bot_task():
    try:
        caption, img_prompt = generate_content_with_gemini()
        if caption and img_prompt:
            img_url = generate_image_with_pollinations(img_prompt)
            post_to_facebook(caption, img_url)
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
