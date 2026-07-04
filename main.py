import os
import time
import requests
from datetime import datetime
import pytz
from threading import Thread
from flask import Flask

# ==================== FLASK SERVER FOR RENDER ====================
app = Flask('')

@app.route('/')
def home():
    return "Ariyan_bot is Running 24/7 Live on Render!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_server)
    t.start()
# =================================================================

FB_PAGE_ID = "1096048570267653"
FB_PAGE_TOKEN = "EAAYUZCxrcPcQBR2uXwrOZAodwqERnWZB74hZCRTKB5o5GJE1fZCYeefWJITtOh0i9gBtHCiucOMmb81ghaf7KZBycOWs8P3nUWEGQqwFZClFpTgqrrnojA1ihf72A9RNsOib6yZCEKr3kJifWxquYFSH9Wqv0r1FDVZBFmbDhwZC3b6ZAg6lwQbrkkyONlyzCHiN1M8y67DiL92CdEYUpEwC1t4oZBRKZC6JW9BX68yr88bblVskZD"
GEMINI_API_KEY = "AQ.Ab8RN6Juov6ymRDzVnsjna0bopBN5cgz81O1Jf-fdHHP1kZnmA"

def get_current_mood_instruction():
    bd_timezone = pytz.timezone("Asia/Dhaka")
    current_hour = datetime.now(bd_timezone).hour
    
    if 6 <= current_hour < 12:
        return (
            "Write a beautiful, inspiring, and positive Bengali drama/natok title and a short 2-line motivational Facebook status caption for the page 'Mojar Karigor'. "
            "At the end, write a 1-sentence English image prompt representing hope, beautiful morning scenery, or positive human emotions (e.g., 'A bright cinematic outdoor portrait of a happy person looking at the sunrise, soft morning light, bokeh effect, 8k resolution')."
        )
    elif 12 <= current_hour < 20:
        return (
            "Write a hilarious, funny, and comedic Bengali drama/natok title and a short 2-line witty/comedy Facebook status caption that perfectly matches the page name 'Mojar Karigor'. Make people laugh. "
            "At the end, write a 1-sentence English image prompt representing a funny situation, comedic acting, or expressive funny faces (e.g., 'A humorous cinematic close-up of a funny expressive character, bright comedy lighting, highly detailed, 8k resolution')."
        )
    else:
        return (
            "Write a deep, emotional, and romantic Bengali drama/natok title and a short 2-line emotional/romantic Facebook status caption for the page 'Mojar Karigor'. "
            "At the end, write a 1-sentence English image prompt representing a cinematic romantic scene or a dramatic portrait (e.g., 'A cinematic high-resolution dramatic portrait of a romantic couple in the rain, moody lighting, beautiful bokeh effect, 8k resolution, sony a7riv style')."
        )

def generate_ai_text_and_prompt():
    instruction = get_current_mood_instruction()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    prompt_instruction = f"{instruction}\n\nFormat your response exactly like this, separating with '---' and do NOT use **:\nTitle\n---\nPrompt"
    payload = {"contents": [{"parts": [{"text": prompt_instruction}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        ai_output = response.json()['candidates'][0]['content']['parts'][0]['text']
        parts = ai_output.split("---")
        fb_caption = parts[0].strip().replace("**", "")
        image_prompt = parts[1].strip() if len(parts) > 1 else "Cinematic drama scene, 8k, bokeh"
        return fb_caption, image_prompt
    except:
        return "🎬 নতুন ধামাকা পোস্ট! মোজার কারিগর পেজের সাথেই থাকুন। ❤️", "Cinematic portrait, bokeh, 8k"

def post_ai_content_to_facebook():
    fb_caption, image_prompt = generate_ai_text_and_prompt()
    encoded_prompt = requests.utils.quote(image_prompt)
    ai_image_url = f"https://image.pollinations.ai/p/{encoded_prompt}?width=1200&height=800&enhance=true"
    
    fb_url = f"https://graph.facebook.com/v25.0/{FB_PAGE_ID}/photos"
    payload = {'url': ai_image_url, 'caption': fb_caption, 'access_token': FB_PAGE_TOKEN}
    
    try:
        res = requests.post(fb_url, data=payload, timeout=30).json()
        if "id" in res:
            print(f"✅ [Ariyan_bot] সফলভাবে পোস্ট করেছে! আইডি: {res['id']}")
        else:
            print(f"❌ ফেসবুক এরর: {res.get('error', {}).get('message')}")
    except Exception as e:
        print(f"❌ সমস্যা: {e}")

def main():
    print("🚀 Ariyan_bot সার্ভার চালু হচ্ছে...")
    keep_alive()
    
    while True:
        post_ai_content_to_facebook()
        print("🕒 ৩ ঘণ্টা বিরতি... বট ব্যাকগ্রাউন্ডে সচল আছে।")
        time.sleep(10800)

if __name__ == "__main__":
    main()