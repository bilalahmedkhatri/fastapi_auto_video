import os, random, requests, gc, sys
import warnings
from fx_transitions import TransitionFactory
from moviepy import concatenate_videoclips
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════════
# 🛠️ Windows Cleanup Configuration
# ═══════════════════════════════════════════════════════════════════════════════
# This section handles the infamous "OSError: [WinError 6] The handle is invalid"
# error that occurs on Windows when using MoviePy with Python 3.12.
#
# The issue: Windows closes subprocess handles before Python's garbage collector
# runs MoviePy's __del__ methods, causing invalid handle errors during cleanup.
#
# Solutions implemented:
# 1. Suppress warnings at environment level
# 2. Explicit cleanup in try-finally blocks
# 3. Multiple rounds of garbage collection
# 4. Small delay before exit for handle release
# 5. Disable subprocess cleanup on Windows
#
# References:
# - https://github.com/Zulko/moviepy/issues/1925
# - https://stackoverflow.com/questions/tagged/moviepy+windows
# ═══════════════════════════════════════════════════════════════════════════════

if sys.platform == 'win32':
    # Suppress MoviePy Windows cleanup warnings
    warnings.filterwarnings('ignore', category=UserWarning, module='moviepy')
    warnings.filterwarnings('ignore', category=ResourceWarning)
    os.environ['PYTHONWARNINGS'] = 'ignore'
    # Set subprocess to not inherit handles (Windows-specific fix)
    import subprocess
    if hasattr(subprocess, '_mswindows'):
        subprocess._cleanup = lambda: None

# ---------------------------------------------------
# 🔹 Step 1: Download random images & videos
# ---------------------------------------------------

ASSET_DIR = Path("assets")
ASSET_DIR.mkdir(exist_ok=True)

VIDEO_CANDIDATES = [
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
    "https://download.samplelib.com/mp4/sample-5s.mp4",
    "https://filesamples.com/samples/video/mp4/sample_640x360.mp4",
    "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4",
]

IMAGE_TEMPLATE = "https://picsum.photos/720/720?random={}"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def download_file(url, out_path, timeout=20):
    out_path = Path(out_path)
    if out_path.exists() and out_path.stat().st_size > 1000:
        return str(out_path)
    print(f"Downloading: {url} -> {out_path}")
    try:
        with requests.get(url, stream=True, headers=HEADERS, timeout=timeout) as r:
            r.raise_for_status()
            with open(out_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024*8):
                    if chunk:
                        f.write(chunk)
        return str(out_path)
    except Exception as e:
        if out_path.exists():
            try:
                out_path.unlink()
            except:
                pass
        raise

def prepare_assets(asset_dir="assets", n_images=3, n_videos=2):
    asset_dir = Path(asset_dir)
    asset_dir.mkdir(parents=True, exist_ok=True)

    sources = []
    # images
    for i in range(n_images):
        url = IMAGE_TEMPLATE.format(random.randint(1, 999999))
        out = asset_dir / f"img_{i}.jpg"
        try:
            download_file(url, out)
            sources.append(str(out))
        except Exception as e:
            print(f"Failed to download image {url}: {e}")

    # videos (try each candidate until one downloads)
    for i in range(n_videos):
        downloaded = False
        for url in VIDEO_CANDIDATES:
            out = asset_dir / f"video_{i}.mp4"
            try:
                download_file(url, out)
                # quick sanity: file > 1 KB
                if out.exists() and out.stat().st_size > 1000:
                    sources.append(str(out))
                    downloaded = True
                    break
            except Exception as e:
                print(f"Try failed for {url}: {e}")
        if not downloaded:
            raise RuntimeError(
                "Could not download any test video. "
                "Check your internet / firewall, or place test MP4 files into the assets/ folder manually."
            )

    random.shuffle(sources)
    return sources

# ---------------------------------------------------
# 🔹 Step 2: Apply all transitions in a loop
# ---------------------------------------------------
def build_demo_video(sources, out_path="demo.mp4", size=(720,720), total_duration=60):
    transitions = [
        TransitionFactory.fade,
        TransitionFactory.slide,
        TransitionFactory.zoom,
        TransitionFactory.spin,
        TransitionFactory.flash,
        TransitionFactory.circle,
        TransitionFactory.pixelate,
        TransitionFactory.glitch,
        TransitionFactory.split,
    ]

    clips = []
    transition_objects = []  # Keep track of transition objects
    transition_idx = 0

    try:
        for i in range(len(sources)-1):
            transition_cls = transitions[transition_idx % len(transitions)]
            transition = transition_cls(sources=[sources[i], sources[i+1]], duration=2, size=size)
            transition_objects.append(transition)
            clips.append(transition.build())
            transition_idx += 1

        # Loop clips to reach desired total duration
        current_duration = sum(clip.duration for clip in clips)
        if current_duration < total_duration:
            # Repeat clips until we have enough duration
            extended_clips = clips.copy()
            while sum(clip.duration for clip in extended_clips) < total_duration:
                extended_clips.extend(clips)
            clips = extended_clips
        
        final = concatenate_videoclips(clips, method="compose")

        # Trim to exactly the desired duration
        if final.duration > total_duration:
            final = final.subclipped(0, total_duration)

        final.write_videofile(out_path, fps=15)
        
    finally:
        # Comprehensive cleanup to avoid Windows handle errors
        # This is crucial for Windows + Python 3.12 + MoviePy combination
        
        # Step 1: Close the final concatenated clip first
        try:
            if 'final' in locals():
                final.close()
                del final
        except Exception:
            pass
        
        # Step 2: Close all individual clips
        for clip in clips:
            try:
                if hasattr(clip, 'close'):
                    clip.close()
            except Exception:
                pass
        
        # Step 3: Close transition objects' internal clips (source clips)
        for trans_obj in transition_objects:
            try:
                if hasattr(trans_obj, 'clips'):
                    for clip in trans_obj.clips:
                        if hasattr(clip, 'close'):
                            clip.close()
                # Also close the transition object itself if it has a close method
                if hasattr(trans_obj, 'close'):
                    trans_obj.close()
            except Exception:
                pass
        
        # Step 4: Clear references and force garbage collection
        clips.clear()
        transition_objects.clear()
        
        # Step 5: Multiple rounds of garbage collection to ensure cleanup
        for _ in range(3):
            gc.collect()


# ---------------------------------------------------
# 🔹 Run demo
# ---------------------------------------------------
if __name__ == "__main__":
    try:
        print("Downloading assets...")
        sources = prepare_assets()
        print("Building demo video...")
        build_demo_video(sources, out_path="demo2.mp4")
        print("✅ Demo saved as demo1.mp4")
    finally:
        # Final cleanup before exit to prevent Windows handle errors
        # Multiple rounds of garbage collection
        for _ in range(3):
            gc.collect()
        
        # Small delay to allow Windows to fully release file handles
        import time
        time.sleep(0.5)
        
        # One more final garbage collection
        gc.collect()
