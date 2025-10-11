import numpy as np
from moviepy import TextClip, ImageClip
import logging
from pathlib import Path

# Setup logging for text overlay module
LOGS_DIR = Path(__file__).resolve().parent.parent.parent / 'logs' / 'video_generation'
LOGS_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# File handler
log_file = LOGS_DIR / 'text_overlays.log'
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(file_formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# Add handlers if not already added
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def create_first5_words_highlighted_clips(
    transcript,
    size=(1080, 1920),
    font_size=100,
    base_color='white',
    highlight_color='#ffe066',
    highlight_text_color='black',
    border_color='#ffae00',
    border_width=4,
    box_padding=16,
    font='Arial',
    position=('center', 'top')
):
    """Show first 5 words as a phrase (wrapped), highlight each word with a styled background box in sync with voiceover, always on top of the phrase. Uses PIL for word positioning."""
    try:
        logger.info(f"📝 create_first5_words_highlighted_clips called")
        logger.info(f"   - transcript type: {type(transcript)}")
        logger.info(f"   - transcript length: {len(transcript) if transcript else 0}")
        logger.info(f"   - size: {size}, font_size: {font_size}, position: {position}")
        logger.info(f"   - colors: base={base_color}, highlight={highlight_color}, text={highlight_text_color}, border={border_color}")
        
        from PIL import Image as PILImage, ImageDraw, ImageFont
        clips = []
        for seg_idx, seg in enumerate(transcript):
            logger.info(f"   - Processing segment {seg_idx + 1}/{len(transcript)}")
            words = seg.get('words', [])[:5]
            if not words:
                logger.warning(f"     - Segment {seg_idx + 1} has no words, skipping")
                continue
            logger.info(f"     - Segment {seg_idx + 1} has {len(words)} words")
            phrase = ' '.join([w['text'] for w in words])
            seg_start = words[0]['start']
            seg_end = words[-1]['end']
            logger.info(f"     - Phrase: '{phrase}' ({seg_start:.2f}s - {seg_end:.2f}s)")
            # Prepare PIL font
            try:
                pil_font = ImageFont.truetype(font, font_size)
            except Exception:
                pil_font = ImageFont.load_default()
            # Wrap phrase using PIL
            max_width = size[0] - 40  # margin
            lines = []
            line = ''
            for word in phrase.split():
                test_line = (line + ' ' + word).strip()
                bbox = pil_font.getbbox(test_line)
                w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
                if w > max_width and line:
                    lines.append(line)
                    line = word
                else:
                    line = test_line
            if line:
                lines.append(line)
            # Render phrase to get line heights and widths
            line_heights = []
            line_widths = []
            for l in lines:
                bbox = pil_font.getbbox(l)
                line_widths.append(bbox[2] - bbox[0])
                line_heights.append(bbox[3] - bbox[1])
            phrase_h = sum(line_heights)
            video_w, video_h = size
            y_center = 50 if position[1] == 'top' else (
                video_h - phrase_h) // 2
            # Create base phrase TextClip (wrapped, centered)
            try:
                logger.info(f"     - Creating base phrase clip with {len(lines)} lines")
                base_phrase_clip = TextClip(
                    text='\n'.join(lines),
                    font_size=font_size,
                    color=base_color,
                    font=font,
                    size=(video_w, phrase_h),
                    method='caption',
                ).with_start(seg_start).with_duration(seg_end-seg_start).with_position((0, y_center))
                clips.append(base_phrase_clip)
                logger.info(f"     - Base phrase clip created successfully")
            except Exception as e:
                logger.error(f"❌ Error creating base phrase clip: {e}")
                print(f"Error creating base phrase clip: {e}")
                continue
            # Calculate word positions in wrapped lines (center each line)
            word_idx = 0
            y_offset = 0
            for line_idx, line in enumerate(lines):
                words_in_line = line.split()
                # Center this line
                line_w = line_widths[line_idx]
                x_line = (video_w - line_w) // 2
                # For each word in this line
                x_offset = 0
                for w_in_line in words_in_line:
                    if word_idx >= len(words):
                        break
                    word_text = words[word_idx]['text']
                    start = words[word_idx]['start']
                    end = words[word_idx]['end']
                    duration = end - start
                    if not word_text or duration <= 0:
                        word_idx += 1
                        continue
                    # Measure word position within the line
                    pre_text = ' '.join(
                        words_in_line[:words_in_line.index(w_in_line)])
                    if pre_text:
                        bbox = pil_font.getbbox(pre_text)
                        x_offset = bbox[2] - bbox[0]
                    else:
                        x_offset = 0
                    bbox_word = pil_font.getbbox(word_text)
                    word_w, word_h = bbox_word[2] - \
                        bbox_word[0], bbox_word[3] - bbox_word[1]
                    word_x = x_line + x_offset
                    word_y = y_center + sum(line_heights[:line_idx])
                    # Create styled box as background
                    try:
                        box_w = int(word_w + 2 * box_padding)
                        box_h = int(word_h + 2 * box_padding)
                        box_img = PILImage.new(
                            'RGBA', (box_w, box_h), highlight_color)
                        draw = ImageDraw.Draw(box_img)
                        for i in range(border_width):
                            draw.rectangle(
                                [i, i, box_w - 1 - i, box_h - 1 - i],
                                outline=border_color
                            )
                        box_np = np.array(box_img)
                        box_clip = ImageClip(box_np).with_start(start).with_duration(
                            duration).with_position((word_x - box_padding, word_y - box_padding))
                        # Create word text (on top of box)
                        word_clip = TextClip(
                            text=word_text,
                            font_size=font_size,
                            color=highlight_text_color,
                            font=font,
                            method='label',
                        ).with_start(start).with_duration(duration).with_position((word_x, word_y))
                        clips.append(box_clip)
                        clips.append(word_clip)
                        logger.debug(f"       - Created highlight for word '{word_text}' at ({word_x}, {word_y})")
                    except Exception as e:
                        logger.error(f"❌ Error creating highlight for word '{word_text}': {e}")
                        print(
                            f"Error creating highlight for word '{word_text}': {e}")
                    word_idx += 1
        
        logger.info(f"✅ Text overlay function created {len(clips)} total clips")
        return clips
    except Exception as e:
        logger.error(f"❌ Error in create_first5_words_highlighted_clips: {e}")
        import traceback
        logger.error(traceback.format_exc())
        print(f"Error loading transcript: {e}")
        return []
