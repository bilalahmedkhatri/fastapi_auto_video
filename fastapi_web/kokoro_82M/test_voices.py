"""Quick test script for multiple voice types."""

from kokoro_voice_generator import KokoroVoiceGenerator
from pathlib import Path

def test_multiple_voices():
    """Test voice generation with multiple voice types."""
    gen = KokoroVoiceGenerator()
    
    # Test multiple voices
    voices = ['af_sarah', 'am_michael', 'bf_emma', 'bm_lewis']
    texts = [
        'Hello, I am Sarah',
        'Greetings from Michael',
        'Good morning, this is Emma',
        'How do you do, Lewis here'
    ]
    
    print('🎤 Testing Multiple Voices...\n')
    print('=' * 60)
    print(f'{"Voice":<15} | {"Duration":<12} | {"File"}')
    print('=' * 60)
    
    success_count = 0
    for voice, text in zip(voices, texts):
        try:
            path, meta = gen.generate_voice(text, voice_type=voice, normalize=True)
            duration = meta['duration_seconds']
            filename = Path(path).name
            print(f'{voice:<15} | {duration:>5.2f}s       | {filename}')
            success_count += 1
        except Exception as e:
            print(f'{voice:<15} | ERROR          | {str(e)[:40]}')
    
    print('=' * 60)
    print(f'\n✨ Results: {success_count}/{len(voices)} voices generated successfully')
    
    # List all generated files
    print('\n📁 Generated files in media/voiceover/user/:')
    user_dir = Path('media/voiceover/user')
    if user_dir.exists():
        wav_files = sorted(user_dir.glob('*.wav'), reverse=True)
        for wav_file in wav_files[:5]:  # Show last 5
            size_kb = wav_file.stat().st_size / 1024
            print(f'  - {wav_file.name} ({size_kb:.1f} KB)')

if __name__ == '__main__':
    test_multiple_voices()
