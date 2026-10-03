import os
import json
from google import genai
from google.genai import types

def generate_script(prompt: str) -> dict:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")

    client = genai.Client(api_key=api_key)

    system_instruction = (
        "You are WhyzeD Studio Engine. Generate a short-form vertical video script (9:16) "
        "structured as valid JSON matching this schema:\n"
        "{\n"
        '  "topic": "string",\n'
        '  "scenes": [\n'
        "    {\n"
        '      "scene_id": 1,\n'
        '      "narration": "string",\n'
        '      "visual_prompt": "string",\n'
        '      "duration_seconds": 5\n'
        "    }\n"
        "  ]\n"
        "}\n"
        "Do not include markdown backticks or extra commentary, return ONLY the raw JSON object."
    )

    primary_model = "gemini-3.8-flash"

    try:
        response = client.models.generate_content(
            model=primary_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7,
                response_mime_type="application/json"
            )
        )
        
        script_data = json.loads(response.text)
        print(f"[Script Engine] Script generated successfully for topic: '{prompt}'")
        return script_data

    except Exception as e:
        print(f"[Script Engine] Primary model ({primary_model}) failed: {e}")
        fallback_model = "gemini-3.5-flash-lite"
        try:
            print(f"[Script Engine] Retrying with fallback model '{fallback_model}'...")
            response = client.models.generate_content(
                model=fallback_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        except Exception as fallback_err:
            raise RuntimeError(f"Script generation failed on all attempts: {fallback_err}")

if __name__ == "__main__":
    test_script = generate_script("Ijaw River Flowing")
    print(json.dumps(test_script, indent=2))
