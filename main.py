import edge_tts
import asyncio
import os
import requests
from groq import Groq
from moviepy.editor import *

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")

def generate_fact():
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{
            "role": "user",
            "content": "اكتب حقيقة مذهلة وغير معروفة باللغة العربية. جملة واحدة فقط. لا تضع مقدمة."
        }]
    )
    return response.choices[0].message.content

async def text_to_speech(text, output="voice.mp3"):
    communicate = edge_tts.Communicate(text, voice="ar-SA-HamedNeural")
    await communicate.save(output)

def get_image():
    headers = {"Authorization": PEXELS_API_KEY}
    res = requests.get(
        "https://api.pexels.com/v1/search?query=nature+amazing&per_page=1",
        headers=headers
    ).json()
    img_url = res["photos"][0]["src"]["large"]
    img_data = requests.get(img_url).content
    with open("bg.jpg", "wb") as f:
        f.write(img_data)

def make_video(fact_text):
    audio = AudioFileClip("voice.mp3")
    duration = audio.duration
    bg = ImageClip("bg.jpg").set_duration(duration).resize((1080, 1920))
    txt = TextClip(
        fact_text,
        fontsize=60,
        color="white",
        font="Arial",
        size=(900, None),
        method="caption",
        align="center"
    ).set_duration(duration).set_position("center")
    overlay = ColorClip((1080, 1920), color=(0,0,0)).set_opacity(0.5).set_duration(duration)
    video = CompositeVideoClip([bg, overlay, txt]).set_audio(audio)
    video.write_videofile("output.mp4", fps=24, codec="libx264")

if __name__ == "__main__":
    print("⏳ جاري توليد الحقيقة...")
    fact = generate_fact()
    print(f"✅ الحقيقة: {fact}")
    print("⏳ جاري توليد الصوت...")
    asyncio.run(text_to_speech(fact))
    print("⏳ جاري جلب الصورة...")
    get_image()
    print("⏳ جاري صنع الفيديو...")
    make_video(fact)
    print("✅ الفيديو جاهز: output.mp4")
   
