import edge_tts
import asyncio
import os
import requests
import random
from groq import Groq
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import arabic_reshaper
from bidi.algorithm import get_display

# إعداد المفاتيح من بيئة العمل (GitHub Secrets)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")

def generate_fact():
    """توليد حقيقة علمية باستخدام ذكاء اصطناعي"""
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user", 
            "content": "اكتب حقيقة علمية مذهلة باللغة العربية. ابدأ بـ 'هل تعلم أن'. اجعلها جملة واحدة قصيرة جداً لتناسب شاشة الهاتف."
        }]
    )
    return response.choices[0].message.content.strip()

async def text_to_speech(text, output="voice.mp3"):
    """تحويل النص لصوت سعودي طبيعي"""
    communicate = edge_tts.Communicate(text, voice="ar-SA-HamedNeural")
    await communicate.save(output)

def get_background_video():
    """جلب فيديو خلفية من Pexels"""
    headers = {"Authorization": PEXELS_API_KEY}
    url = "https://api.pexels.com/videos/search?query=nature+galaxy&orientation=portrait&per_page=10"
    res = requests.get(url, headers=headers).json()
    # اختيار فيديو عشوائي من النتائج لزيادة التنوع
    video_url = random.choice(res["videos"])["video_files"][0]["link"]
    video_data = requests.get(video_url).content
    with open("bg_video.mp4", "wb") as f:
        f.write(video_data)

def create_text_frame(text, font_path="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
    """صناعة صورة نصية شفافة مع معالجة اللغة العربية"""
    # إعادة تشكيل النص العربي ليظهر بشكل صحيح
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    
    img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype(font_path, 60)
    except:
        font = ImageFont.load_default()

    # رسم النص في المنتصف مع ظل أسود للوضوح
    w, h = 1080, 1920
    draw.text((w/2, h/2), bidi_text, font=font, fill="white", anchor="mm", align="center", stroke_width=2, stroke_fill="black")
    return np.array(img)

def make_video(fact_text):
    """تجميع الفيديو والصوت والنص"""
    audio = AudioFileClip("voice.mp3")
    bg_video = VideoFileClip("bg_video.mp4").resize((1080, 1920)).subclip(0, audio.duration)
    
    # إضافة تعتيم خفيف للخلفية لبروز النص
    dark_bg = bg_video.colorx(0.7)
    
    # تحويل النص إلى كليب فيديو
    text_img = create_text_frame(fact_text)
    text_clip = ImageClip(text_img).set_duration(audio.duration).set_position('center')

    # الدمج النهائي
    final_video = CompositeVideoClip([dark_bg, text_clip]).set_audio(audio)
    final_video.write_videofile("output.mp4", fps=24, codec="libx264", audio_codec="aac")

async def main():
    print("جاري التشغيل...")
    fact = generate_fact()
    print(f"الحقيقة المنتجة: {fact}")
    
    await asyncio.gather(
        text_to_speech(fact),
        asyncio.to_thread(get_background_video)
    )
    
    make_video(fact)
    print("تم إنتاج الفيديو بنجاح!")

if __name__ == "__main__":
    asyncio.run(main())
