import edge_tts
import asyncio
import os
import requests
from groq import Groq
from moviepy.editor import ImageClip, AudioFileClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")

def generate_fact():
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": "اكتب حقيقة علمية مذهلة باللغة العربية. تبدأ بهل تعلم وتكون 3 جمل مفصلة. لا تضع مقدمة."
        }]
    )
    return response.choices[0].message.content

async def text_to_speech(text, output="voice.mp3"):
    communicate = edge_tts.Communicate(text, voice="ar-SA-HamedNeural")
    await communicate.save(output)

def get_image():
    headers = {"Authorization": PEXELS_API_KEY}
    url = "https://api.pexels.com/v1/search?query=space+galaxy&per_page=1"
    res = requests.get(url, headers=headers).json()
    img_url = res["photos"][0]["src"]["large2x"]
    img_data = requests.get(img_url).content
    with open("bg.jpg", "wb") as f:
        f.write(img_data)

def make_video(fact_text):
    audio = AudioFileClip("voice.mp3")
    duration = audio.duration
    img = Image.open("bg.jpg").resize((1080, 1920))
    overlay = Image.new("RGBA", (1080, 1920), (0, 0, 0, 140))
    img = img.convert("RGBA")
    from PIL import Image as PILImage
    img = PILImage.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
    except Exception:
        font = ImageFont.load_default()
    words = fact_text.split()
    lines = []
    line = ""
    for word in words:
        test = line + word + " "
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > 900:
            lines.append(line.strip())
            line = word + " "
        else:
            line = test
    if line:
        lines.append(line.strip())
    text_block = "\n".join(lines)
    draw.text((540, 960), text_block, font=font, fill="white", anchor="mm", align="center")
    frame = np.array(img.convert("RGB"))
    video = ImageClip(frame).set_duration(duration).set_audio(audio)
    video.write_videofile("output.mp4", fps=24, codec="libx264", audio_codec="aac")

if __name__ == "__main__":
    print("توليد الحقيقة...")
    fact = generate_fact()
    print(fact)
    print("توليد الصوت...")
    asyncio.run(text_to_speech(fact))
    print("جلب الصورة...")
    get_image()
    print("صنع الفيديو...")
    make_video(fact)
    print("الفيديو جاهز!")
