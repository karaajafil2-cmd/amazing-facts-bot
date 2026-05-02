import edge_tts
import asyncio
import os
import requests
from groq import Groq
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")

def generate_fact():
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "اكتب حقيقة مذهلة وغير معروفة باللغة العربية. جملة واحدة فقط. لا تضع مقدمة."}]
    )
    return response.choices[0].message.content

async def text_to_speech(text, output="voice.mp3"):
    communicate = edge_tts.Communicate(text, voice="ar-SA-HamedNeural")
    await communicate.save(output)

def get_image():
    headers = {"Authorization": PEXELS_API_KEY}
    res = requests.get("https://api.pexels.com/v1/search?query=nature&per_page=1", headers=headers).json()
    img_url = res["photos"][0]["src"]["large"]
    img_data = requests.get(img_url).content
    with open("bg.jpg", "wb") as f:
        f.write(img_data)

def make_frame(fact_text, size=(1080, 1920)):
    img = Image.open("bg.jpg").resize(size)
    overlay = Image.new("RGBA", size, (0, 0, 0, 128))
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
    except:
        font = ImageFont.load_default()
    
    words = fact_text.split()
    lines = []
    line = ""
    for word in words:
        if len(line + word) < 25:
            line += word + " "
        else:
            lines.append(line.strip())
            line = word + " "
    lines.append(line.strip())
    
    text_block = "\n".join(lines)
    bbox = draw.textbbox((0, 0), text_block, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = (size[0] - w) // 2
    y = (size[1] - h) // 2
    draw.text((x, y), text_block, font=font, fill="white", align="center")
    return np.array(img.convert("RGB"))

def make_video(fact_text):
    audio = AudioFileClip("voice.mp3")
    duration = audio.duration
    frame = make_frame(fact_text)
    video = ImageClip(frame).set_duration(duration).set_audio(audio)
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
