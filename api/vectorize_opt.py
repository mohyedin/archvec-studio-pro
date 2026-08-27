import sys
import re

filepath = 'archvec-studio/api/vectorize.py'
with open(filepath, 'r') as f:
    code = f.read()

weld_code = """
def weld_vertices(polys, threshold=4.0):
    all_pts = []
    for p in polys:
        all_pts.extend(p)
    
    # Simple O(N^2) clustering for small N
    clusters = []
    for pt in all_pts:
        found = False
        for cluster in clusters:
            cx, cy, count = cluster['sum_x']/cluster['count'], cluster['sum_y']/cluster['count'], cluster['count']
            if math.hypot(pt['x'] - cx, pt['y'] - cy) < threshold:
                cluster['sum_x'] += pt['x']
                cluster['sum_y'] += pt['y']
                cluster['count'] += 1
                cluster['pts'].append(pt)
                found = True
                break
        if not found:
            clusters.append({'sum_x': pt['x'], 'sum_y': pt['y'], 'count': 1, 'pts': [pt]})
            
    for cluster in clusters:
        avg_x = round(cluster['sum_x'] / cluster['count'], 2)
        avg_y = round(cluster['sum_y'] / cluster['count'], 2)
        for pt in cluster['pts']:
            pt['x'] = avg_x
            pt['y'] = avg_y
            
    return polys
"""

# Insert weld_code before process_image
if 'def weld_vertices' not in code:
    code = code.replace('def process_image(', weld_code + '\ndef process_image(')

# Call weld_vertices after apply_regression
if 'clean_polys = [cad_master_regularize(p) for p in clean_polys]' in code:
    if 'clean_polys = weld_vertices(clean_polys)' not in code:
        code = code.replace(
            'clean_polys = [cad_master_regularize(p) for p in clean_polys]',
            'clean_polys = [cad_master_regularize(p) for p in clean_polys]\n        clean_polys = weld_vertices(clean_polys)'
        )

with open(filepath, 'w') as f:
    f.write(code)

print("Optimization injected successfully.")
