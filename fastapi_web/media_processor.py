"""
Image and Video Processing Module for Auto Movie Editor
Handles comprehensive media analysis, processing, and validation
"""

import logging
import asyncio
import base64
import hashlib
import mimetypes
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any
from datetime import datetime
import json

# Image/Video processing libraries
import cv2
import numpy as np
from PIL import Image, ImageStat, ImageFilter
import ffmpeg

# Machine learning libraries for analysis
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    logging.warning("face_recognition not available - face detection disabled")

try:
    from ultralytics import YOLO
    OBJECT_DETECTION_AVAILABLE = True
except ImportError:
    OBJECT_DETECTION_AVAILABLE = False
    logging.warning("ultralytics not available - object detection disabled")

# Set up logging
logger = logging.getLogger(__name__)


class MediaAnalysisResult:
    """Data class for media analysis results"""
    
    def __init__(self):
        self.file_info = {}
        self.technical_specs = {}
        self.content_analysis = {}
        self.quality_metrics = {}
        self.processing_recommendations = {}
        self.errors = []
        self.warnings = []


class ImageVideoProcessor:
    """
    Comprehensive image and video processor for auto movie generation
    
    Features:
    - Media validation and format checking
    - Technical analysis (resolution, bitrate, duration, etc.)
    - Content analysis (faces, objects, scenes)
    - Quality assessment (sharpness, brightness, contrast)
    - Processing recommendations (cropping, effects, transitions)
    - Batch processing capabilities
    """
    
    def __init__(self):
        self.supported_image_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        self.supported_video_formats = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv'}
        self.max_file_size_mb = 500  # 500MB max file size
        
        # Initialize ML models if available
        self.yolo_model = None
        if OBJECT_DETECTION_AVAILABLE:
            try:
                self.yolo_model = YOLO('yolov8n.pt')  # Load nano model for speed
                logger.info("YOLO object detection model loaded")
            except Exception as e:
                logger.warning(f"Failed to load YOLO model: {e}")
                
        self.face_recognition_enabled = FACE_RECOGNITION_AVAILABLE
        if self.face_recognition_enabled:
            logger.info("Face recognition enabled")

    async def analyze_media_batch(self, media_items: List[Dict[str, Any]]) -> Dict[str, MediaAnalysisResult]:
        """
        Analyze multiple media items in parallel
        
        Args:
            media_items: List of media items with 'id', 'data', 'type' keys
            
        Returns:
            Dict mapping media_id to MediaAnalysisResult
        """
        logger.info(f"Starting batch analysis of {len(media_items)} media items")
        
        tasks = []
        for item in media_items:
            task = asyncio.create_task(
                self._analyze_single_media(item),
                name=f"analyze_{item.get('id', 'unknown')}"
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        analysis_results = {}
        for i, result in enumerate(results):
            media_id = media_items[i].get('id', f'item_{i}')
            if isinstance(result, Exception):
                logger.error(f"Analysis failed for {media_id}: {result}")
                error_result = MediaAnalysisResult()
                error_result.errors.append(str(result))
                analysis_results[media_id] = error_result
            else:
                analysis_results[media_id] = result
        
        logger.info(f"Batch analysis completed for {len(media_items)} items")
        return analysis_results

    async def _analyze_single_media(self, media_item: Dict[str, Any]) -> MediaAnalysisResult:
        """Analyze a single media item"""
        result = MediaAnalysisResult()
        
        try:
            media_id = media_item.get('id', 'unknown')
            media_data = media_item.get('data')  # Could be file path, base64, or bytes
            media_type = media_item.get('type', 'unknown')
            
            logger.info(f"Analyzing media item: {media_id} (type: {media_type})")
            
            # Determine file path or create temporary file
            file_path = await self._prepare_media_file(media_data, media_id)
            
            # Basic file validation
            await self._validate_media_file(file_path, result)
            if result.errors:
                return result
            
            # Determine if image or video
            if self._is_image(file_path):
                await self._analyze_image(file_path, result)
            elif self._is_video(file_path):
                await self._analyze_video(file_path, result)
            else:
                result.errors.append(f"Unsupported media type: {file_path.suffix}")
            
            # Add processing recommendations
            self._generate_processing_recommendations(result)
            
            logger.info(f"Analysis completed for {media_id}")
            
        except Exception as e:
            logger.error(f"Error analyzing media: {e}")
            result.errors.append(f"Analysis error: {str(e)}")
        
        return result

    async def _prepare_media_file(self, media_data: Union[str, bytes, None], media_id: str) -> Path:
        """Convert media data to file path"""
        if isinstance(media_data, str):
            if media_data.startswith('data:'):
                # Base64 data URL
                return await self._save_base64_to_temp(media_data, media_id)
            else:
                # File path
                return Path(media_data)
        elif isinstance(media_data, bytes):
            # Raw bytes
            return await self._save_bytes_to_temp(media_data, media_id)
        else:
            raise ValueError(f"Unsupported media data type: {type(media_data)}")

    async def _save_base64_to_temp(self, data_url: str, media_id: str) -> Path:
        """Save base64 data URL to temporary file"""
        try:
            # Parse data URL
            header, data = data_url.split(',', 1)
            mime_type = header.split(';')[0].split(':')[1]
            
            # Determine file extension
            extension = mimetypes.guess_extension(mime_type) or '.tmp'
            
            # Create temporary file
            temp_file = Path(tempfile.gettempdir()) / f"media_{media_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{extension}"
            
            # Decode and save
            file_data = base64.b64decode(data)
            with open(temp_file, 'wb') as f:
                f.write(file_data)
            
            return temp_file
            
        except Exception as e:
            raise ValueError(f"Failed to process base64 data: {e}")

    async def _save_bytes_to_temp(self, data: bytes, media_id: str) -> Path:
        """Save raw bytes to temporary file"""
        temp_file = Path(tempfile.gettempdir()) / f"media_{media_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tmp"
        
        with open(temp_file, 'wb') as f:
            f.write(data)
        
        return temp_file

    async def _validate_media_file(self, file_path: Path, result: MediaAnalysisResult):
        """Validate media file basics"""
        try:
            if not file_path.exists():
                result.errors.append("File does not exist")
                return
            
            # Check file size
            file_size = file_path.stat().st_size
            size_mb = file_size / (1024 * 1024)
            
            result.file_info = {
                'filename': file_path.name,
                'extension': file_path.suffix.lower(),
                'size_bytes': file_size,
                'size_mb': round(size_mb, 2),
                'path': str(file_path)
            }
            
            if size_mb > self.max_file_size_mb:
                result.errors.append(f"File too large: {size_mb:.1f}MB (max: {self.max_file_size_mb}MB)")
            
            # Check if supported format
            extension = file_path.suffix.lower()
            if extension not in (self.supported_image_formats | self.supported_video_formats):
                result.errors.append(f"Unsupported format: {extension}")
                
        except Exception as e:
            result.errors.append(f"File validation error: {str(e)}")

    def _is_image(self, file_path: Path) -> bool:
        """Check if file is an image"""
        return file_path.suffix.lower() in self.supported_image_formats

    def _is_video(self, file_path: Path) -> bool:
        """Check if file is a video"""
        return file_path.suffix.lower() in self.supported_video_formats

    async def _analyze_image(self, file_path: Path, result: MediaAnalysisResult):
        """Comprehensive image analysis"""
        try:
            # Load image with PIL
            with Image.open(file_path) as img:
                # Basic technical specs
                result.technical_specs = {
                    'width': img.width,
                    'height': img.height,
                    'mode': img.mode,
                    'format': img.format,
                    'aspect_ratio': round(img.width / img.height, 3),
                    'total_pixels': img.width * img.height
                }
                
                # Convert to RGB if necessary for analysis
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Quality metrics
                await self._analyze_image_quality(img, result)
                
                # Content analysis
                await self._analyze_image_content(img, result)
                
        except Exception as e:
            result.errors.append(f"Image analysis error: {str(e)}")

    async def _analyze_image_quality(self, img: Image.Image, result: MediaAnalysisResult):
        """Analyze image quality metrics"""
        try:
            # Convert to numpy array for analysis
            img_array = np.array(img)
            
            # Calculate basic statistics
            stat = ImageStat.Stat(img)
            
            # Brightness (average pixel value)
            brightness = sum(stat.mean) / len(stat.mean)
            
            # Contrast (standard deviation)
            contrast = sum(stat.stddev) / len(stat.stddev)
            
            # Sharpness using Laplacian variance
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Noise estimation using median filter difference
            median_filtered = cv2.medianBlur(gray, 5)
            noise = np.mean(np.abs(gray.astype(np.float64) - median_filtered.astype(np.float64)))
            
            # Color distribution
            hist_r = cv2.calcHist([img_array], [0], None, [256], [0, 256])
            hist_g = cv2.calcHist([img_array], [1], None, [256], [0, 256])
            hist_b = cv2.calcHist([img_array], [2], None, [256], [0, 256])
            
            # Color variety (number of unique colors approximation)
            color_variety = len(np.unique(img_array.reshape(-1, img_array.shape[2]), axis=0))
            
            result.quality_metrics = {
                'brightness': round(brightness, 2),
                'contrast': round(contrast, 2),
                'sharpness': round(sharpness, 2),
                'noise_level': round(noise, 2),
                'color_variety': color_variety,
                'quality_score': self._calculate_quality_score(brightness, contrast, sharpness, noise)
            }
            
        except Exception as e:
            result.warnings.append(f"Quality analysis error: {str(e)}")

    async def _analyze_image_content(self, img: Image.Image, result: MediaAnalysisResult):
        """Analyze image content (faces, objects, etc.)"""
        content_analysis = {
            'faces_detected': 0,
            'objects_detected': [],
            'dominant_colors': [],
            'scene_type': 'unknown'
        }
        
        try:
            img_array = np.array(img)
            
            # Face detection
            if self.face_recognition_enabled:
                try:
                    # Convert RGB to BGR for face_recognition
                    rgb_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB) if img_array.shape[2] == 3 else img_array
                    face_locations = face_recognition.face_locations(rgb_array)
                    content_analysis['faces_detected'] = len(face_locations)
                    
                    if face_locations:
                        content_analysis['face_locations'] = [
                            {'top': loc[0], 'right': loc[1], 'bottom': loc[2], 'left': loc[3]}
                            for loc in face_locations
                        ]
                except Exception as e:
                    result.warnings.append(f"Face detection error: {str(e)}")
            
            # Object detection
            if self.yolo_model and OBJECT_DETECTION_AVAILABLE:
                try:
                    # Run YOLO detection
                    results = self.yolo_model(img_array)
                    
                    objects = []
                    for r in results:
                        boxes = r.boxes
                        if boxes is not None:
                            for box in boxes:
                                confidence = box.conf.item()
                                if confidence > 0.5:  # Only include high-confidence detections
                                    class_id = int(box.cls.item())
                                    class_name = self.yolo_model.names[class_id]
                                    objects.append({
                                        'class': class_name,
                                        'confidence': round(confidence, 3),
                                        'bbox': box.xyxy.tolist()[0]
                                    })
                    
                    content_analysis['objects_detected'] = objects
                    
                except Exception as e:
                    result.warnings.append(f"Object detection error: {str(e)}")
            
            # Dominant colors analysis
            try:
                # Resize image for faster processing
                small_img = img.resize((100, 100))
                small_array = np.array(small_img)
                
                # Reshape and find dominant colors using k-means
                from sklearn.cluster import KMeans
                pixels = small_array.reshape(-1, 3)
                kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
                kmeans.fit(pixels)
                
                dominant_colors = []
                for center in kmeans.cluster_centers_:
                    color = [int(c) for c in center]
                    dominant_colors.append({
                        'rgb': color,
                        'hex': f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
                    })
                
                content_analysis['dominant_colors'] = dominant_colors
                
            except ImportError:
                result.warnings.append("sklearn not available for color analysis")
            except Exception as e:
                result.warnings.append(f"Color analysis error: {str(e)}")
            
            result.content_analysis = content_analysis
            
        except Exception as e:
            result.warnings.append(f"Content analysis error: {str(e)}")

    async def _analyze_video(self, file_path: Path, result: MediaAnalysisResult):
        """Comprehensive video analysis"""
        try:
            # Use ffmpeg-python for video analysis
            probe = ffmpeg.probe(str(file_path))
            
            # Get video stream info
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
            
            if not video_stream:
                result.errors.append("No video stream found")
                return
            
            # Basic technical specs
            duration = float(probe['format']['duration'])
            
            result.technical_specs = {
                'duration_seconds': round(duration, 2),
                'width': int(video_stream['width']),
                'height': int(video_stream['height']),
                'fps': eval(video_stream['r_frame_rate']),  # Convert fraction to float
                'codec': video_stream['codec_name'],
                'bitrate': int(probe['format'].get('bit_rate', 0)),
                'aspect_ratio': round(int(video_stream['width']) / int(video_stream['height']), 3),
                'total_frames': int(duration * eval(video_stream['r_frame_rate'])),
                'has_audio': audio_stream is not None
            }
            
            if audio_stream:
                result.technical_specs['audio_codec'] = audio_stream['codec_name']
                result.technical_specs['sample_rate'] = int(audio_stream.get('sample_rate', 0))
            
            # Video quality analysis (sample frames)
            await self._analyze_video_quality(file_path, result)
            
            # Content analysis (keyframes)
            await self._analyze_video_content(file_path, result)
            
        except Exception as e:
            result.errors.append(f"Video analysis error: {str(e)}")

    async def _analyze_video_quality(self, file_path: Path, result: MediaAnalysisResult):
        """Analyze video quality by sampling frames"""
        try:
            # Open video with OpenCV
            cap = cv2.VideoCapture(str(file_path))
            
            if not cap.isOpened():
                result.warnings.append("Could not open video for quality analysis")
                return
            
            # Sample frames at different time points
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_frames = min(10, total_frames)  # Sample up to 10 frames
            
            quality_metrics = {
                'avg_brightness': 0,
                'avg_contrast': 0,
                'avg_sharpness': 0,
                'frame_consistency': 0,
                'motion_intensity': 0
            }
            
            prev_frame = None
            brightness_values = []
            sharpness_values = []
            motion_values = []
            
            for i in range(sample_frames):
                frame_pos = (i / sample_frames) * total_frames
                cap.set(cv2.CAP_PROP_POS_FRAMES, int(frame_pos))
                
                ret, frame = cap.read()
                if not ret:
                    continue
                
                # Convert to grayscale for analysis
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Brightness
                brightness = np.mean(gray)
                brightness_values.append(brightness)
                
                # Sharpness (Laplacian variance)
                sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
                sharpness_values.append(sharpness)
                
                # Motion intensity (frame difference)
                if prev_frame is not None:
                    motion = np.mean(np.abs(gray.astype(np.float32) - prev_frame.astype(np.float32)))
                    motion_values.append(motion)
                
                prev_frame = gray
            
            cap.release()
            
            # Calculate averages
            if brightness_values:
                quality_metrics['avg_brightness'] = round(np.mean(brightness_values), 2)
                quality_metrics['brightness_consistency'] = round(np.std(brightness_values), 2)
            
            if sharpness_values:
                quality_metrics['avg_sharpness'] = round(np.mean(sharpness_values), 2)
                quality_metrics['sharpness_consistency'] = round(np.std(sharpness_values), 2)
            
            if motion_values:
                quality_metrics['avg_motion_intensity'] = round(np.mean(motion_values), 2)
            
            # Overall quality score
            quality_metrics['quality_score'] = self._calculate_video_quality_score(quality_metrics)
            
            result.quality_metrics = quality_metrics
            
        except Exception as e:
            result.warnings.append(f"Video quality analysis error: {str(e)}")

    async def _analyze_video_content(self, file_path: Path, result: MediaAnalysisResult):
        """Analyze video content using keyframes"""
        content_analysis = {
            'scene_changes': 0,
            'avg_faces_per_frame': 0,
            'dominant_colors_timeline': [],
            'content_type': 'unknown'
        }
        
        try:
            # Sample keyframes for content analysis
            cap = cv2.VideoCapture(str(file_path))
            
            if not cap.isOpened():
                result.warnings.append("Could not open video for content analysis")
                return
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            keyframes = min(5, total_frames)  # Analyze up to 5 keyframes
            
            face_counts = []
            prev_hist = None
            scene_changes = 0
            
            for i in range(keyframes):
                frame_pos = (i / keyframes) * total_frames
                cap.set(cv2.CAP_PROP_POS_FRAMES, int(frame_pos))
                
                ret, frame = cap.read()
                if not ret:
                    continue
                
                # Face detection on keyframes
                if self.face_recognition_enabled:
                    try:
                        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        face_locations = face_recognition.face_locations(rgb_frame)
                        face_counts.append(len(face_locations))
                    except Exception:
                        pass
                
                # Scene change detection using histogram comparison
                if prev_hist is not None:
                    current_hist = cv2.calcHist([frame], [0, 1, 2], None, [50, 50, 50], [0, 256, 0, 256, 0, 256])
                    similarity = cv2.compareHist(prev_hist, current_hist, cv2.HISTCMP_CORREL)
                    
                    if similarity < 0.7:  # Threshold for scene change
                        scene_changes += 1
                
                prev_hist = cv2.calcHist([frame], [0, 1, 2], None, [50, 50, 50], [0, 256, 0, 256, 0, 256])
            
            cap.release()
            
            # Calculate metrics
            if face_counts:
                content_analysis['avg_faces_per_frame'] = round(np.mean(face_counts), 2)
            
            content_analysis['scene_changes'] = scene_changes
            
            # Determine content type based on analysis
            if content_analysis['avg_faces_per_frame'] > 0.5:
                content_analysis['content_type'] = 'people-focused'
            elif scene_changes > keyframes * 0.5:
                content_analysis['content_type'] = 'dynamic'
            else:
                content_analysis['content_type'] = 'static'
            
            result.content_analysis = content_analysis
            
        except Exception as e:
            result.warnings.append(f"Video content analysis error: {str(e)}")

    def _calculate_quality_score(self, brightness: float, contrast: float, sharpness: float, noise: float) -> float:
        """Calculate overall image quality score (0-100)"""
        try:
            # Normalize metrics to 0-1 range
            brightness_score = 1 - abs(brightness - 127.5) / 127.5  # Optimal brightness around 127.5
            contrast_score = min(contrast / 50, 1)  # Higher contrast is generally better
            sharpness_score = min(sharpness / 100, 1)  # Higher sharpness is better
            noise_score = max(0, 1 - noise / 20)  # Lower noise is better
            
            # Weighted average
            quality_score = (brightness_score * 0.2 + contrast_score * 0.3 + sharpness_score * 0.4 + noise_score * 0.1) * 100
            
            return round(max(0, min(100, quality_score)), 1)
            
        except Exception:
            return 50.0  # Default middle score

    def _calculate_video_quality_score(self, metrics: dict) -> float:
        """Calculate overall video quality score"""
        try:
            brightness = metrics.get('avg_brightness', 127.5)
            sharpness = metrics.get('avg_sharpness', 50)
            consistency = 100 - metrics.get('brightness_consistency', 50)  # Lower variation is better
            
            brightness_score = 1 - abs(brightness - 127.5) / 127.5
            sharpness_score = min(sharpness / 100, 1)
            consistency_score = min(consistency / 100, 1)
            
            quality_score = (brightness_score * 0.3 + sharpness_score * 0.4 + consistency_score * 0.3) * 100
            
            return round(max(0, min(100, quality_score)), 1)
            
        except Exception:
            return 50.0

    def _generate_processing_recommendations(self, result: MediaAnalysisResult):
        """Generate processing recommendations based on analysis"""
        recommendations = {
            'suggested_effects': [],
            'quality_improvements': [],
            'optimization_tips': [],
            'transition_suitability': 'medium'
        }
        
        try:
            # Image recommendations
            if result.technical_specs.get('width'):
                width = result.technical_specs['width']
                height = result.technical_specs['height']
                aspect_ratio = result.technical_specs.get('aspect_ratio', 1)
                
                # Resolution recommendations
                if width < 1920:
                    recommendations['quality_improvements'].append('Consider upscaling for better quality')
                
                if aspect_ratio < 0.9 or aspect_ratio > 1.1:
                    recommendations['optimization_tips'].append('May need cropping for square formats')
                
                # Quality-based recommendations
                quality_score = result.quality_metrics.get('quality_score', 50)
                
                if quality_score < 30:
                    recommendations['quality_improvements'].extend([
                        'Image quality is low - consider enhancement filters',
                        'May benefit from noise reduction'
                    ])
                elif quality_score > 80:
                    recommendations['suggested_effects'].append('High quality - suitable for Ken Burns effect')
                
                brightness = result.quality_metrics.get('brightness', 127.5)
                if brightness < 100:
                    recommendations['quality_improvements'].append('Image appears dark - consider brightness adjustment')
                elif brightness > 180:
                    recommendations['quality_improvements'].append('Image appears bright - consider exposure adjustment')
                
                sharpness = result.quality_metrics.get('sharpness', 50)
                if sharpness < 30:
                    recommendations['quality_improvements'].append('Image appears soft - consider sharpening')
                
                # Content-based recommendations
                faces = result.content_analysis.get('faces_detected', 0)
                if faces > 0:
                    recommendations['suggested_effects'].extend([
                        'Contains faces - suitable for portrait mode effects',
                        'Consider face-focused cropping'
                    ])
                
                objects = result.content_analysis.get('objects_detected', [])
                if len(objects) > 3:
                    recommendations['suggested_effects'].append('Rich content - suitable for zoom effects')
            
            # Video recommendations
            duration = result.technical_specs.get('duration_seconds')
            if duration:
                if duration < 2:
                    recommendations['optimization_tips'].append('Very short video - consider extending duration')
                elif duration > 30:
                    recommendations['optimization_tips'].append('Long video - consider creating highlights')
                
                fps = result.technical_specs.get('fps', 24)
                if fps < 24:
                    recommendations['quality_improvements'].append('Low frame rate - may appear jerky')
                elif fps > 60:
                    recommendations['optimization_tips'].append('High frame rate - consider frame rate conversion for web')
                
                motion = result.quality_metrics.get('avg_motion_intensity', 0)
                if motion > 50:
                    recommendations['transition_suitability'] = 'high'
                    recommendations['suggested_effects'].append('High motion - good for dynamic transitions')
                elif motion < 10:
                    recommendations['transition_suitability'] = 'low'
                    recommendations['suggested_effects'].append('Static content - suitable for slow transitions')
            
            result.processing_recommendations = recommendations
            
        except Exception as e:
            logger.warning(f"Error generating recommendations: {e}")


