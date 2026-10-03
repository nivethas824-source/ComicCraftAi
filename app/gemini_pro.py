import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def get_working_model():
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for m in available_models:
            if "pro" in m:
                return genai.GenerativeModel(m)
        for m in available_models:
            if "flash" in m:
                return genai.GenerativeModel(m)
        if available_models:
            return genai.GenerativeModel(available_models[0])
    except Exception as e:
        print(f"Model listing fallback notice: {e}")
    return genai.GenerativeModel("gemini-pro")

def generate_story(outline: list, tone: str, art_style: str) -> str:
    model = get_working_model()
    
    formatted_outline = ""
    for p in outline:
        formatted_outline += f"Panel {p.get('panel')}: {p.get('title')}\nDescription: {p.get('scene_description')}\n\n"
        
    prompt = f"""
You are a comic book script writer.
Expand this 5-panel comic outline into an engaging narrative:
Tone: {tone}
Art Style: {art_style}

Outline:
{formatted_outline}

Format output panel by panel using '**Panel X: Title**':
- CAPTION: Scene atmosphere
- NARRATION: Core actions and events
- DIALOGUE: Character spoken lines
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error in generate_story: {e}")
        fallback_text = ""
        for p in outline:
            fallback_text += f"**Panel {p.get('panel')}: {p.get('title')}**\n"
            fallback_text += f"**CAPTION** Atmospheric tones fill the surroundings in {tone} style.\n"
            fallback_text += f"**NARRATION** {p.get('scene_description')}\n\n"
        return fallback_text