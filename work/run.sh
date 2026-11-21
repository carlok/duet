#!/usr/bin/env bash
# Runs inside the Podman container. Everything stays in this folder.
set -u
cd /home/claude/soup
CORES=$(nproc)
MEM_MB=$(awk '/MemAvailable/ {print int($2/1024)}' /proc/meminfo)
SEEDS=${SEEDS:-$(( (MEM_MB / 750) - 1 ))}; [ "$SEEDS" -gt $(( CORES - 1 )) ] && SEEDS=$(( CORES - 1 )); [ "$SEEDS" -lt 1 ] && SEEDS=1
BUDGET=${BUDGET:-3600}
echo "cores=$CORES mem_available=${MEM_MB}MB search_processes=$SEEDS budget=${BUDGET}s"
[ -f M_law_major.npy ] || { echo "building the law x structure matrix (all cores)..."; python3 matrix.py; }
CALIB_NULL=${CALIB_NULL:-30} CALIB_SEED=11 CALIB_OUT=calib_results_mac.pkl python3 calib.py > calib_mac.log 2>&1 &
for i in $(seq 1 "$SEEDS"); do python3 loop_dual.py "$BUDGET" $((100 + i)) > loopdual_$((100 + i)).log 2>&1 & done
wait
python3 report.py | tee report.txt
