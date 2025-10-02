import os, random, requests
from fx_transitions import TransitionFactory
from moviepy import concatenate_videoclips
from pathlib import Path

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
    transition_idx = 0

    for i in range(len(sources)-1):
        transition_cls = transitions[transition_idx % len(transitions)]
        transition = transition_cls([sources[i], sources[i+1]], duration=2, size=size)
        clips.append(transition.build())
        transition_idx += 1

    final = concatenate_videoclips(clips, method="compose")

    # Trim / extend to exactly 1 min
    if final.duration > total_duration:
        final = final.subclip(0, total_duration)
    else:
        final = final.loop(duration=total_duration)

    final.write_videofile(out_path, fps=24)

# ---------------------------------------------------
# 🔹 Run demo
# ---------------------------------------------------
if __name__ == "__main__":
    print("Downloading assets...")
    sources = prepare_assets()
    print("Building demo video...")
    build_demo_video(sources, out_path="demo.mp4")
    print("✅ Demo saved as demo.mp4")
