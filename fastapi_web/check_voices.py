"""
Check voices in database
"""
from sqlmodel import Session, select
from models.db_models import SelectAIVoices, engine

def check_voices():
    session = Session(engine)
    
    # Get all active voices
    voices = session.exec(
        select(SelectAIVoices)
        .where(SelectAIVoices.is_active == True)
        .order_by(SelectAIVoices.voice_id)
    ).all()
    
    print(f'\n📊 Total Active Voices: {len(voices)}\n')
    print('=' * 100)
    print(f'{"#":3} | {"Voice ID":15} | {"Voice Name":20} | {"Gender":8} | {"Accent":15} | {"Language":8} | {"Provider":10}')
    print('=' * 100)
    
    for i, v in enumerate(voices, 1):
        print(f'{i:3} | {v.voice_id:15} | {v.voice_name:20} | {v.gender or "N/A":8} | {v.accent or "N/A":15} | {v.language:8} | {v.provider:10}')
    
    print('=' * 100)
    
    # Check for inactive voices
    inactive_voices = session.exec(
        select(SelectAIVoices)
        .where(SelectAIVoices.is_active == False)
    ).all()
    
    if inactive_voices:
        print(f'\n⚠️  Inactive Voices: {len(inactive_voices)}')
        for v in inactive_voices:
            print(f'   - {v.voice_id} ({v.voice_name})')
    
    session.close()

if __name__ == "__main__":
    check_voices()
