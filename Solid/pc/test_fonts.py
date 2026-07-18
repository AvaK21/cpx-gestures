from PIL import ImageFont, ImageDraw, Image
import numpy as np
import os
import cv2

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
font_location = os.path.join(BASE_DIR, "font", "VERDANA.TTF") # path to the font file
font = ImageFont.truetype(font_location, 28)  # load once, outside loop

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # --- your MediaPipe logic here ---

    # PIL text draw
    img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).convert("RGBA")
    overlay = Image.new("RGBA", img_pil.size,(0,0,0,0))
    draw_overlay = ImageDraw.Draw(overlay)
    text = "Thumbs_UP (97.23%)"
    bbox = draw_overlay.textbbox((10, 30), text = text, font=font)
    padding = 6

    draw_overlay.rectangle(
    (bbox[0] - padding, bbox[1] - padding, bbox[2] + padding, bbox[3] + padding),
    fill=(0, 0, 0, 100)  # black, semi-transparent
    )  

    draw_overlay.text((10,30), text = text,font = font, fill = (255,255,255,255))

    
    img_pil = Image.alpha_composite(img_pil, overlay).convert("RGB")


    frame = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

    cv2.imshow("Gestures", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break