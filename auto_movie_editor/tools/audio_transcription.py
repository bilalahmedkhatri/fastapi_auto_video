import whisper_timestamped as whisper
from pprint import pprint
import json
import os


def split_segments_to_max_words(result, max_words=5):
    """
    Splits each segment in the transcription result into smaller segments with up to max_words words.
    Each new segment will have its own text, start, end, and words list.
    """
    new_segments = []
    for segment in result.get("segments", []):
        words = segment.get("words", [])
        for i in range(0, len(words), max_words):
            chunk = words[i:i+max_words]
            if not chunk:
                continue
            new_text = " ".join([w["text"] for w in chunk])
            new_segment = {
                "id": len(new_segments),
                "seek": segment.get("seek", 0),
                "start": chunk[0]["start"],
                "end": chunk[-1]["end"],
                "text": new_text,
                "words": chunk,
            }
            # Optionally copy other fields from the original segment if needed
            new_segments.append(new_segment)
    # Copy the rest of the result, but replace segments
    new_result = dict(result)
    new_result["segments"] = new_segments
    return new_result


def transcribe_audio_to_json(audio_file_path, output_json_path=None):
    """
    Transcribes the given audio file using whisper_timestamped and saves the result as a JSON file.
    Args:
        audio_file_path (str): Path to the audio file.
        output_json_path (str, optional): Path to save the JSON result. If None, saves as <audio_file>.json
    Returns:
        bool: True if successful, False otherwise.
    """
    if not os.path.isfile(audio_file_path):
        print(f"Error: File not found: {audio_file_path}")
        return False
    
    audio = whisper.load_audio(audio_file_path)
    model = whisper.load_model("small")
    result = whisper.transcribe(model, audio)

    # Limit each segment to 5 words
    result = split_segments_to_max_words(result, max_words=5)

    if not output_json_path:
        output_json_path = os.path.splitext(audio_file_path)[0] + ".json"

    try:
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"Transcription saved to {output_json_path}")
        return True
    except Exception as e:
        print(f"Error saving JSON: {e}")
        return False


if __name__ == "__main__":
    file = r"G:\\Development\\auto_movie_editor\\tools\\ds_movie_voice.mp3"
    transcribe_audio_to_json(file)
