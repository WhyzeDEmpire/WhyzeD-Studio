import os
import subprocess

def generate_voice_over(text: str, output_wav_path: str) -> str:
    os.makedirs(os.path.dirname(output_wav_path), exist_ok=True)
    clean_text = text.strip()
    if not clean_text:
        clean_text = "WhyzeD Studio on device video generation."
        
    print(f"[Voice Engine] Synthesizing: '{clean_text[:50]}...'")
    
    raw_tmp = output_wav_path + ".raw.wav"
    cmd_espeak = ["espeak-ng", "-v", "en-us", "-s", "140", "-w", raw_tmp, clean_text]
    
    try:
        subprocess.run(cmd_espeak, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Resample to standard 44100Hz mono PCM audio
        cmd_resample = [
            "ffmpeg", "-y",
            "-i", raw_tmp,
            "-ar", "44100",
            "-ac", "1",
            "-c:a", "pcm_s16le",
            output_wav_path
        ]
        subprocess.run(cmd_resample, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(raw_tmp):
            os.remove(raw_tmp)
        print(f"[Voice Engine] Voice WAV generated successfully: {output_wav_path}")
    except Exception as e:
        print(f"[Voice Engine] Warning: Voice synthesis failed ({e}). Creating fallback audio.")
        cmd_fallback = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", "anullsrc=r=44100:cl=mono",
            "-t", "5",
            output_wav_path
        ]
        subprocess.run(cmd_fallback, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
    return output_wav_path

if __name__ == "__main__":
    generate_voice_over("Testing WhyzeD Studio voice engine.", "/sdcard/WhyzeD Studio/workspace/test_voice.wav")
