"""T4: one data directory per arm, so the arms share no queue, dedup markers, gate, results or corpus.

    python -m soup.t4_setup [prior noprior]      (run once, before the T4 run; refuses to overwrite)

Each SOUP_DATA/t4-<arm>/ gets symlinks to the matrix files (read-only, memory-mapped; one copy in RAM)
and a copy of today's corpus store (the common start). Everything else (queue, results, journal, logs)
starts empty. Run an arm with SOUP_DATA=/data/t4-<arm>.
"""
import os
import shutil
import sys

from .paths import DATA

LINKED = ('M_probe_major.npy', 'M_law_major.npy', 'meta.pkl', 'nondeg.npy')


def setup(arm):
    d = DATA / f't4-{arm}'
    if d.exists(): raise SystemExit(f'{d} exists: T4 directories are created once')
    d.mkdir()
    for f in LINKED: os.symlink(os.path.join('..', f), d / f)
    shutil.copytree(DATA / 'corpus', d / 'corpus')
    n = sum(1 for e in os.listdir(d / 'corpus') if e.endswith('.npz'))
    print(f'{d}: matrix linked, corpus copied ({n} structures)')


if __name__ == '__main__':
    for arm in (sys.argv[1:] or ['prior', 'noprior']): setup(arm)
