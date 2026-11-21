"""External provers (T2). E first: one deterministic strategy (--auto), a processed-clause budget instead
of a CPU-time budget (so the result does not depend on machine speed), proof object for proof length.

prove_e(T, goal) -> dict(status, proof_steps, processed, secs)
  status       'proved' | 'unknown' (budget or resource out) | 'countersatisfiable' | 'error'
  proof_steps  inference steps in the proof object (derived clauses, input clauses not counted)
  processed    E's processed-clause count: a deterministic effort measure
"""
import os
import re
import subprocess
import tempfile
import time

from .data import fof

E_BIN = os.environ.get('SOUP_EPROVER', 'eprover')


def problem(T, goal):
    return '\n'.join([fof(t, f'a{k}', 'axiom') for k, t in enumerate(T)] + [fof(goal, 'goal', 'conjecture')]) + '\n'


def _proof_steps(out):
    m = re.search(r'# SZS output start CNFRefutation(.*?)# SZS output end', out, re.S)
    if not m: return None
    steps = 0
    for line in m.group(1).splitlines():
        line = line.strip()
        if not (line.startswith('cnf(') or line.startswith('fof(')): continue
        if ", file(" in line or ",file(" in line: continue      # input formula
        steps += 1
    return steps


def prove_e(T, goal, processed_limit=200_000, cpu_limit=300, extra=()):
    src = problem(T, goal)
    with tempfile.NamedTemporaryFile('w', suffix='.p', delete=False) as fh:
        fh.write(src); path = fh.name
    t0 = time.time()
    try:
        r = subprocess.run([E_BIN, '--auto', '--proof-object', '--print-statistics', '-s',
                            f'--processed-clauses-limit={processed_limit}', f'--cpu-limit={cpu_limit}', *extra, path],
                           capture_output=True, text=True, timeout=cpu_limit + 30)
        out = r.stdout
    except subprocess.TimeoutExpired:
        return {'status': 'unknown', 'reason': 'wall timeout', 'secs': round(time.time() - t0, 2)}
    finally:
        os.unlink(path)
    m = re.search(r'SZS status (\w+)', out)
    szs = m.group(1) if m else 'None'
    status = {'Theorem': 'proved', 'CounterSatisfiable': 'countersatisfiable'}.get(szs, 'unknown')
    if szs == 'None' and r.returncode not in (0, 1, 6, 7): status = 'error'
    pm = re.search(r'# Processed clauses\s*:\s*(\d+)', out)
    return {'status': status, 'szs': szs, 'proof_steps': _proof_steps(out) if status == 'proved' else None,
            'processed': int(pm.group(1)) if pm else None, 'secs': round(time.time() - t0, 2), 'rc': r.returncode}


V_BIN = os.environ.get('SOUP_VAMPIRE', 'vampire')


def prove_vampire(T, goal, cpu_limit=60, extra=('-sa', 'discount')):
    """Vampire with one fixed saturation algorithm (not the time-sliced portfolio), for cross-checks."""
    with tempfile.NamedTemporaryFile('w', suffix='.p', delete=False) as fh:
        fh.write(problem(T, goal)); path = fh.name
    t0 = time.time()
    try:
        r = subprocess.run([V_BIN, *extra, '-t', str(cpu_limit), path], capture_output=True, text=True,
                           timeout=cpu_limit + 30)
        out = r.stdout
    except subprocess.TimeoutExpired:
        return {'status': 'unknown', 'reason': 'wall timeout'}
    finally:
        os.unlink(path)
    m = re.search(r'SZS status (\w+)', out)
    szs = m.group(1) if m else ('Theorem' if 'Refutation found' in out else 'None')
    status = {'Theorem': 'proved', 'CounterSatisfiable': 'countersatisfiable', 'Satisfiable': 'countersatisfiable'}.get(szs, 'unknown')
    return {'status': status, 'szs': szs, 'secs': round(time.time() - t0, 2)}
