import os
import time
import requests
from datetime import datetime
import pytz
from threading import Thread
from flask import Flask

# ==================== CONFIGURATION ====================
FB_PAGE_ID = os.environ.get("FB_PAGE_ID", "1096048570267653")
FB_PAGE_TOKEN = os.environ.get("FB_PAGE_TOKEN", "EAAYUZCxrcPcQBRwco1ab7DqRoN6ZCPriCRzNN6yoFAhsqZAAvaafRRmZBztty8otazQ2TAmG5xCHoLUGC2WMFPLUK9jjxMYJTytFQktc9rx27JZAWXMQ0VauXlk6LIZAcdqu5rxvPg5snNPgYZCGMCmq0e3I7sPDBGasFKVdbZCM6lmnsspj2J9ZAFgPuEcaaEGGwUgZC1S2k7Moiw0g8BhbbDNnPVCLRMjP3Ms3WuvJVZBrOFPRclhIt3c4IDIM6gNForFZAGnkVu7pkKzklZB3l0Tze")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "Ab8RN6Juov6ymRDzVnsjna0bopBN5cgz81O1Jf-fdHHP1kZnmA")
# =======================================================

app = Flask(__name__)

@app.route('/')
def home():
    return "Ariyan_bot is running successfully and active!"

def get_bangla_mood_prompt():
    """বাংলাদেশ সময় অনুযায়ী মুড ঠিক করার ফাংশন"""
    tz = pytz.timezone('Asia/Dhaka')
    current_hour = datetime.now(tz).hour
    
    if 5 <= current_hour < 12:
        return "সকালবেলা নিয়ে একটি সুন্দর আবেগঘন বা অনুপ্রেরণামূলক ফেসবুক পোস্ট এবং একটি বাস্তবসম্মত ইমেজ প্রম্পট তৈরি করো।"
    elif 12 <= current_hour < 18:
        return "দুপুর বা বিকেলবেলা নিয়ে অলসতা, আড্ডা বা সুন্দর কোনো অনুভূতি প্রকাশ করে একটি ফেসবুক পোস্ট এবং একটি বাস্তবসম্মত ইমেজ প্রম্পট তৈরি করো।"
    else:
        return "রাত বা গভীর রাতের একাকীত্ব, নীরবতা বা সুন্দর কোনো অনুভূতি নিয়ে একটি ফেসবুক পোস্ট এবং একটি বাস্তবসম্মত ইমেজ প্রম্পট তৈরি করো।"

def generate_content_with_gemini():
    """গুগল জেমিনি এআই দিয়ে বাংলা ক্যাপশন ও ইমেজ প্রম্পট তৈরি করার ফাংশন"""
    print("🤖 জেমিনি এআই দিয়ে কন্টেন্ট জেনারেট করা হচ্ছে...")
    mood_instruction = get_bangla_mood_prompt()
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    
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
    
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    
    text_output = result['candidates'][0]['content']['parts'][0]['text']
    
    # ক্যাপশন ও প্রম্পট আলাদা করা
    caption = text_output.split("CAPTION:")[1].split("IMAGE_PROMPT:")[0].strip()
    image_prompt = text_output.split("IMAGE_PROMPT:")[1].strip()
    
    return caption, image_prompt

def generate_image_with_pollinations(image_prompt):
    """Pollinations AI দিয়ে ফ্রিতে ছবি জেনারেট করে তার লিংক বের করার ফাংশন"""
    print("🎨 ছবি জেনারেট করা হচ্ছে...")
    base_url = "https://image.pollinations.ai/p/"
    encoded_prompt = requests.utils.quote(image_prompt)
    image_url = f"{base_url}{encoded_prompt}?width=1080&height=1080&nologo=true"
    return image_url

def post_to_facebook(caption, image_url):
    """ফেসবুক পেজে ছবি ও ক্যাপশন একসাথে পোস্ট করার ফাংশন"""
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

def bot_loop():
    """৩ ঘণ্টা পর পর রান হওয়ার মূল লুপ"""
    print("🚀 Ariyan_bot এর ব্যাকগ্রাউন্ড প্রসেস শুরু হলো...")
    
    # প্রথমবার রান করার সাথে সাথেই একটি পোস্ট করার চেষ্টা করবে
    try:
        caption, img_prompt = generate_content_with_gemini()
        img_url = generate_image_with_pollinations(img_prompt)
        post_to_facebook(caption, img_url)
    except Exception as e:
        print(f"❌ প্রথম পোস্টে এরর: {e}")

    while True:
        # ৩ ঘণ্টা অপেক্ষা (৩ ঘণ্টা = ১০৮০০ সেকেন্ড)
        print("🕒 ৩ ঘণ্টার বিরতি শুরু হলো...")
        time.sleep(10800)
        
        try:
            caption, img_prompt = generate_content_with_gemini()
            img_url = generate_image_with_pollinations(img_prompt)
            post_to_facebook(caption, img_url)
        except Exception as e:
            print(f"❌ লুপের ভেতর এরর ঘটেছে: {e}")

if __name__ == "__main__":
    # সার্ভার কিল হওয়া আটকাতে ব্যাকগ্রাউন্ড থ্রেড চালু
    t = Thread(target=bot_loop)
    t.daemon = True
    t.start()
    
    # রেন্ডার সার্ভার বাইন্ডিং
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
