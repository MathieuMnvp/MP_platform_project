import numpy as np

n = 17
pitch = 0.012618
radius = 0.004757
half_gap = 0.0004035
active_height = 2.005613

with open("buoyantSimple_PWR/system/searchableCylinder", "w") as f:
    for i in range(n):
        for j in range(n):
            x = ((i+0.5) * pitch) + half_gap
            y = ((j+0.5) * pitch) + half_gap
            f.write(f"rod_{i+1}_{j+1}\n")
            f.write("{\n")
            f.write(f"    type searchableCylinder;\n")
            f.write(f"    point1 ({x} {y} 0);\n")
            f.write(f"    point2 ({x} {y} {active_height});\n")
            f.write(f"    radius {radius};\n")
            f.write("}\n\n")



