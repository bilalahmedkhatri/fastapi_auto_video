import replicate
import aiohttp
import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from .voices_replicate_json import voices
from dotenv import load_dotenv
load_dotenv()


def generate_voice_replicate(text: str, output_path: str = "voiceover.wav", voice="am_puck", speed=1):
    """
    Asynchronously generate voiceover from text using Replicate Kokoro model and save to disk.
    Returns the URL of the generated audio file.
    """
    
    MODEL_ID = "jaaari/kokoro-82m:f559560eb822dc509045f3921a1921234918b91739db4bf3daab2169b71c7a13"
    output = replicate.run(
        MODEL_ID,
        input={
            "text": text,
            "speed": speed,
            "voice": voice,
        }
    )
    # Handle FileOutput object or direct URL
    return output.url

async def download_voice_replicate(text: str, output_path: str = "voiceover.wav", voice="am_puck", speed=1):
    
    loop = asyncio.get_event_loop()
    
    with ThreadPoolExecutor() as pool:
        url = await loop.run_in_executor(pool, generate_voice_replicate, text, output_path, voice, speed)
    
    if not isinstance(url, str):
        raise ValueError("Expected URL string from Replicate, got: {}".format(type(url)))
    
    # Download and save the audio file
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                with open(output_path, "wb") as file:
                    file.write(await resp.read())
                    return str(output_path)
            else:
                raise Exception(f"Failed to download audio from Replicate: {resp.status}")
    return output_path


def select_voice():
    
    t = "Breaking news on two wheels! 2023 is delivering absolute fire in the motorcycle world. At number 5, Yamaha's MT-09 SP gets Öhlins suspension and refined electronics. Next, the screaming Kawasaki Ninja ZX-4RR brings 16,000 RPM thrills to the 400cc class. At mid-point, BMW's R 1300 GS adventure bike sheds weight while gaining power and radar-assisted tech. The podium spot goes to Ducati's Streetfighter V4 Lamborghini edition—63 horsepower per liter wrapped in carbon fiber and Italian flair. But our showstopper? Harley-Davidson's Nightster Special, blending classic cruiser style with modern Revolution Max 975 torque. Which 2023 machine has your heart racing? Comment below!"
    
    path = r"G:\Development\auto_movie_editor\tools\ai_apis"
    
    n = 0
    for v in voices['American_English']:
        n = n + 1 
        r = asyncio.run(generate_voice_replicate(t, f"{path}\\voices_{n}_{v}.wav", v))
        x = asyncio.sleep(2)
        print(f"Generated voiceover saved to {r}.")
        
        
        
async def generate_voice_murf(
    text: str,
    output_path: str = "voiceover_murf.wav",
    voiceId: str = "en-US-natalie",
    audioDuration: int = 1,
    format: str = "WAV",
    channelType: str = "STEREO",
    modelVersion: str = "GEN2",
    style: str = "",
    pitch: int = 0
) -> str:
    """
    Asynchronously generate voiceover from text using Murf API and save to disk.
    All Murf parameters are exposed for customization.
    Returns the URL of the generated audio file.
    Murf API requires an API key and specific endpoint.
    """
    api_key = os.getenv("MURF_API_KEY")
    if api_key is None:
        raise ValueError("Murf API key is required.")
    murf_endpoint = "https://api.murf.ai/v1/speech/generate"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "voiceId": voiceId,
        "audioDuration": audioDuration,
        "format": format,
        "channelType": channelType,
        "modelVersion": modelVersion,
        "style": style,
        "pitch": pitch
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(murf_endpoint, json=payload, headers=headers) as resp:
            if resp.status == 200:
                print('response 200 from Murf AI.')
                data = await resp.json()
                audio_url = data.get("audio_url")
                if not audio_url:
                    raise Exception("No audio_url found in Murf response.")
                async with session.get(audio_url) as audio_resp:
                    if audio_resp.status == 200:
                        with open(output_path, "wb") as file:
                            file.write(await audio_resp.read())
                    else:
                        raise Exception(f"Failed to download audio from Murf: {audio_resp.status}")
                return audio_url
            else:
                error_text = await resp.text()
                raise Exception(f"Murf API error: {resp.status} {error_text}")

# select_voice()

# t = "Breaking news on two wheels! 2023 is delivering absolute fire in the motorcycle world. At number 5, Yamaha's MT-09 SP gets Öhlins suspension and refined electronics. Next, the screaming Kawasaki Ninja ZX-4RR brings 16,000 RPM thrills to the 400cc class. At mid-point, BMW's R 1300 GS adventure bike sheds weight while gaining power and radar-assisted tech. The podium spot goes to Ducati's Streetfighter V4 Lamborghini edition—63 horsepower per liter wrapped in carbon fiber and Italian flair. But our showstopper? Harley-Davidson's Nightster Special, blending classic cruiser style with modern Revolution Max 975 torque. Which 2023 machine has your heart racing? Comment below!"
# path = r"G:\Development\auto_movie_editor\tools\ai_apis\voice_gen_api_2.wav"
# r = asyncio.run(generate_voice_replicate(t, path))
# print('result is :', r)