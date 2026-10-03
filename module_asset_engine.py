import os
import requests
import subprocess

def fetch_media_asset(prompt: str, output_path: str) -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    api_key = os.environ.get("PIXABAY_API_KEY")
    
    if api_key:
        print(f"[Asset Engine] Searching Pixabay for: '{prompt[:40]}...'")
        url = "https://pixabay.com/api/videos/"
        params = {
            "key": api_key,
            "q": prompt,
            "per_page": 3,
            "video_type": "film"
        }
        try:
            res = requests.get(url, params=params, timeout=10)
            if res.status_code == 200:
                data = res.json()
                if data.get("hits"):
                    video_url = data["hits"][0]["videos"]["small"]["url"]
                    print(f"[Asset Engine] Downloading stock video from Pixabay...")
                    v_res = requests.get(video_url, timeout=15)
                    with open(output_path, "wb") as f:
                        f.write(v_res.content)
                    return output_path
        except Exception as e:
            print(f"[Asset Engine] Pixabay fetch failed ({e}). Falling back to synthetic layout.")

    # Fallback synthetic media generator using FFmpeg
    print(f"[Asset Engine] Generating synthetic scene background: {output_path}")
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "color=c=0x0B0F19:s=1080x1920:r=30",
        "-t", "5",
        "-pix_fmt", "yuv420p",
        "-c:v", "libx264",
        output_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path

if __name__ == "__main__":
    print("[Asset Engine] Module Ready.")
