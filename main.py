import edge_tts
import asyncio
import os
import requests
import random
from groq import Groq
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import arabic_reshaper
from bidi.algorithm import get_display

# الإعدادات
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")

def generate_fact():
    """توليد حقيقة علمية قصيرة ومبهرة"""
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user", 
            "content": "اكتب حقيقة علمية مذهلة باللغة العربية. ابدأ بـ 'هل تعلم أن'. اجعلها جملة واحدة أو جملتين كحد أقصى لتناسب الشاشة."
        }]
    )
    return response.choices[0].message.content.strip()

async def text_to_speech(text, output="voice.mp3"):
    """تحويل النص لصوت سعودي طبيعي"""
    communicate = edge_tts.Communicate(text, voice="ar-SA-HamedNeural")
    await communicate.save(output)

def get_background_video():
    """جلب فيديو خلفية متحرك بدلاً من صورة ثابتة"""
    headers = {"Authorization": PEXELS_API_KEY}
    # البحث عن فيديوهات طبيعة أو فضاء بدقة عمودية
    url = "https://api.pexels.com/videos/search?query=galaxy+stars&orientation=portrait&per_page=1"
    res = requests.get(url, headers=headers).json()
    video_url = res["videos"][0]["video_files"][0]["link"]
    
    video_data = requests.get(video_url).content
    with open("bg_video.mp4", "wb") as f:
        f.write(video_data)

def process_text_for_pillow(text, max_width=900):
    """إصلاح النص العربي وتغليفه ليناسب العرض"""
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

def create_text_image(text, duration):
    """تحويل النص إلى صورة شفافة مع معالجة اللغة العربية"""
    # إعداد الخط (تأكد من المسار أو استخدم اسم الخط مباشرة إذا كان منصب)
    try:
        font = ImageFont.truetype("arial.ttf", 60) # أو مسار خط يدعم العربية
    except:
        font = ImageFont.load_default()

    img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # معالجة النص العربي
    processed_text = process_text_for_pillow(text)
    
    # رسم النص في المنتصف مع ظل بسيط للوضوح
    w, h = 1080, 1920
    draw.text((w/2, h/2), processed_text, font=font, fill="white", anchor="mm", align="center", stroke_width=2, stroke_fill="black")
    
    return np.array(img)

def make_video(fact_text):
    """تجميع العناصر لإنتاج الفيديو النهائي"""
    audio = AudioFileClip("voice.mp3")
    
    # تحميل فيديو الخلفية وقصه على مدة الصوت
    bg_video = VideoFileClip("bg_video.mp4").resize((1080, 1920)).subclip(0, audio.duration)
    
    # إضافة طبقة تعتيم خفيفة للفيديو الأصلي لبروز النص
    dark_overlay = bg_video.colorx(0.6) 

    # إنشاء نص احترافي (استخدام ImageClip بدلاً من TextClip لتفادي مشاكل ImageMagick)
    from moviepy.editor import ImageClip
    text_frame = create_text_image(fact_text, audio.duration)
    text_clip = ImageClip(text_frame).set_duration(audio.duration).set_position('center')

    # الدمج النهائي
    final_video = CompositeVideoClip([dark_overlay, text_clip]).set_audio(audio)
    final_video.write_videofile("output_final.mp4", fps=24, codec="libx264", audio_codec="aac")

async def main():
    print("1. توليد النص...")
    fact = generate_fact()
    print(f"النص: {fact}")

    print("2. توليد الصوت وجلب الفيديو...")
    await asyncio.gather(
        text_to_speech(fact),
        asyncio.to_thread(get_background_video)
    )

    print("3. مونتاج الفيديو النهائي...")
    make_video(fact)
    print("تم بنجاح! الملف: output_final.mp4")

if __name__ == "__main__":
    asyncio.run(main())
