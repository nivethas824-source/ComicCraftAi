import os
from datetime import datetime
from fpdf import FPDF

EXPORT_FOLDER = os.path.join("static", "exports")
FONT_PATH = os.path.join("fonts", "DejaVuSans.ttf")

def save_pdf(layout: list) -> str:
    """
    Compiles comic panels into a PDF using FPDF and saves it into static/exports/.
    """
    os.makedirs(EXPORT_FOLDER, exist_ok=True)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Unicode Font Handling
    has_custom_font = False
    if os.path.exists(FONT_PATH):
        try:
            pdf.add_font("DejaVu", "", FONT_PATH)
            has_custom_font = True
        except Exception as e:
            print(f"Font loading error: {e}")

    font_family = "DejaVu" if has_custom_font else "Helvetica"

    for panel in layout:
        pdf.add_page()
        
        # Panel Title
        pdf.set_font(font_family, "B" if not has_custom_font else "", 14)
        pdf.cell(0, 10, f"Panel {panel['panel']}: {panel['title']}", ln=True, align="C")
        
        # Image Placement
        image_path = panel.get("image_path", "")
        y_image = 30
        image_height = 90
        spacing_after = 10

        if os.path.exists(image_path):
            pdf.image(image_path, x=35, y=y_image, w=140, h=image_height)
        else:
            pdf.set_y(y_image)
            pdf.set_font(font_family, "", 10)
            pdf.multi_cell(0, 10, f"[Image missing: {image_path}]", align="C")

        # Text Placement Below Image
        pdf.set_y(y_image + image_height + spacing_after)
        pdf.set_font(font_family, "", 11)
        
        story_text = panel.get("text", "")
        # Sanitize text for standard FPDF if custom font is absent
        if not has_custom_font:
            story_text = story_text.encode('latin-1', 'replace').decode('latin-1')

        pdf.multi_cell(0, 7, story_text)

    # Save PDF with unique timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"comic_{timestamp}.pdf"
    pdf_path = os.path.join(EXPORT_FOLDER, filename)
    pdf.output(pdf_path)
    
    return f"static/exports/{filename}"