import requests
import json

for i in range(3):
    r = requests.post(
        'http://localhost:8000/api/voiceover/free_tool',
        json={'text': f'Test number {i+1}', 'voice_id': 'af_sarah'}
    )
    data = r.json()
    print(f'Request {i+1}: Status {r.status_code}, Remaining: {data.get("remaining_uses", "N/A")}')
    if r.status_code != 200:
        print(f'  Error: {data.get("detail", "Unknown")}')
