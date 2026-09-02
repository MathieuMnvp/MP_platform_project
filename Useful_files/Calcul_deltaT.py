import numpy as np
import pandas as pd
from pathlib import Path
from collections import defaultdict

input_file = "TH_output.csv"

# Lecture du fichier
with open(input_file, 'r') as f:
    z_list = []
    for z in range(1, 25):
        xy_list = []
        f.seek(0)  # Revenir au début du fichier pour chaque z
        for line in f:
            if not line.strip() or line.startswith('#'):
                continue
            parts = line.split(',')  # Utiliser ',' au lieu de split() par défaut
            if len(parts) >= 4:
                try:
                    iz = int(parts[2])
                    T = float(parts[3])
                    if iz == z:
                        xy_list.append(T)
                except (ValueError, IndexError):
                    continue
        if xy_list:
            z_list.append(np.mean(xy_list))
        else:
            z_list.append(np.nan)

print(z_list)







