import os
import json
from google import genai
from google.genai import types

def generate_scene_script(prompt: str, target_scenes: int = 2) -> list[dict]:
    """
    Parses user prompt into an EpNova-style multi-shot drama script.
    Maintains character visual anchors and scene context across shots.
    """
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    system_instruction = f"""
    You are the EpNova Drama & Script Engine for WhyzeD Studio.
    Convert user prompts into a structured multi-shot drama script breakdown with exactly {target_scenes} scenes.
    
    Ensure visual continuity, multi-shot pacing, and specific prompt modifiers for post-editing.
    Output MUST be valid raw JSON array matching this format:
    [
      {{
        "scene_id": 1,
        "visual_prompt": "Shot 1: Close-up description...",
        "prompt_edit_modifier": "Post-processing overlay instructions...",
        "narration_text": "Spoken dialogue or narration line.",
        "estimated_seconds": 5.0
      }}
    ]
    Do NOT wrap in markdown fences. Return ONLY raw JSON.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,
        )
    )

    clean_json = response.text.strip().removeprefix("```json").removesuffix("```").strip()
    return json.loads(clean_json)

if __name__ == "__main__":
    print("[Script Engine] Module Ready.")
