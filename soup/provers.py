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


# ---- Prover9 / Mace4 (LADR). Laws as f(x,y), g(x,y); u..z are variables in LADR syntax.
from .data import TREES as _TREES


def _ladr(t): return 'xyzwuv'[t[1]] if t[0] == 'v' else f"{'f' if t[0] == 'f' else 'g'}({_ladr(t[1])},{_ladr(t[2])})"


def ladr_input(T, goal=None, extra=''):
    ax = '\n'.join(f'{_ladr(_TREES[t][0])} = {_ladr(_TREES[t][1])}.' for t in T)
    g = f'{_ladr(_TREES[goal][0])} = {_ladr(_TREES[goal][1])}.' if goal is not None else ''
    return f'{extra}\nformulas(assumptions).\n{ax}\nend_of_list.\nformulas(goals).\n{g}\nend_of_list.\n'


def prove_prover9(T, goal, seconds=60):
    t0 = time.time()
    r = subprocess.run(['prover9'], input=ladr_input(T, goal, f'assign(max_seconds, {seconds}).'),
                       capture_output=True, text=True, timeout=seconds + 30)
    m = re.search(r'Length of proof: (\d+)', r.stdout)
    st = 'proved' if 'THEOREM PROVED' in r.stdout else ('countersatisfiable' if 'SEARCH FAILED' in r.stdout and 'sos_empty' in r.stdout else 'unknown')
    return {'status': st, 'proof_length': int(m.group(1)) if m else None, 'secs': round(time.time() - t0, 2)}


def mace4(T, goal=None, start=2, end=10, seconds=600):
    """Smallest model of T (violating goal if given) with start <= size <= end. Returns size or None, and secs."""
    t0 = time.time()
    r = subprocess.run(['mace4', '-n', str(start), '-N', str(end), '-t', str(seconds)],
                       input=ladr_input(T, goal), capture_output=True, text=True, timeout=seconds + 60)
    m = re.search(r'interpretation\( (\d+),', r.stdout)
    return {'size': int(m.group(1)) if m else None, 'exhausted_to': end if 'exit (exhausted)' in r.stdout else None,
            'reason': (re.findall(r'Exiting with (.*)\.', r.stdout) or ['?'])[-1], 'secs': round(time.time() - t0, 1)}
