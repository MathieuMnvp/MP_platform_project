import numpy as np

n = 17
pitch = 0.012618
radius = 0.004757
half_gap = 0.0004035
active_height = 2.005613

with open("buoyantSimple_PWR/system/refinementRegionsDict", "w") as f:
    for i in range(n):
        for j in range(n):
            name = f"rod_{i+1}_{j+1}"
            f.write(f"    {name}\n")
            f.write("    {\n")
            f.write("        mode inside;\n")
            f.write(f"       levels ((1E15 0));\n")
            f.write("    }\n")

