"""Human-readable outputs: journal/journal.md (append-only narrative) and journal/leaderboard.md (rewritten)."""
import os
import time
from pathlib import Path

from ..paths import data, ensure


def hm(t=None): return time.strftime('%H:%M:%S', time.localtime(t or time.time()))
def ymd_hm(t=None): return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t or time.time()))


class Journal:
    def __init__(self):
        ensure('journal'); self.path = data('journal', 'journal.md')
        if not self.path.exists(): self.path.write_text('# soup journal\n\nAppend-only. One section per run; times are UTC (container clock).\n')

    def write(self, text):
        with open(self.path, 'a') as fh: fh.write(text if text.endswith('\n') else text + '\n'); fh.flush()


def claims_text(r):
    parts = []
    for c in r.get('claims', []):
        st = c['status']
        if st == 'proved': parts.append(f"{c['law']} proved (effort {c['effort']:,}{', stage c' if c.get('proved_in') == 'c' else ''})")
        elif st.startswith('false'): parts.append(f"{c['law']} {st}")
        elif st == 'open': parts.append(f"{c['law']} OPEN ({c.get('budget', '')})")
        else: parts.append(f"{c['law']} {st}")
    return '; '.join(parts) or 'none'


def models_text(r):
    mc = r.get('model_counts', {})
    return '/'.join(str(mc.get(str(n), mc.get(n, 0))) for n in (2, 3, 4, 5))


def result_line(r):
    du = ','.join(r.get('dualities', [])) or '-'
    s = (f"- {hm(r.get('t_done'))} · `{r['key'][:8]}` stage {r.get('stage')} · score **{r.get('score', 0):.3f}** "
         f"(cheap {r.get('cheap') or 0:.3f}) · {du} · {r.get('arm')} · models 2/3/4/5 = {models_text(r)} · "
         f"{r.get('verifier')} in {sum((r.get('secs') or {}).values()):.0f}s\n"
         f"  - laws: {' & '.join(r['laws'])}\n"
         f"  - claims: {claims_text(r)}")
    if r.get('redundant'): s += f"\n  - redundant (proved from the others): {'; '.join(r['redundant'])}"
    if r.get('status') and r['status'] != 'ok': s += f"\n  - {r['status']}"
    return s


def leaderboard(results, top=30, header=''):
    rs = sorted((r for r in results if r.get('score', 0) > 0), key=lambda r: -r['score'])
    n_open = sum(1 for r in results if any(c['status'] in ('unknown', 'open') for c in r.get('claims', [])))
    lines = [f'# soup leaderboard', '', f'Updated {ymd_hm()}. {header}',
             f'{len(results)} verified theories, {len(rs)} with positive score, {n_open} with open claims. '
             'Score = verified score (stages a/b, c when run); difficulty from z3 effort (z3-solver 5.4.1.0).', '',
             '| # | score | key | arm | dualities | laws | proved emergent | refuted | open | models 2/3/4/5 | stage |',
             '|---|---|---|---|---|---|---|---|---|---|---|']
    for i, r in enumerate(rs[:top], 1):
        cl = r.get('claims', [])
        proved = '; '.join(f"{c['law']} ({c['difficulty']:.2f})" for c in cl if c['status'] == 'proved')
        lines.append(f"| {i} | {r['score']:.3f} | `{r['key'][:8]}` | {r.get('arm')} | {','.join(r.get('dualities', [])) or '-'} | "
                     f"{' & '.join(r['laws'])} | {proved} | {sum(c['status'].startswith('false') for c in cl)} | "
                     f"{sum(c['status'] in ('unknown', 'open') for c in cl)} | {models_text(r)} | {r.get('stage')} |")
    lines.append('')
    p = data('journal', 'leaderboard.md'); tmp = p.with_name('.leaderboard.tmp')
    tmp.write_text('\n'.join(lines)); os.replace(tmp, p)
