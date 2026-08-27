import cv2
import math
import os
import sys
sys.path.append('archvec-studio')
from api.vectorize import process_image, pdist

dataset = ['plan1.png', 'plan2.jpg', 'plan3.png', 'plan4.png', 'plan5.png', 'plan6.png']
results = []

print(f"{'Plan Name':<15} | {'Polys':<6} | {'Lines':<6} | {'Orthogonal %':<12} | {'Texts':<5} | {'Status'}")
print("-" * 70)

for plan in dataset:
    filepath = os.path.join('archvec-studio/presets', plan)
    if not os.path.exists(filepath):
        continue
    
    with open(filepath, 'rb') as f:
        img_bytes = f.read()
    
    try:
        res = process_image(img_bytes)
        polys = res['polygons']
        
        total_lines = 0
        ortho_lines = 0
        
        for p in polys:
            pts = p['pts']
            n = len(pts)
            for i in range(n):
                p1 = pts[i]
                p2 = pts[(i+1)%n]
                dx = p2['x'] - p1['x']
                dy = p2['y'] - p1['y']
                dist = math.hypot(dx, dy)
                if dist < 1.0:
                    continue
                total_lines += 1
                deg = math.degrees(math.atan2(dy, dx)) % 180.0
                # Check if it's perfectly horizontal or vertical (within 1 degree)
                if deg < 1.0 or deg > 179.0 or abs(deg - 90.0) < 1.0:
                    ortho_lines += 1
                    
        ortho_pct = (ortho_lines / total_lines * 100) if total_lines > 0 else 0
        print(f"{plan:<15} | {len(polys):<6} | {total_lines:<6} | {ortho_pct:>6.1f}%      | {len(res['texts']):<5} | SUCCESS")
    except Exception as e:
        print(f"{plan:<15} | ERROR: {str(e)}")
