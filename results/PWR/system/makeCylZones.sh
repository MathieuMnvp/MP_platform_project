#!/usr/bin/env bash
set -euo pipefail
Lx=1.0                
radius_cm=0.4757      
pitch_cm=1.2618        
ag_cm=0.04035          


# Conversion en mètres
radius=$(echo "$radius_cm*0.01" | bc -l)
pitch=$(echo "$pitch_cm*0.01" | bc -l)
offset=$(echo "($ag_cm + $pitch_cm/2)*0.01" | bc -l)

# Création du topoSetDict
mkdir -p system
cat > system/topoSetDict <<EOF
actions
(
EOF

for i in $(seq 0 16); do
  for j in $(seq 0 16); do
    yi=$(echo "$offset + $pitch * $i" | bc -l)
    zj=$(echo "$offset + $pitch * $j" | bc -l)
    name="fuel_${i}_${j}"

    cat >> system/topoSetDict <<EOF
  {
    name    ${name}_cells;
    type    cellSet;
    action  new;
    source  cylinderToCell;
    sourceInfo
    {
      p1      (0 ${yi} ${zj});
      p2      (${Lx} ${yi} ${zj});
      radius  ${radius};
    }
  }
  {
    name    ${name};
    type    cellZoneSet;
    action  new;
    source  setToCellZone;
    sourceInfo
    {
      set ${name}_cells;
    }
  }
EOF
  done
done

cat >> system/topoSetDict <<EOF
);
EOF
