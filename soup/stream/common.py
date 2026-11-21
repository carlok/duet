"""Small shared pieces: atomic JSON files, heartbeats, memory of a process, stop signals."""
import json
import os
import signal
import time
from pathlib import Path

import numpy as np

from ..paths import data, ensure


def _default(o):
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, (np.floating,)): return float(o)
    if isinstance(o, (np.bool_,)): return bool(o)
    if isinstance(o, (set, tuple, np.ndarray)): return list(o)
    raise TypeError(type(o))


def dumps(obj): return json.dumps(obj, ensure_ascii=False, default=_default)


def write_json(path, obj):
    """Write-then-rename: readers never see a half-written file."""
    path = Path(path); tmp = path.with_name(f'.tmp-{path.name}-{os.getpid()}')
    tmp.write_text(dumps(obj)); os.replace(tmp, path)


def read_json(path):
    try: return json.loads(Path(path).read_text())
    except (FileNotFoundError, json.JSONDecodeError): return None


def heartbeat(name, **fields):
    ensure('logs', 'workers')
    write_json(data('logs', 'workers', f'{name}.json'), dict(name=name, pid=os.getpid(), t=time.time(), **fields))


MATRIX_FILES = ('M_probe_major.npy', 'M_law_major.npy')


def memory(pid):
    """Memory of a process in MB from /proc: rss, pss (shared pages divided among the sharers),
    private, shared, and the part of rss/pss that is the memory-mapped matrix."""
    out = {}
    try:
        for line in open(f'/proc/{pid}/smaps_rollup'):
            k, *v = line.split()
            if k in ('Rss:', 'Pss:', 'Shared_Clean:', 'Shared_Dirty:', 'Private_Clean:', 'Private_Dirty:'):
                out[k[:-1]] = int(v[0]) / 1024
        mrss = mpss = 0.0; inside = False
        for line in open(f'/proc/{pid}/smaps'):
            parts = line.split()
            if parts and '-' in parts[0] and len(parts) >= 5:      # a mapping header line
                inside = any(line.rstrip().endswith(m) for m in MATRIX_FILES)
            elif inside and parts[0] == 'Rss:': mrss += int(parts[1]) / 1024
            elif inside and parts[0] == 'Pss:': mpss += int(parts[1]) / 1024
    except (FileNotFoundError, ProcessLookupError, PermissionError):
        return None
    r = lambda x: round(x, 1)
    return {'rss_mb': r(out.get('Rss', 0)), 'pss_mb': r(out.get('Pss', 0)),
            'private_mb': r(out.get('Private_Clean', 0) + out.get('Private_Dirty', 0)),
            'shared_mb': r(out.get('Shared_Clean', 0) + out.get('Shared_Dirty', 0)),
            'matrix_rss_mb': r(mrss), 'matrix_pss_mb': r(mpss)}


class Stop(Exception):
    pass


class StopFlag:
    """SIGTERM/SIGINT: set a flag; with raise_=True also interrupt the running Python code."""
    def __init__(self, raise_=False):
        self.set = False; self.raise_ = raise_
        signal.signal(signal.SIGTERM, self._h); signal.signal(signal.SIGINT, self._h)

    def _h(self, *_):
        first = not self.set
        self.set = True
        if self.raise_ and first: raise Stop()
