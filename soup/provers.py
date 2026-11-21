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


# Memory cap (MB) for every external prover: a prover that needs more stops with "resource out" (unknown)
# instead of being OOM-killed by the kernel and taking neighbours with it (21 Nov 2026: Vampire at 2-4.4 GB).
PROVER_MB = int(os.environ.get('SOUP_PROVER_MEMORY_MB', 2000))


def prove_e(T, goal, processed_limit=200_000, cpu_limit=300, extra=(), auto='--auto'):
    """auto: '--auto' (one strategy, deterministic; the pipeline default) or '--auto-schedule' (portfolio)."""
    src = problem(T, goal) if isinstance(goal, int) else goal
    with tempfile.NamedTemporaryFile('w', suffix='.p', delete=False) as fh:
        fh.write(src); path = fh.name
    t0 = time.time()
    try:
        r = subprocess.run([E_BIN, auto, '--proof-object', '--print-statistics', '-s', f'--memory-limit={PROVER_MB}',
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
    if szs == 'None' and r.returncode not in (0, 1, 6, 7, 8): status = 'error'   # 8 = resource out
    pm = re.search(r'# Processed clauses\s*:\s*(\d+)', out)
    return {'status': status, 'szs': szs, 'proof_steps': _proof_steps(out) if status == 'proved' else None,
            'processed': int(pm.group(1)) if pm else None, 'secs': round(time.time() - t0, 2), 'rc': r.returncode}


V_BIN = os.environ.get('SOUP_VAMPIRE', 'vampire')


def parse_vampire_model(out):
    """The finite model of a Vampire run (finite model building), as tables {'n', 'f', 'g'} over 0..n-1
    ('g' is None for one-operation problems); None if the output has no complete FiniteModel block."""
    m = re.search(r'SZS output start FiniteModel(.*?)SZS output end FiniteModel', out, re.S)
    if not m: return None
    blk = m.group(1)
    n = len(set(re.findall(r"'fmb_\$i_(\d+)'", blk)))
    if n == 0: return None
    tabs = {}
    for op, a, b, c in re.findall(r"\b([fg])\('fmb_\$i_(\d+)','fmb_\$i_(\d+)'\) = 'fmb_\$i_(\d+)'", blk):
        tabs.setdefault(op, [[None] * n for _ in range(n)])[int(a) - 1][int(b) - 1] = int(c) - 1
    if not tabs or any(v is None for t in tabs.values() for r in t for v in r): return None
    return {'n': n, 'f': tabs.get('f'), 'g': tabs.get('g')}


def prove_vampire(T, goal, cpu_limit=60, extra=('-sa', 'discount'), keep_output=False):
    """Vampire with one fixed saturation algorithm (not the time-sliced portfolio), for cross-checks.
    extra=('--mode', 'casc') or ('--mode', 'portfolio', '--schedule', 'casc_sat') selects a portfolio (this build has
    no '--mode casc_sat'). goal: law index or a TPTP string. A finite model, if Vampire prints one, is returned
    parsed ('model'); keep_output=True also returns the full output whenever the status is not 'unknown'."""
    with tempfile.NamedTemporaryFile('w', suffix='.p', delete=False) as fh:
        fh.write(problem(T, goal) if isinstance(goal, int) else goal); path = fh.name
    t0 = time.time()
    try:
        r = subprocess.run([V_BIN, *extra, '-m', str(PROVER_MB), '-t', str(cpu_limit), path], capture_output=True, text=True,
                           timeout=cpu_limit + 30)
        out = r.stdout
    except subprocess.TimeoutExpired:
        return {'status': 'unknown', 'reason': 'wall timeout'}
    finally:
        os.unlink(path)
    m = re.search(r'SZS status (\w+)', out)
    szs = m.group(1) if m else ('Theorem' if 'Refutation found' in out else 'None')
    status = {'Theorem': 'proved', 'CounterSatisfiable': 'countersatisfiable', 'Satisfiable': 'countersatisfiable'}.get(szs, 'unknown')
    res = {'status': status, 'szs': szs, 'secs': round(time.time() - t0, 2)}
    model = parse_vampire_model(out) if status == 'countersatisfiable' else None
    if model: res['model'] = model
    if keep_output and status != 'unknown': res['output'] = out
    return res


T_BIN = os.environ.get('SOUP_TWEE', 'twee')


def prove_twee(T, goal, seconds=60):
    """Twee 2.7.1 (unit equality, completion). Wall-time limit; heap capped through the GHC RTS (the binary
    is linked with -rtsopts). proof_steps: rewrite steps ("by ...") in Twee's human-readable proof."""
    with tempfile.NamedTemporaryFile('w', suffix='.p', delete=False) as fh:
        fh.write(problem(T, goal) if isinstance(goal, int) else goal); path = fh.name
    t0 = time.time()
    try:
        r = subprocess.run([T_BIN, path, '+RTS', f'-M{PROVER_MB}m', '-RTS'], capture_output=True, text=True,
                           timeout=seconds)
        out = r.stdout
    except subprocess.TimeoutExpired:
        return {'status': 'unknown', 'reason': 'wall timeout', 'secs': round(time.time() - t0, 2)}
    finally:
        os.unlink(path)
    m = re.search(r'SZS status (\w+)', out) or re.search(r'RESULT: (\w+)', out)
    szs = m.group(1) if m else 'None'
    status = {'Theorem': 'proved', 'Unsatisfiable': 'proved', 'CounterSatisfiable': 'countersatisfiable',
              'Satisfiable': 'countersatisfiable'}.get(szs, 'unknown')
    steps = len(re.findall(r'\{ by ', out)) if status == 'proved' else None
    return {'status': status, 'szs': szs, 'proof_steps': steps, 'secs': round(time.time() - t0, 2), 'rc': r.returncode,
            'proof': out[out.find('Proof:'):] if status == 'proved' and 'Proof:' in out else None}


# ---- Prover9 / Mace4 (LADR). Laws as f(x,y), g(x,y); u..z are variables in LADR syntax.
from .data import TREES as _TREES


def _ladr(t): return 'xyzwuv'[t[1]] if t[0] == 'v' else f"{'f' if t[0] == 'f' else 'g'}({_ladr(t[1])},{_ladr(t[2])})"


def ladr_input(T, goal=None, extra='', extra_axioms=()):
    """T: law indices; extra_axioms: further equations as (lhs, rhs) trees (e.g. lemmas beyond order 4)."""
    ax = '\n'.join([f'{_ladr(_TREES[t][0])} = {_ladr(_TREES[t][1])}.' for t in T] +
                   [f'{_ladr(l)} = {_ladr(r)}.' for l, r in extra_axioms])
    g = f'{_ladr(_TREES[goal][0])} = {_ladr(_TREES[goal][1])}.' if goal is not None else ''
    return f'{extra}\nformulas(assumptions).\n{ax}\nend_of_list.\nformulas(goals).\n{g}\nend_of_list.\n'


def prove_prover9(T, goal, seconds=60, extra_axioms=(), max_weight=None):
    """An empty set of support is a saturation only if no clause was thrown away: Prover9 deletes clauses
    over max_weight (default 100) and counts them as Deleted_by_rule; sos_limit deletions likewise. Until
    21 Nov 2026 (evening) any sos_empty was reported as countersatisfiable, which is unsound."""
    t0 = time.time()
    opts = f'assign(max_seconds, {seconds}).\nassign(max_megs, {PROVER_MB}).'
    if max_weight is not None: opts += f'\nassign(max_weight, {max_weight}).'
    r = subprocess.run(['prover9'], input=ladr_input(T, goal, opts, extra_axioms),
                       capture_output=True, text=True, timeout=seconds + 30)
    m = re.search(r'Length of proof: (\d+)', r.stdout)
    last = lambda k: int((re.findall(rf'{k}=(\d+)', r.stdout) or ['-1'])[-1])   # final statistics block
    deleted = {k: last(k) for k in ('Deleted_by_rule', 'Sos_limit_deleted')}
    complete = 'sos_empty' in r.stdout and all(v == 0 for v in deleted.values())
    st = 'proved' if 'THEOREM PROVED' in r.stdout else ('countersatisfiable' if complete else 'unknown')
    reason = f'sos_empty after deletions {deleted} (incomplete)' if st == 'unknown' and 'sos_empty' in r.stdout else None
    return {'status': st, 'proof_length': int(m.group(1)) if m else None, 'secs': round(time.time() - t0, 2),
            'deleted': deleted, 'reason': reason}


def mace4(T, goal=None, start=2, end=10, seconds=600):
    """Smallest model of T (violating goal if given) with start <= size <= end. Returns size or None, and secs."""
    t0 = time.time()
    r = subprocess.run(['mace4', '-n', str(start), '-N', str(end), '-t', str(seconds), '-b', str(PROVER_MB)],
                       input=ladr_input(T, goal), capture_output=True, text=True, timeout=seconds + 60)
    m = re.search(r'interpretation\( (\d+),', r.stdout)
    sizes = [int(x) for x in re.findall(r'DOMAIN SIZE (\d+)', r.stdout)]
    exhausted = 'exit (exhausted)' in r.stdout or 'exhausted' in r.stdout.split('Exiting with')[-1]
    # sizes completely searched without a model: all started sizes, minus the last one unless the search exhausted
    done_to = (max(sizes) if exhausted else max(sizes) - 1) if sizes and not m else None
    tables = None
    if m:
        n = int(m.group(1)); tables = []
        for op in ('f', 'g'):
            t = re.search(op + r'\(_,_\), \[([\d,\s]+)\]', r.stdout)
            vals = [int(v) for v in t.group(1).replace(',', ' ').split()] if t else [0] * (n * n)
            tables.append([vals[i * n:(i + 1) * n] for i in range(n)])
    return {'size': int(m.group(1)) if m else None, 'tables': tables, 'searched_to': done_to, 'exhausted_to': end if exhausted else None,
            'reason': (re.findall(r'Exiting with (.*)\.', r.stdout) or ['?'])[-1], 'secs': round(time.time() - t0, 1)}
