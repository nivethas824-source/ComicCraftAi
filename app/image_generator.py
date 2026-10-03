import os
import re
import torch
from PIL import Image

_pipe = None

def sanitize_filename(prompt: str) -> str:
    clean = re.sub(r'[^\w\s-]', '', prompt[:35]).strip().lower()
    return re.sub(r'[-\s]+', '_', clean)

def get_pipeline():
    global _pipe
    if _pipe is None:
        try:
            from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
            model_id = "runwayml/stable-diffusion-v1-5"
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"Loading Stable Diffusion pipeline on: {device}...")
            
            _pipe = StableDiffusionPipeline.from_pretrained(
                model_id,
                torch_dtype=torch.float32,
                safety_checker=None,
                requires_safety_checker=False
            ).to(device)
            
            # Fast & High Quality Scheduler (DPM-Solver): குறைவான steps-லும் தெளிவான படம் தரும்
            _pipe.scheduler = DPMSolverMultistepScheduler.from_config(_pipe.scheduler.config)
            _pipe.enable_attention_slicing()
        except Exception as e:
            print(f"Failed to load Diffusers pipeline: {e}")
            _pipe = "FALLBACK"
    return _pipe

def generate_image(prompt: str, filename: str = None) -> str:
    if not filename:
        filename = f"{sanitize_filename(prompt)}.png"
    if not filename.endswith(".png"):
        filename += ".png"

    output_dir = os.path.join("static", "panels")
    os.makedirs(output_dir, exist_ok=True)
    full_path = os.path.join(output_dir, filename)

    pipe = get_pipeline()
    
    if pipe != "FALLBACK" and pipe is not None:
        try:
            # 512x512 with 10 steps + DPM-Solver yields sharp, clear comic illustrations
            image = pipe(
                prompt=f"{prompt}, high quality, crisp comic illustration, highly detailed, vivid colors",
                negative_prompt="blurry, low quality, distorted, bad anatomy, pixelated, watermark",
                num_inference_steps=10,
                height=512,
                width=512,
                guidance_scale=7.5
            ).images[0]
            image.save(full_path)
            return f"static/panels/{filename}"
        except Exception as e:
            print(f"Error during image generation: {e}")

    # Fallback Placeholder
    img = Image.new("RGB", (512, 512), color=(44, 62, 80))
    img.save(full_path)
    return f"static/panels/{filename}"