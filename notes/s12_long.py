"""T6: S12 => x·x = x∘x, long prover runs (night 22-23 Nov 2026, after X5). Earlier budget: 1,800 s per prover
(REPORT, round 2); here 7,200 s each, four jobs in parallel, full output kept in work/check/s12_long/<job>.txt.

    podman run -d --name soup-s12 -v "$PWD/work:/data" -v "$PWD/notes:/notes:ro" -e PYTHONPATH=/app soup python3 /notes/s12_long.py

Jobs: Vampire FMB (-sa fmb), Vampire portfolio casc_sat, Vampire casc, Twee. Every prover under SOUP_PROVER_MEMORY_MB.
A model, if one is found, is checked afterwards by law_vector and direct evaluation before anything is reported.
"""
import json, os, re, subprocess, tempfile, time
from concurrent.futures import ThreadPoolExecutor, as_completed

from soup.named import law_index
from soup.provers import problem, PROVER_MB, V_BIN, T_BIN

S12 = sorted(law_index(s) for s in ['x·(y∘(y∘(x∘y)))=x', 'x∘(y·(y·(x·y)))=x',
                                     '(((x∘y)∘x)∘x)·y=y', '(((x·y)·x)·x)∘y=y'])
GOAL = law_index('x·x=x∘x')
SECS = int(os.environ.get('S12_SECS', 7200))
OUT = os.environ.get('S12_OUT', '/data/check/s12_long')
os.makedirs(OUT, exist_ok=True)
src = problem(S12, GOAL)
open(f'{OUT}/problem.p', 'w').write(src)
JOBS = {
    'vampire_fmb': [V_BIN, '-sa', 'fmb', '-m', str(PROVER_MB), '-t', str(SECS)],
    'vampire_casc_sat': [V_BIN, '--mode', 'portfolio', '--schedule', 'casc_sat', '-m', str(PROVER_MB), '-t', str(SECS)],
    'vampire_casc': [V_BIN, '--mode', 'casc', '-m', str(PROVER_MB), '-t', str(SECS)],
    'twee': [T_BIN, None, '+RTS', f'-M{PROVER_MB}m', '-RTS'],
}


def run(name):
    cmd = [f'{OUT}/problem.p' if c is None else c for c in JOBS[name]]
    if name != 'twee': cmd.append(f'{OUT}/problem.p')
    t0 = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=SECS + 120)
        out, rc = r.stdout + r.stderr, r.returncode
    except subprocess.TimeoutExpired as e:
        out, rc = (e.stdout or b'').decode(errors='replace') if isinstance(e.stdout, bytes) else (e.stdout or ''), 'timeout'
    open(f'{OUT}/{name}.txt', 'w').write(out)
    m = re.search(r'SZS status (\w+)', out) or re.search(r'RESULT: (\w+)', out)
    return {'job': name, 'szs': m.group(1) if m else None, 'rc': rc, 'secs': round(time.time() - t0, 1),
            'finite_model': 'Finite Model Found' in out or 'fmb' in name and 'Satisfiable' in out}


print(json.dumps({'start_utc': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()), 'secs': SECS, 'mem_mb': PROVER_MB}),
      flush=True)
res = []
with ThreadPoolExecutor(len(JOBS)) as ex:
    for f in as_completed([ex.submit(run, j) for j in JOBS]):
        res.append(f.result()); print(json.dumps(f.result()), flush=True)
json.dump(res, open(f'{OUT}/summary.json', 'w'), indent=1)
print(json.dumps({'end_utc': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}), flush=True)
