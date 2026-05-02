import edge_tts
import asyncio
import os
import requests
from groq import Groq
from moviepy.editor import ImageClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")

def generate_fact():
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
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
        "https://api.pexels.com/v1/search?query=nature&per_page=1",
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
    overlay = ColorClip((1080, 1920), color=(0,0,0)).set_opacity(0.5).set_duration(duration)
    txt = TextClip(
        fact_text,
        fontsize=55,
        color="white",
        size=(900, None),
        method="caption",
        align="center"
    ).set_duration(duration).set_position("center")
    video = CompositeVideoClip([bg, overlay, txt]).set_audio(audio)
    video.write_videofile("output.mp4", fps=24, codec="libx264", audio_codec="aac")

if __name__ == "__main__":
    print("⏳ توليد الحقيقة...")
    fact = generate_fact()
    print(f"✅ {fact}")
    print("⏳ توليد الصوت...")
    asyncio.run(text_to_speech(fact))
    print("⏳ جلب الصورة...")
    get_image()
    print("⏳ صنع الفيديو...")
    make_video(fact)
    print("✅ الفيديو جاهز!")
   
