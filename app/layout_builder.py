import re

def build_comic_layout(image_paths: list, full_story: str, outline: list) -> list:
    """
    Combines images, generated story, and outline descriptions into a structured panel list.
    """
    # Split story into panel blocks using regex header matches
    raw_story_panels = re.split(r'\*\*Panel\s+\d+[:\s]*', full_story)
    
    # Clean up empty splits
    story_panels = [p.strip() for p in raw_story_panels if p.strip()]
    
    layout = []
    for idx, (img_path, panel_info) in enumerate(zip(image_paths, outline)):
        # Retrieve corresponding story block or fallback to scene description
        text_content = story_panels[idx] if idx < len(story_panels) else panel_info.get("scene_description", "")
        
        # Clean heading lines inside the text content if duplicated
        lines = text_content.splitlines()
        if lines and lines[0].strip().startswith("**"):
            lines = lines[1:]
        cleaned_text = "\n".join(lines).strip()

        layout.append({
            "panel": panel_info.get("panel", idx + 1),
            "title": panel_info.get("title", f"Panel {idx + 1}"),
            "image_path": img_path,
            "text": cleaned_text,
            "scene_description": panel_info.get("scene_description", ""),
            "image_prompt": panel_info.get("image_prompt", "")
        })
        
    return layout