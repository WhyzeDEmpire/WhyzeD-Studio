import os
import json
from module_voice_engine import CustomVoiceEngine
from module_asset_engine import fetch_and_apply_edit

def execute_phase_2_pipeline(manifest_path: str = "config/pipeline_manifest.json"):
    print("="*60)
    print("      WHYZED STUDIO: EXECUTING PHASE 2 CORE PIPELINE      ")
    print("="*60)

    if not os.path.exists(manifest_path):
        raise FileNotFoundError(f"Manifest missing at {manifest_path}")

    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    voice_ref = manifest["voice_config"]["reference_wav"]
    scenes = manifest["scenes"]
    voice_engine = CustomVoiceEngine(voice_ref)

    for scene in scenes:
        scene_id = scene["scene_id"]
        duration = scene.get("estimated_seconds", 5.0)
        print(f"\n--- Processing Scene {scene_id} ({duration}s) ---")
        
        audio_out = f"workspace/scene_{scene_id}_voice.wav"
        voice_engine.synthesize_scene_voice(scene["narration_text"], audio_out, duration_sec=duration)
        scene["audio_file"] = audio_out

        video_out = f"workspace/scene_{scene_id}_raw.mp4"
        fetch_and_apply_edit(scene["visual_prompt"], scene["prompt_edit_modifier"], video_out)
        scene["video_file"] = video_out

    updated_manifest_path = "workspace/active_pipeline_manifest.json"
    with open(updated_manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print("\n" + "="*60)
    print(f"Phase 2 Complete. Active manifest ready at: {updated_manifest_path}")
    print("="*60)

if __name__ == "__main__":
    execute_phase_2_pipeline()
