import cv2
import numpy as np
import sys
import os
import ezdxf
sys.path.append('archvec-studio-pro')
from api.vectorize import process_image

filepath = 'archvec-studio-pro/presets/plan1.png'
with open(filepath, 'rb') as f:
    img_bytes = f.read()

res = process_image(img_bytes, epsilon=2.5)

# 1. Save DXF
with open('archvec-studio-pro/final_stunning_output.dxf', 'w') as f:
    f.write(res['dxf'])

# 2. Render high-res PNG from the parsed lines
width, height = res['width'], res['height']
scale = 2
canvas = np.zeros((height*scale, width*scale, 3), dtype=np.uint8)

# Colors
color_wall = (248, 189, 56) # BGR for #38bdf8
color_furn = (60, 146, 251) # BGR for #fb923c
color_anno = (102, 51, 255) # BGR for #ff3366

for l in res['lines']:
    color = color_wall if l['layer'] == 'A-WALL' else (color_furn if l['layer'] == 'A-FURN' else color_anno)
    thickness = 3 if l['layer'] == 'A-WALL' else 2
    cv2.line(canvas, (int(l['x1']*scale), int(l['y1']*scale)), (int(l['x2']*scale), int(l['y2']*scale)), color, thickness, cv2.LINE_AA)

# Draw texts
for t in res['texts']:
    cv2.putText(canvas, t['text'], (int(t['x']*scale), int(t['y']*scale)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_anno, 2, cv2.LINE_AA)

cv2.imwrite('archvec-studio-pro/stunning_preview.png', canvas)
print("Preview and DXF generated!")
