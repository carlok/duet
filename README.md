# soup: genetic search over two-operation equational theories (Podman bundle)

Everything runs inside a container; nothing is installed on the Mac. Outputs stay in `work/`.

    cd ~/tmp/soup
    podman machine inspect --format '{{.Resources.CPUs}} CPUs, {{.Resources.Memory}} MB'   # what the Podman VM has now
    # optional, your call: give the Podman VM more of the Mac (needs a restart of the VM)
    #   podman machine stop && podman machine set --cpus 11 --memory 12288 && podman machine start
    podman build -t soup .
    podman run --rm -v "$PWD/work:/home/claude/soup" soup

What `run.sh` does, in the container:
1. Builds the 71,369-law x 12,509-structure matrix once (about 1 GB of RAM at peak; written to `work/`).
2. Runs the calibration: lattice, skew lattice, dimonoid, absorption pair, one-sided quasigroups against
   size-matched random theories (CALIB_NULL=30 per size by default).
3. Runs the duality-prior MAP-Elites search, one process per spare core (about 750 MB each), for BUDGET seconds (default 3600).
4. Writes `work/report.txt`.

Knobs: `podman run --rm -e BUDGET=7200 -e SEEDS=8 -e CALIB_NULL=50 -v "$PWD/work:/home/claude/soup" soup`
