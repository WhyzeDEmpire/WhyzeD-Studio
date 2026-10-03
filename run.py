import os
import sys
import subprocess

def run_step(command, label):
    print(f"\n--- {label} ---")
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Stream real-time terminal output
    for line in process.stdout:
        print(line, end="", flush=True)
        
    process.wait()
    if process.returncode != 0:
        print(f"\n[Error] {label} failed with exit code {process.returncode}")
        sys.exit(1)

def main():
    print("==================================================")
    print("         WHYZED STUDIO - ON-DEVICE ENGINE          ")
    print("==================================================")
    
    topic = input("Enter video topic/prompt (or press Enter for default): ").strip()
    if not topic:
        topic = "Ijaw River Flowing"
        
    print(f"\n[Run] Initiating creation process for topic: '{topic}'")
    os.environ["STUDIO_ACTIVE_TOPIC"] = topic
    
    run_step("python -u pipeline_orchestrator.py", "STEP 1: Pipeline Orchestrator")
    run_step("python -u ffmpeg_engine.py", "STEP 2: FFmpeg Rendering Engine")
        
    print("\n==================================================")
    print("SUCCESS: Master video rendered successfully!")
    print("Path: /sdcard/Movies/WhyzeDStudio/WhyzeD_Studio_Master.mp4")
    print("==================================================")

if __name__ == "__main__":
    main()
