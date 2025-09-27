import replicate

class SegmentGenerator:
    """
    Class for handling segmentation of text, audio, or video.
    Also supports audio transcription using Replicate Whisper API.
    """

    def __init__(self):
        pass

    def segment_text(self, text: str, max_length: int = 100) -> list:
        """
        Split text into segments of max_length characters.

        Args:
            text: The input text to segment.
            max_length: Maximum length of each segment.

        Returns:
            List of text segments.
        """
        segments = []
        current = ""
        for word in text.split():
            if len(current) + len(word) + 1 > max_length:
                segments.append(current.strip())
                current = word
            else:
                current += " " + word
        if current:
            segments.append(current.strip())
        return segments

    def segment_audio(self, transcript: list, max_duration: float = 10.0) -> list:
        """
        Split transcript segments so that each segment does not exceed max_duration seconds.

        Args:
            transcript: List of transcript segments, each with 'start' and 'end' times.
            max_duration: Maximum duration per segment in seconds.

        Returns:
            List of segmented transcript dicts.
        """
        segments = []
        current = []
        current_start = None
        current_end = None
        for seg in transcript:
            seg_start = seg.get('start', 0)
            seg_end = seg.get('end', 0)
            if current_start is None:
                current_start = seg_start
            current_end = seg_end
            current.append(seg)
            if current_end - current_start >= max_duration:
                segments.append(current)
                current = []
                current_start = None
                current_end = None
        if current:
            segments.append(current)
        return segments

    def segment_video(self, total_duration: float, segment_length: float = 10.0) -> list:
        """
        Split video duration into segments of segment_length seconds.

        Args:
            total_duration: Total duration of the video in seconds.
            segment_length: Desired segment length in seconds.

        Returns:
            List of (start, end) tuples for each segment.
        """
        segments = []
        start = 0.0
        while start < total_duration:
            end = min(start + segment_length, total_duration)
            segments.append((start, end))
            start = end
        return segments

    def transcribe_audio(self, audio_url: str, language: str = "None", timestamp: str = "chunk", batch_size: int = 64, diarise_audio: bool = False) -> dict:
        """
        Transcribe audio using Replicate Whisper API.

        Args:
            audio_url: URL to the audio file.
            language: Language code or "None" for auto.
            timestamp: Timestamp granularity ("chunk", "word", etc.).
            batch_size: Batch size for processing.
            diarise_audio: Whether to diarise speakers.

        Returns:
            Transcription result as a dict.
        """
        output = replicate.run(
            "vaibhavs10/incredibly-fast-whisper:3ab86df6c8f54c11309d4d1f930ac292bad43ace52d10c80d87eb258b3c9f79c",
            input={
                "task": "transcribe",
                "audio": audio_url,
                "language": language,
                "timestamp": timestamp,
                "batch_size": batch_size,
                "diarise_audio": diarise_audio
            }
        )
        return output
