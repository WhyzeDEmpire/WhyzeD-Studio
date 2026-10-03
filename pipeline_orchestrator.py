import os
import json
import subprocess
import module_script_engine
import module_voice_engine
import module_asset_engine

WORKSPACE = "/sdcard/WhyzeD Studio/workspace"
MANIFEST_PATH = os.path.join(WORKSPACE, "active_pipeline_manifest.json")

def get_audio_duration(file_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=True)
        return float(result.stdout.strip())
    except Exception:
        return 5.0

def run_pipeline():
    os.makedirs(WORKSPACE, exist_ok=True)
    topic = os.environ.get("STUDIO_ACTIVE_TOPIC", "Ijaw River Flowing")
    print(f"[Orchestrator] Active Topic: '{topic}'")
    
    script = module_script_engine.generate_script(topic)
    manifest = {"topic": topic, "scenes": []}
    
    scene_videos = []
    voice_files = []
    
    for i, scene in enumerate(script.get("scenes", []), start=1):
        narration = scene.get("narration", "")
        visual_desc = scene.get("visual_prompt", "")
        
        voice_path = os.path.join(WORKSPACE, f"scene_{i}_voice.wav")
        raw_video_path = os.path.join(WORKSPACE, f"scene_{i}_raw.mp4")
        proc_video_path = os.path.join(WORKSPACE, f"scene_{i}_proc.mp4")
        
        # 1. Generate Voice
        module_voice_engine.generate_voice_over(narration, voice_path)
        audio_dur = get_audio_duration(voice_path)
        if audio_dur < 1.0:
            audio_dur = 5.0
            
        # 2. Generate Asset matching Audio Duration
        module_asset_engine.fetch_media_asset(visual_desc, raw_video_path)
        
        # Format raw video scene duration to match audio length
        cmd_format = [
            "ffmpeg", "-y",
            "-stream_loop", "-1",
            "-i", raw_video_path,
            "-t", str(audio_dur),
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
            "-r", "30",
            "-pix_fmt", "yuv420p",
            "-c:v", "libx264",
            proc_video_path
        ]
        subprocess.run(cmd_format, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        scene_videos.append(proc_video_path)
        voice_files.append(voice_path)
        
        manifest["scenes"].append({
            "scene_id": i,
            "narration": narration,
            "duration": audio_dur,
            "video_path": proc_video_path,
            "voice_path": voice_path
        })

    # Save Concat File List
    concat_txt = os.path.join(WORKSPACE, "concat_list.txt")
    with open(concat_txt, "w") as f:
        for vp in scene_videos:
            f.write(f"file '{vp}'\n")
            
    # Concatenate Voice Files
    merged_voice = os.path.join(WORKSPACE, "merged_voice.wav")
    filter_complex = "".join([f"[{k}:a]" for k in range(len(voice_files))]) + f"concat=n={len(voice_files)}:v=0:a=1[aout]"
    cmd_audio_merge = ["ffmpeg", "-y"]
    for vf in voice_files:
        cmd_audio_merge.extend(["-i", vf])
    cmd_audio_merge.extend(["-filter_complex", filter_complex, "-map", "[aout]", merged_voice])
    subprocess.run(cmd_audio_merge, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)
        
    print(f"[Orchestrator] Pipeline Manifest generated: {MANIFEST_PATH}")

if __name__ == "__main__":
    run_pipeline()
