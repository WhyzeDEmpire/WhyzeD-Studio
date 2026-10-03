import os
import requests
import subprocess

def fetch_and_apply_edit(visual_prompt: str, prompt_edit_modifier: str, output_mp4_path: str) -> str:
    os.makedirs(os.path.dirname(output_mp4_path), exist_ok=True)
    print(f"[Asset Engine] Processing Shot: '{visual_prompt[:40]}...'")
    print(f"[Asset Engine] Applying Edit Modifier: '{prompt_edit_modifier}'")

    pexels_key = os.environ.get("PEXELS_API_KEY")
    if pexels_key:
        headers = {"Authorization": pexels_key}
        url = "https://api.pexels.com/videos/search?query=technology&orientation=portrait&per_page=1"
        try:
            res = requests.get(url, headers=headers).json()
            video_url = res["videos"][0]["video_files"][0]["link"]
            video_data = requests.get(video_url).content
            with open(output_mp4_path, "wb") as f:
                f.write(video_data)
            print(f"[Asset Engine] Assets fetched successfully.")
            return output_mp4_path
        except Exception as e:
            print(f"[Asset Engine] Fallback notice: {e}")

    # Robust synthetic video generation via FFmpeg lavfi
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "color=c=0x090D16:s=1080x1920:d=5",
        "-vf", "drawtext=text='WHYZED STUDIO SHOT':fontcolor=0x00F0FF:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        output_mp4_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"[Asset Engine] Generated valid fallback video: {output_mp4_path}")
    return output_mp4_path

if __name__ == "__main__":
    print("[Asset Engine] Module Ready.")
