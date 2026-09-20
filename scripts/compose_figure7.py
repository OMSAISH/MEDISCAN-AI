import os
from PIL import Image, ImageDraw, ImageFont

FONT_PATH_REG = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_PATH_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

STEPS_DIR = "/Users/omsaishdhokchaule/.gemini/antigravity/brain/aeea39ca-d2bf-42b0-b6dc-682fe1ff841c/scratch/steps"
OUTPUT_PATH = "/Users/omsaishdhokchaule/.gemini/antigravity/brain/aeea39ca-d2bf-42b0-b6dc-682fe1ff841c/figure7_user_workflow.png"
DOCS_OUTPUT_PATH = "/Users/omsaishdhokchaule/Downloads/MEDISCAN-AI/docs/figure7_user_workflow.png"

def draw_arrow(draw, start_xy, end_xy, color="#0f172a", width=5, arrow_size=16):
    x1, y1 = start_xy
    x2, y2 = end_xy
    draw.line([x1, y1, x2, y2], fill=color, width=width)
    
    # Arrow head
    if x2 > x1: # pointing right
        draw.polygon([
            (x2, y2),
            (x2 - arrow_size, y2 - arrow_size // 1.3),
            (x2 - arrow_size, y2 + arrow_size // 1.3)
        ], fill=color)
    elif y2 > y1: # pointing down
        draw.polygon([
            (x2, y2),
            (x2 - arrow_size // 1.3, y2 - arrow_size),
            (x2 + arrow_size // 1.3, y2 - arrow_size)
        ], fill=color)

def main():
    W, H = 2400, 1560
    img = Image.new("RGB", (W, H), "#f8fafc")
    draw = ImageDraw.Draw(img)

    # Fonts
    title_font = ImageFont.truetype(FONT_PATH_BOLD, 36)
    subtitle_font = ImageFont.truetype(FONT_PATH_REG, 21)
    card_title_font = ImageFont.truetype(FONT_PATH_BOLD, 22)
    card_desc_font = ImageFont.truetype(FONT_PATH_REG, 15)
    num_font = ImageFont.truetype(FONT_PATH_BOLD, 20)

    # 1. Header Banner
    header_x1, header_y1 = 40, 30
    header_x2, header_y2 = W - 40, 150
    draw.rounded_rectangle([header_x1, header_y1, header_x2, header_y2], radius=16, fill="#0f2b48")

    # Header Text
    t_text = "Figure 7 – User Workflow and System Interface Flow"
    sub_text = "Step-by-step process of how a researcher uses MediScan AI for drug repurposing analysis"
    
    # Centers
    t_bbox = draw.textbbox((0, 0), t_text, font=title_font)
    sub_bbox = draw.textbbox((0, 0), sub_text, font=subtitle_font)
    
    draw.text(((W - (t_bbox[2] - t_bbox[0])) // 2, 50), t_text, font=title_font, fill="#ffffff")
    draw.text(((W - (sub_bbox[2] - sub_bbox[0])) // 2, 98), sub_text, font=subtitle_font, fill="#93c5fd")

    # Step Definitions
    steps_config = [
        # Row 1 (4 cards)
        {
            "num": "1",
            "title": "Login / Register",
            "desc": "User creates an account or logs in to access the platform.",
            "color": "#1d4ed8",
            "bg_color": "#eff6ff",
            "border_color": "#bfdbfe",
            "img": "step1_login.png",
            "crop": (280, 100, 1000, 780),
            "rect": (40, 180, 560, 800)
        },
        {
            "num": "2",
            "title": "Search for a Drug",
            "desc": "User enters a drug name to start the analysis.",
            "color": "#059669",
            "bg_color": "#ecfdf5",
            "border_color": "#a7f3d0",
            "img": "step2_search.png",
            "crop": (60, 70, 1220, 780),
            "rect": (630, 180, 1150, 800)
        },
        {
            "num": "3",
            "title": "AI Agents Processing",
            "desc": "Multiple AI agents work in parallel to gather and analyze information.",
            "color": "#d97706",
            "bg_color": "#fffbeb",
            "border_color": "#fde68a",
            "img": "step3_processing.png",
            "crop": (60, 70, 1220, 780),
            "rect": (1220, 180, 1740, 800)
        },
        {
            "num": "4",
            "title": "View Results",
            "desc": "System presents potential new indications with confidence scores.",
            "color": "#6d28d9",
            "bg_color": "#f5f3ff",
            "border_color": "#ddd6fe",
            "img": "step4_results.png",
            "crop": (60, 70, 1220, 780),
            "rect": (1810, 180, 2330, 800)
        },
        # Row 2 (3 cards)
        {
            "num": "5",
            "title": "Explore Detailed Evidence",
            "desc": "User can view supporting evidence from all sources with explanations.",
            "color": "#be185d",
            "bg_color": "#fdf2f8",
            "border_color": "#fbcfe8",
            "img": "step5_evidence.png",
            "crop": (180, 100, 1100, 820),
            "rect": (40, 880, 760, 1500)
        },
        {
            "num": "6",
            "title": "Generate Research Report",
            "desc": "User exports a comprehensive report in multiple formats.",
            "color": "#0f766e",
            "bg_color": "#f0fdfa",
            "border_color": "#99f6e4",
            "img": "step6_report.png",
            "crop": (380, 300, 900, 720),
            "rect": (830, 880, 1550, 1500)
        },
        {
            "num": "7",
            "title": "Save and Track Progress",
            "desc": "All searches and reports are saved in the user dashboard for future reference.",
            "color": "#1d4ed8",
            "bg_color": "#eff6ff",
            "border_color": "#bfdbfe",
            "img": "step7_dashboard.png",
            "crop": (60, 70, 1220, 780),
            "rect": (1620, 880, 2340, 1500)
        }
    ]

    for step in steps_config:
        x1, y1, x2, y2 = step["rect"]
        
        # Draw outer card container
        draw.rounded_rectangle([x1, y1, x2, y2], radius=14, fill="#ffffff", outline=step["border_color"], width=2)
        
        # Header banner inside card
        header_h = 74
        draw.rounded_rectangle([x1, y1, x2, y1 + header_h], radius=14, fill=step["bg_color"])
        draw.rectangle([x1, y1 + header_h - 14, x2, y1 + header_h], fill=step["bg_color"]) # square bottom of header
        draw.line([x1, y1 + header_h, x2, y1 + header_h], fill=step["border_color"], width=1)

        # Number Badge (Circle)
        badge_r = 18
        badge_cx, badge_cy = x1 + 30, y1 + 36
        draw.ellipse([badge_cx - badge_r, badge_cy - badge_r, badge_cx + badge_r, badge_cy + badge_r], fill=step["color"])
        
        # Number inside badge
        n_bbox = draw.textbbox((0, 0), step["num"], font=num_font)
        draw.text((badge_cx - (n_bbox[2] - n_bbox[0]) // 2, badge_cy - (n_bbox[3] - n_bbox[1]) // 2 - 1), step["num"], font=num_font, fill="#ffffff")

        # Step Title
        draw.text((x1 + 62, y1 + 14), step["title"], font=card_title_font, fill="#0f172a")

        # Step Description (truncated or wrapped)
        draw.text((x1 + 62, y1 + 44), step["desc"], font=card_desc_font, fill="#475569")

        # Load screenshot
        screenshot_path = os.path.join(STEPS_DIR, step["img"])
        if os.path.exists(screenshot_path):
            raw_shot = Image.open(screenshot_path)
            cropped_shot = raw_shot.crop(step["crop"])
            
            # Target inner size
            inner_pad = 12
            target_w = (x2 - x1) - (inner_pad * 2)
            target_h = (y2 - y1) - header_h - (inner_pad * 2)
            
            # Resize preserving aspect ratio or fitting nicely
            shot_resized = cropped_shot.resize((target_w, target_h), Image.Resampling.LANCZOS)
            
            # Frame around screenshot
            shot_x = x1 + inner_pad
            shot_y = y1 + header_h + inner_pad
            
            img.paste(shot_resized, (shot_x, shot_y))
            draw.rectangle([shot_x, shot_y, shot_x + target_w, shot_y + target_h], outline="#cbd5e1", width=1)

    # 2. Draw connecting arrows
    # Row 1 horizontal arrows
    draw_arrow(draw, (565, 490), (625, 490), color="#1e293b", width=5, arrow_size=16)
    draw_arrow(draw, (1155, 490), (1215, 490), color="#1e293b", width=5, arrow_size=16)
    draw_arrow(draw, (1745, 490), (1805, 490), color="#1e293b", width=5, arrow_size=16)

    # Connecting curve/elbow arrow from Card 4 down to Card 5
    # From (2070, 800) down to 840, across to 400, down to 875
    path_points = [
        (2070, 800),
        (2070, 840),
        (400, 840),
        (400, 875)
    ]
    draw.line([(2070, 800), (2070, 840)], fill="#1e293b", width=5)
    draw.line([(2070, 840), (400, 840)], fill="#1e293b", width=5)
    draw_arrow(draw, (400, 840), (400, 875), color="#1e293b", width=5, arrow_size=16)

    # Row 2 horizontal arrows
    draw_arrow(draw, (765, 1190), (825, 1190), color="#1e293b", width=5, arrow_size=16)
    draw_arrow(draw, (1555, 1190), (1615, 1190), color="#1e293b", width=5, arrow_size=16)

    # Save output image
    img.save(OUTPUT_PATH, "PNG", quality=95)
    img.save(DOCS_OUTPUT_PATH, "PNG", quality=95)
    print(f"Composite Figure 7 saved successfully to {OUTPUT_PATH} and {DOCS_OUTPUT_PATH}")

if __name__ == "__main__":
    main()
