"""
Kokoro Voice Generator - Core Generation Logic

Pure generator class without voice catalog management.
Voice selection is handled by the calling application.

Author: Auto Video Generator Team
Date: 2025-11-12
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
import numpy as np

try:
    import torch
except ImportError:
    raise ImportError("PyTorch required: pip install torch")

try:
    from scipy.io import wavfile
except ImportError:
    raise ImportError("scipy required: pip install scipy")

try:
    from kokoro import KPipeline
except ImportError:
    raise ImportError("Kokoro required: pip install kokoro-onnx")

try:
    from .config import KOKORO_CONFIG, AUDIO_CONFIG, FILE_CONFIG
except ImportError:
    from config import KOKORO_CONFIG, AUDIO_CONFIG, FILE_CONFIG


class KokoroVoiceGenerator:
    """Pure voice generation engine without voice catalog management."""
    
    def __init__(
        self,
        device: Optional[str] = None,
        output_base_dir: Optional[str] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize Kokoro voice generator.
        
        Args:
            device: 'cuda' or 'cpu' (auto-detect if None)
            output_base_dir: Base directory for audio files
            logger: Custom logger instance
        """
        self.output_base_dir = Path(output_base_dir or FILE_CONFIG["output_dir"])
        self.output_base_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logger or self._setup_logger()
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        
        self.logger.info(f"Using device: {self.device}")
        self._initialize_model()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup basic logging."""
        logger = logging.getLogger("KokoroGenerator")
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _initialize_model(self) -> None:
        """Initialize Kokoro pipeline."""
        try:
            self.model = KPipeline(
                lang_code=KOKORO_CONFIG["lang_code"],
                device=self.device
            )
            self.logger.info(f"Kokoro model initialized: {KOKORO_CONFIG['model_name']}")
        except Exception as e:
            self.logger.error(f"Model initialization failed: {str(e)}")
            raise RuntimeError(f"Failed to initialize Kokoro: {str(e)}")
    
    def _normalize_audio(self, audio: np.ndarray, target_db: float = None) -> np.ndarray:
        """Normalize audio to target loudness."""
        target_db = target_db or AUDIO_CONFIG["target_db"]
        rms = np.sqrt(np.mean(audio ** 2))
        
        if rms > 0:
            current_db = 20 * np.log10(rms)
            db_diff = target_db - current_db
            scaling_factor = 10 ** (db_diff / 20.0)
            audio = audio * scaling_factor
        
        return np.clip(audio, -1.0, 1.0)
    
    def _generate_timestamp_filename(self) -> str:
        """Generate timestamp-based filename."""
        return datetime.now().strftime(FILE_CONFIG["filename_format"])
    
    def generate_voice(
        self,
        text: str,
        voice_type: str,
        output_dir: Optional[str] = None,
        filename: Optional[str] = None,
        speed: float = None,
        normalize: bool = True,
        save_metadata: bool = True
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate voice from text.
        
        Args:
            text: Text to synthesize
            voice_type: Voice identifier (e.g., "af_sarah", "am_michael")
            output_dir: Custom output directory
            filename: Custom filename (without extension)
            speed: Speech speed (0.5-2.0, default 1.0)
            normalize: Apply audio normalization
            save_metadata: Save JSON metadata file
        
        Returns:
            Tuple of (audio_file_path, metadata_dict)
        
        Raises:
            ValueError: Invalid input parameters
            RuntimeError: Generation failed
        """
        # Validate inputs
        if not text or not isinstance(text, str):
            raise ValueError("Text must be a non-empty string")
        
        text = text.strip()
        if not text:
            raise ValueError("Text cannot be empty")
        
        speed = speed or AUDIO_CONFIG["speed_default"]
        if not (AUDIO_CONFIG["speed_min"] <= speed <= AUDIO_CONFIG["speed_max"]):
            raise ValueError(f"Speed must be between {AUDIO_CONFIG['speed_min']} and {AUDIO_CONFIG['speed_max']}")
        
        try:
            self.logger.info(f"Generating: text='{text[:50]}...', voice={voice_type}")
            
            # Generate audio using KPipeline
            result = next(self.model(text=text, voice=voice_type.lower(), speed=speed))
            audio_tensor = result.audio
            
            # Convert to numpy
            audio = audio_tensor.cpu().numpy() if isinstance(audio_tensor, torch.Tensor) else np.array(audio_tensor)
            
            # Ensure mono
            if audio.ndim > 1:
                audio = np.mean(audio, axis=0)
            
            # Normalize
            if normalize:
                audio = self._normalize_audio(audio)
            
            # Prepare output
            output_path = Path(output_dir) if output_dir else self.output_base_dir
            output_path.mkdir(parents=True, exist_ok=True)
            
            filename = filename or self._generate_timestamp_filename()
            audio_file = output_path / f"{filename}{FILE_CONFIG['audio_extension']}"
            
            # Save audio
            audio_int16 = np.clip(audio * 32767, -32768, 32767).astype(np.int16)
            wavfile.write(str(audio_file), KOKORO_CONFIG["sample_rate"], audio_int16)
            
            # Create metadata
            metadata = {
                "text": text,
                "voice_type": voice_type,
                "audio_file": str(audio_file),
                "sample_rate": KOKORO_CONFIG["sample_rate"],
                "duration_seconds": float(audio.shape[0] / KOKORO_CONFIG["sample_rate"]),
                "speed": speed,
                "normalized": normalize,
                "generated_at": datetime.now().isoformat(),
                "file_size_bytes": audio_file.stat().st_size
            }
            
            # Save metadata
            if save_metadata:
                metadata_file = output_path / f"{filename}{FILE_CONFIG['metadata_suffix']}"
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
                metadata["metadata_file"] = str(metadata_file)
            
            self.logger.info(f"Generated: {audio_file.name} ({metadata['duration_seconds']:.2f}s)")
            
            return str(audio_file), metadata
        
        except Exception as e:
            self.logger.error(f"Generation failed: {str(e)}")
            raise RuntimeError(f"Voice generation failed: {str(e)}")
    
    def generate_batch_voices(
        self,
        texts: List[str],
        voice_types: List[str],
        output_dir: Optional[str] = None,
        **kwargs
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Generate multiple voices in batch.
        
        Args:
            texts: List of texts to synthesize
            voice_types: List of voice identifiers (must match texts length)
            output_dir: Output directory for all files
            **kwargs: Additional arguments for generate_voice
        
        Returns:
            List of (audio_path, metadata) tuples
        """
        if not texts:
            raise ValueError("Texts list cannot be empty")
        
        if len(voice_types) == 1:
            voice_types = voice_types * len(texts)
        elif len(voice_types) != len(texts):
            raise ValueError(f"voice_types ({len(voice_types)}) must match texts ({len(texts)})")
        
        results = []
        for i, (text, voice_type) in enumerate(zip(texts, voice_types)):
            try:
                self.logger.info(f"Batch {i+1}/{len(texts)}")
                audio_path, metadata = self.generate_voice(
                    text=text,
                    voice_type=voice_type,
                    output_dir=output_dir,
                    **kwargs
                )
                results.append((audio_path, metadata))
            except Exception as e:
                self.logger.error(f"Batch item {i+1} failed: {str(e)}")
                continue
        
        self.logger.info(f"Batch complete: {len(results)}/{len(texts)} successful")
        return results
    
    def list_generated_voices(
        self,
        output_dir: Optional[str] = None,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """List all generated voice files."""
        search_dir = Path(output_dir) if output_dir else self.output_base_dir
        
        if not search_dir.exists():
            return []
        
        audio_files = []
        for wav_file in sorted(search_dir.glob(f"*{FILE_CONFIG['audio_extension']}")):
            file_info = {
                "filename": wav_file.name,
                "path": str(wav_file),
                "size_kb": wav_file.stat().st_size / 1024,
                "created_at": datetime.fromtimestamp(wav_file.stat().st_ctime).isoformat(),
            }
            
            if include_metadata:
                metadata_file = wav_file.parent / f"{wav_file.stem}{FILE_CONFIG['metadata_suffix']}"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r') as f:
                            file_info["metadata"] = json.load(f)
                    except Exception:
                        pass
            
            audio_files.append(file_info)
        
        return audio_files
    
    def delete_voice_file(
        self,
        filename: str,
        output_dir: Optional[str] = None,
        delete_metadata: bool = True
    ) -> bool:
        """Delete a generated voice file."""
        search_dir = Path(output_dir) if output_dir else self.output_base_dir
        
        if not filename.endswith(FILE_CONFIG["audio_extension"]):
            filename = f"{filename}{FILE_CONFIG['audio_extension']}"
        
        file_path = search_dir / filename
        
        if not file_path.exists():
            self.logger.warning(f"File not found: {file_path}")
            return False
        
        try:
            file_path.unlink()
            self.logger.info(f"Deleted: {file_path}")
            
            if delete_metadata:
                metadata_path = search_dir / f"{file_path.stem}{FILE_CONFIG['metadata_suffix']}"
                if metadata_path.exists():
                    metadata_path.unlink()
            
            return True
        except Exception as e:
            self.logger.error(f"Delete failed: {str(e)}")
            return False