# Utility functions for external use
def create_media_hash(file_path: Union[str, Path]) -> str:
    """Create a unique hash for media file"""
    try:
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5()
            chunk = f.read(8192)
            while chunk:
                file_hash.update(chunk)
                chunk = f.read(8192)
        return file_hash.hexdigest()
    except Exception as e:
        logger.error(f"Error creating hash for {file_path}: {e}")
        return ""


def get_media_thumbnail(file_path: Union[str, Path], size: Tuple[int, int] = (150, 150)) -> Optional[bytes]:
    """Generate thumbnail for media file"""
    try:
        file_path = Path(file_path)
        
        if file_path.suffix.lower() in {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}:
            # Image thumbnail
            with Image.open(file_path) as img:
                img.thumbnail(size, Image.Resampling.LANCZOS)
                buffer = BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                return buffer.getvalue()
                
        elif file_path.suffix.lower() in {'.mp4', '.avi', '.mov', '.mkv'}:
            # Video thumbnail (first frame)
            cap = cv2.VideoCapture(str(file_path))
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                # Convert to PIL Image
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                buffer = BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                return buffer.getvalue()
        
        return None
        
    except Exception as e:
        logger.error(f"Error generating thumbnail for {file_path}: {e}")
        return None


# Example usage and testing
if __name__ == "__main__":
    async def test_processor():
        """Test the image/video processor"""
        processor = ImageVideoProcessor()
        
        # Example media items for testing
        test_items = [
            {
                'id': 'test_image_1',
                'data': 'path/to/test/image.jpg',  # Replace with actual path
                'type': 'image'
            }
        ]
        
        # Run batch analysis
        results = await processor.analyze_media_batch(test_items)
        
        # Print results
        for media_id, result in results.items():
            print(f"\n--- Analysis for {media_id} ---")
            print(f"Technical specs: {result.technical_specs}")
            print(f"Quality metrics: {result.quality_metrics}")
            print(f"Content analysis: {result.content_analysis}")
            print(f"Recommendations: {result.processing_recommendations}")
            if result.errors:
                print(f"Errors: {result.errors}")
            if result.warnings:
                print(f"Warnings: {result.warnings}")
    
    # Run test
    # asyncio.run(test_processor())