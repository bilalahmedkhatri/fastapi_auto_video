
import logging
import whisper_timestamped as whisper
import json
import os
import shutil
from typing import Optional


class WhisperTranscriber:
    def __init__(
        self,
        model_size: str = "small",
        language: Optional[str] = None,
        ensure_ffmpeg: bool = True,
        ffmpeg_path: Optional[str] = None,
    ):
        """Wrapper around whisper_timestamped with extra utilities.

        Args:
            model_size: whisper model size (tiny, base, small, medium, large-v2, etc.)
            language: Optional language code (e.g. 'en'). If None whisper auto-detects.
            ensure_ffmpeg: If True, attempt to locate or provision an ffmpeg executable.
        """
        # Basic logging config if not already configured
        if not logging.getLogger().handlers:
            logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

        self.model_size = model_size
        self.language = language
        self.explicit_ffmpeg_path = ffmpeg_path or os.environ.get("FFMPEG_PATH")
        if ensure_ffmpeg:
            self._ensure_ffmpeg_available()
        logging.info("Loading whisper model '%s'...", model_size)
        self.model = whisper.load_model(model_size)
        logging.info("Whisper model loaded.")

    # --- utility ---------------------------------------------------------
    def _ensure_ffmpeg_available(self):
        """Ensure ffmpeg is callable by the name 'ffmpeg'.

        Resolution order:
          1. Explicit path provided via constructor or FFMPEG_PATH env var.
          2. Already on PATH.
          3. Common Windows install locations.
          4. imageio-ffmpeg package.
        After locating, we prepend its directory to PATH (session only) and verify
        with `ffmpeg -version`. Logs diagnostic info if still unavailable.
        """
        candidates = []
        if self.explicit_ffmpeg_path:
            candidates.append(self.explicit_ffmpeg_path)
        # Already on PATH?
        existing = shutil.which("ffmpeg")
        if existing:
            candidates.append(existing)
        # Common Windows locations
        common_dirs = [
            r"C:\\ffmpeg\\bin\\ffmpeg.exe",
            r"C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
            r"C:\\Program Files (x86)\\ffmpeg\\bin\\ffmpeg.exe",
            r"D:\\ffmpeg\\bin\\ffmpeg.exe",
        ]
        candidates.extend(common_dirs)
        # imageio-ffmpeg fallback
        try:
            import imageio_ffmpeg  # type: ignore
            candidates.append(imageio_ffmpeg.get_ffmpeg_exe())
        except Exception:
            pass

        chosen = None
        for c in candidates:
            if c and os.path.isfile(c):
                chosen = c
                break

        if chosen:
            bin_dir = os.path.dirname(chosen)
            if shutil.which("ffmpeg") != chosen:
                if bin_dir not in os.environ.get("PATH", ""):
                    os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
            logging.info("Using ffmpeg at: %s", chosen)
            # Verify invocation
            import subprocess
            try:
                res = subprocess.run([chosen, "-version"], capture_output=True, text=True, timeout=5)
                if res.returncode != 0:
                    logging.warning("ffmpeg -version returned non-zero exit %s: %s", res.returncode, res.stderr[:200])
                else:
                    first_line = res.stdout.splitlines()[0] if res.stdout else "(no output)"
                    logging.info("ffmpeg version: %s", first_line)
            except Exception as e:
                logging.warning("Failed to execute ffmpeg for verification: %s", e)
            return

        # If still not found, emit detailed diagnostics
        logging.error("ffmpeg not found. PATH=%s", os.environ.get("PATH"))
        raise FileNotFoundError(
            "ffmpeg executable not found. Provide path via constructor ffmpeg_path=, set FFMPEG_PATH env var, "
            "or install and ensure ffmpeg.exe directory is on PATH."
        )

    def transcribe_audio_to_json(self, audio_file_path: str, max_words: int = 5, language: Optional[str] = None):
        """
        Transcribes the given audio file using whisper_timestamped and saves the result as a JSON file.
        Args:
            audio_file_path (str): Path to the audio file.
            output_json_path (str, optional): Path to save the JSON result. If None, saves as <audio_file>.json
            max_words (int): Maximum words per segment.
        Returns:
            bool: True if successful, False otherwise.
        """
        if not os.path.isfile(audio_file_path):
            raise FileNotFoundError(f"Audio file does not exist: {audio_file_path}")

        # Extra diagnostics before attempting to load
        logging.info("Transcribing file: %s", audio_file_path)
        logging.info("Current working directory: %s", os.getcwd())
        logging.info("ffmpeg resolved path: %s", shutil.which("ffmpeg"))
        try:
            audio = whisper.load_audio(audio_file_path)
        except FileNotFoundError as e:
            # Common cause: ffmpeg missing or path contains problematic chars
            raise FileNotFoundError(
                "Failed to load audio via ffmpeg. Ensure ffmpeg is installed and on PATH. Original error: " + str(e)
            ) from e
        except Exception as e:
            raise RuntimeError(f"Unexpected error while loading audio: {e}") from e
        # Use provided language or default to instance language
        lang = language if language is not None else self.language
        result = whisper.transcribe(self.model, audio, language=str(lang))

        # Limit each segment to max_words
        result = self.split_segments_to_max_words(result, max_words=max_words)

        output_json_path = os.path.splitext(audio_file_path)[0] + '.json'
            
        try:
            with open(output_json_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            logging.info(f'Transcription completed and file generated at {output_json_path}.')
            return result
        except Exception as e:
            print(f"Error saving JSON: {e}")
            return False

    def split_segments_to_max_words(self, result: dict, max_words: int = 5):
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


if __name__ == "__main__":
    # Quick interactive diagnostics
    test_file = r"d:\dev\auto_movie_editor\tools\ai_voice_gen_667.mp3"
    # If you know the path to ffmpeg.exe explicitly, set it here or via env var FFMPEG_PATH
    explicit_ffmpeg = None  # e.g. r"C:\\ffmpeg\\bin\\ffmpeg.exe"
    transcriber = WhisperTranscriber(language="en", ffmpeg_path=explicit_ffmpeg)
    try:
        transcriber.transcribe_audio_to_json(test_file)
    except Exception as e:
        logging.error("Transcription failed: %s", e)
        print("Transcription failed:", e)
