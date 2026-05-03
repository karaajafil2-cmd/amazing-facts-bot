import edge_tts
import asyncio
import os
import requests
from groq import Groq
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, ColorClip, VideoFileClip
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
            "content": "اكتب حقيقة علمية مذهلة باللغة العربية. تبدأ بـ 'هل تعلم أن...' وتكون 3 جمل مفصلة ومثيرة. لا تضع مقدمة."
        }]
    )
    return response.choices[0].message.content

async def text_to_speech(text, output="voice.mp3"):
    communicate = edge_tts.Communicate(text, voice="ar-SA-HamedNeural")
    await communicate.save(output)

def get_image():
    headers = {"Authorization": PEXELS_API_KEY}
    res = requests.get(
        "https://api.pexels.com/v1/search?query=space+universe+galaxy&per_page=1",
        headers=headers
    ).json()
    img_url = res["photo
