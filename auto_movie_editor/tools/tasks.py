import asyncio
from worker import celery_app
# from image_processor import ImageProcessor  # Your existing class
from local_searxng_deepseek_copy_chatGPT import ImageProcessor

language_country_codes = [
    "en-US",   # English (United States)
    "en-GB",   # English (United Kingdom)
    "es-ES",   # Spanish (Spain)
    "es-MX",   # Spanish (Mexico)
    "fr-FR",   # French (France)
    "de-DE",   # German (Germany)
    "it-IT",   # Italian (Italy)
    "pt-PT",   # Portuguese (Portugal)
    "pt-BR",   # Portuguese (Brazil)
    "ru-RU",   # Russian (Russia)
    "ja-JP",   # Japanese (Japan)
    "ko-KR",   # Korean (South Korea)
    "zh-CN",   # Chinese (Simplified, China)
    "zh-TW",   # Chinese (Traditional, Taiwan)
    "ar-SA",   # Arabic (Saudi Arabia)
    "nl-NL",   # Dutch (Netherlands)
    "tr-TR",   # Turkish (Turkey)
    "el-GR",   # Greek (Greece)
    "hi-IN",   # Hindi (India)
    "sv-SE",   # Swedish (Sweden)
    "pl-PL",   # Polish (Poland)
    "th-TH",   # Thai (Thailand)
    "vi-VN",   # Vietnamese (Vietnam)
    "he-IL",   # Hebrew (Israel)
    "id-ID",   # Indonesian (Indonesia)
    "no-NO",   # Norwegian (Norway)
    "fi-FI",   # Finnish (Finland)
    "da-DK",   # Danish (Denmark)
    "cs-CZ",   # Czech (Czech Republic)
    "hu-HU",   # Hungarian (Hungary)
]

@celery_app.task()
def process_images_task(params: dict, username: str):
    print('process start')
    processor = ImageProcessor(username)
    asyncio.run(processor.process_images(params, username))
