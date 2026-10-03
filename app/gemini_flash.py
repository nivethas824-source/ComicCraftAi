import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def generate_outline(story_prompt: str, character_name: str, setting: str, tone: str, art_style: str) -> list:
    """
    Generates a structured 5-panel comic outline with clear story progression.
    """
    # gemini-1.5-flash fallback to gemini-pro
    model_name = "gemini-1.5-flash"
    try:
        model = genai.GenerativeModel(
            model_name,
            generation_config={"response_mime_type": "application/json"}
        )
    except Exception:
        model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
You are an expert comic book creator.
Create a dynamic 5-panel comic story progression based on these inputs:
- Prompt: {story_prompt}
- Main Character: {character_name}
- Setting: {setting}
- Tone: {tone}
- Art Style: {art_style}

Follow this strict progression:
Panel 1: Introduction / Setup (The Beginning)
Panel 2: Rising Tension / Inciting Incident (The Problem)
Panel 3: Midpoint / Escalation (The Conflict)
Panel 4: Climax / Decisive Action (The Battle or Climax)
Panel 5: Resolution / Aftermath (The Ending)

Return ONLY a valid JSON list of 5 panel objects. Do not repeat titles or descriptions.
[
  {{
    "panel": 1,
    "title": "Title for Panel 1",
    "scene_description": "Clear scene description for panel 1",
    "image_prompt": "High quality vibrant digital comic art of {character_name} in {setting}, introduction, {art_style} style, detailed, 8k resolution"
  }},
  {{
    "panel": 2,
    "title": "Title for Panel 2",
    "scene_description": "Clear scene description for panel 2",
    "image_prompt": "High quality vibrant digital comic art of {character_name} facing an obstacle in {setting}, {art_style} style, dramatic lighting"
  }},
  {{
    "panel": 3,
    "title": "Title for Panel 3",
    "scene_description": "Clear scene description for panel 3",
    "image_prompt": "High quality digital comic art of {character_name} in high action in {setting}, {art_style} style"
  }},
  {{
    "panel": 4,
    "title": "Title for Panel 4",
    "scene_description": "Clear scene description for panel 4",
    "image_prompt": "High quality digital comic art of climax scene with {character_name} in {setting}, epic lighting, {art_style} style"
  }},
  {{
    "panel": 5,
    "title": "Title for Panel 5",
    "scene_description": "Clear scene description for panel 5",
    "image_prompt": "High quality digital comic art of peaceful ending with {character_name} in {setting}, {art_style} style, warm lighting"
  }}
]
"""
    try:
        response = model.generate_content(prompt)
        text_content = response.text.strip()
        text_content = re.sub(r"^```(?:json)?\s*", "", text_content, flags=re.MULTILINE)
        text_content = re.sub(r"\s*```$", "", text_content, flags=re.MULTILINE)
        data = json.loads(text_content.strip())
        if isinstance(data, list) and len(data) == 5:
            return data
    except Exception as e:
        print(f"Error in Gemini Flash outline generation: {e}")

    # Fallback WITH PROPER PROGRESSION (Same title repeat aagathu!)
    return [
        {
            "panel": 1,
            "title": "The Journey Begins",
            "scene_description": f"{character_name} stands at the boundary of {setting}, preparing for the adventure.",
            "image_prompt": f"Vibrant comic art of {character_name} standing proudly in {setting}, {art_style} style, sunny daylight, sharp focus."
        },
        {
            "panel": 2,
            "title": "The Unexpected Obstacle",
            "scene_description": f"Suddenly, a mysterious obstacle blocks the path in {setting}, demanding courage.",
            "image_prompt": f"Dramatic comic art of {character_name} confronting a mysterious challenge in {setting}, shadows, {art_style} style."
        },
        {
            "panel": 3,
            "title": "Into the Heart of Danger",
            "scene_description": f"{character_name} dives deep into {setting}, discovering ancient secrets and glowing mysteries.",
            "image_prompt": f"Action comic illustration of {character_name} moving cautiously through {setting}, magical glow, {art_style} style."
        },
        {
            "panel": 4,
            "title": "The Decisive Confrontation",
            "scene_description": f"With bravery, {character_name} makes the decisive move to overcome the core trial.",
            "image_prompt": f"Dynamic hero shot of {character_name} performing an epic leap in {setting}, intense action, {art_style} style."
        },
        {
            "panel": 5,
            "title": "A New Dawn Arrives",
            "scene_description": f"Peace returns to {setting} as {character_name} stands triumphant under a warm sky.",
            "image_prompt": f"Beautiful cinematic comic art of {character_name} resting happily in {setting}, golden hour sunset, {art_style} style."
        }
    ]