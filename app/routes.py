import os
import traceback
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.gemini_flash import generate_outline
from app.gemini_pro import generate_story
from app.image_generator import generate_image
from app.layout_builder import build_comic_layout
from app.exporters import save_pdf

# Router and template initialization
router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Pydantic Model for JSON Endpoint
class PromptRequest(BaseModel):
    story_prompt: str
    character_name: str
    setting: str
    tone: str
    art_style: str

# 1. Homepage Route
@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

# 2. Form Submission & Comic Generation Route
@router.post("/generate", response_class=HTMLResponse)
async def generate_comic(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...)
):
    try:
        # Step 1: Generate 5-panel comic outline
        outline = generate_outline(story_prompt, character_name, setting, tone, art_style)
        
        if not isinstance(outline, list) or not all("image_prompt" in panel for panel in outline):
            raise ValueError("Invalid outline structure from Gemini response.")

        # Step 2: Generate narration and dialogues
        full_story = generate_story(outline, tone, art_style)

        # Step 3: Generate images for each panel
        images = []
        for panel in outline:
            prompt = panel.get("image_prompt", f"{character_name} in {setting}, {art_style}")
            img_path = generate_image(prompt)
            images.append(img_path)

        # Step 4: Build Layout
        layout = build_comic_layout(images, full_story, outline)

        # Step 5: Export to PDF
        pdf_path = save_pdf(layout)
        web_pdf_path = pdf_path.replace("\\", "/")

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "layout": layout,
                "pdf_path": web_pdf_path
            }
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# 3. JSON-based Comic Generation Route
@router.post("/generate-comic/json")
async def generate_comic_json(payload: PromptRequest):
    try:
        outline = generate_outline(
            payload.story_prompt,
            payload.character_name,
            payload.setting,
            payload.tone,
            payload.art_style
        )
        full_story = generate_story(outline, payload.tone, payload.art_style)
        images = [generate_image(p.get("image_prompt", "")) for p in outline]
        layout = build_comic_layout(images, full_story, outline)
        pdf_path = save_pdf(layout)

        return {
            "status": "success",
            "layout": layout,
            "pdf_path": pdf_path.replace("\\", "/")
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# 4. Export Success Route
@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request, pdf_path: str = ""):
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={"pdf_path": pdf_path}
    )

# 5. Developer Test Route for Image Generation
@router.get("/test-image")
async def test_image(prompt: str = "A futuristic city at sunset, sci-fi, cinematic, artstation"):
    try:
        image_path = generate_image(prompt)
        return {"message": "Image generated successfully", "path": image_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))