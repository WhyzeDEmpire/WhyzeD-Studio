import os
import json
import subprocess

class FFmpegVideoEngine:
    def __init__(self, workspace_dir: str = "/sdcard/WhyzeD Studio/workspace"):
        self.workspace = workspace_dir
        self.output_dir = "/sdcard/Movies/WhyzeDStudio"
        os.makedirs(self.workspace, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    def process_scene_clip(self, input_video: str, duration_sec: float, output_video: str) -> str:
        filter_chain = (
            "scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920,"
            "fps=30"
        )
        
        cmd = [
            "ffmpeg", "-y",
            "-i", input_video,
            "-t", str(duration_sec),
            "-vf", filter_chain,
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-an",
            output_video
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_video

    def generate_ass_subtitles(self, manifest_scenes: list, ass_filename: str) -> str:
        ass_path = os.path.join(self.workspace, ass_filename)
        
        header = """[Script Info]
Title: WhyzeD Studio Dynamic Subtitles
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,DejaVu Sans,54,&H0000FFFF,&H00000000,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,4,2,2,100,100,450,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        current_time = 0.0
        events = []
        
        for scene in manifest_scenes:
            duration = scene.get("actual_duration_sec", 5.0)
            text = scene.get("narration_text", "")
            
            start_str = self._format_timestamp(current_time)
            end_str = self._format_timestamp(current_time + duration)
            
            events.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{text}")
            current_time += duration
            
        with open(ass_path, "w", encoding="utf-8") as f:
            f.write(header + "\n".join(events))
            
        return ass_path

    def _format_timestamp(self, seconds: float) -> str:
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        cs = int(round((seconds - int(seconds)) * 100))
        return f"{hrs}:{mins:02d}:{secs:02d}.{cs:02d}"

    def build_final_master_render(self, manifest_file: str, final_output_name: str = "WhyzeD_Studio_Master.mp4") -> str:
        with open(manifest_file, "r") as f:
            manifest_data = json.load(f)
            
        # Extract scenes array safely whether manifest_data is a dict or a direct list
        if isinstance(manifest_data, dict):
            scenes = manifest_data.get("scenes", [])
        else:
            scenes = manifest_data

        processed_video_files = []
        audio_files = []
        
        for i, scene in enumerate(scenes):
            raw_vid = scene.get("video_file", os.path.join(self.workspace, f"scene_{i+1}_raw.mp4"))
            proc_vid = os.path.join(self.workspace, f"scene_{i+1}_proc.mp4")
            duration = scene.get("actual_duration_sec", 5.0)
            
            self.process_scene_clip(raw_vid, duration, proc_vid)
            processed_video_files.append(proc_vid)
            audio_files.append(scene.get("audio_file", os.path.join(self.workspace, f"scene_{i+1}_voice.wav")))

        concat_list_path = os.path.join(self.workspace, "concat_list.txt")
        with open(concat_list_path, "w") as f:
            for vfile in processed_video_files:
                f.write(f"file '{vfile}'\n")

        merged_audio = os.path.join(self.workspace, "merged_voice.wav")
        audio_concat_cmd = ["ffmpeg", "-y"]
        for afile in audio_files:
            audio_concat_cmd.extend(["-i", afile])
        audio_concat_cmd.extend([
            "-filter_complex", f"concat=n={len(audio_files)}:v=0:a=1[a]",
            "-map", "[a]",
            merged_audio
        ])
        subprocess.run(audio_concat_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        ass_sub_path = self.generate_ass_subtitles(scenes, "captions.ass")
        output_path = os.path.join(self.output_dir, final_output_name)
        escaped_ass = ass_sub_path.replace(":", "\\:").replace(" ", "\\ ")
        
        filter_complex = (
            f"[0:v]subtitles='{escaped_ass}',"
            "drawtext=text='WHYZED STUDIO':fontcolor=white@0.7:fontsize=38:"
            "x=40:y=h-th-90:shadowcolor=black@0.5:shadowx=2:shadowy=2[v_out]"
        )

        final_cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", concat_list_path,
            "-i", merged_audio,
            "-filter_complex", filter_complex,
            "-map", "[v_out]",
            "-map", "1:a",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            output_path
        ]

        print(f"[FFmpeg Engine] Rendering Final Master Video: {output_path}")
        subprocess.run(final_cmd, check=True)
        print("="*60)
        print(f"SUCCESS! Render saved to gallery path: {output_path}")
        print("="*60)
        return output_path

if __name__ == "__main__":
    engine = FFmpegVideoEngine()
    engine.build_final_master_render("workspace/active_pipeline_manifest.json")
