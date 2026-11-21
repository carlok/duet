"""Summary of the verified theories in SOUP_DATA/results (the streaming search).  python -m soup.report
Calibration has its own report: python -m soup.calib_report. Output is kept as work/report.txt."""
import glob
import json
from collections import Counter

from .paths import data


def main():
    rs = [json.load(open(f)) for f in sorted(glob.glob(str(data('results', '*.json'))))]
    rs.sort(key=lambda r: -(r.get('score') or 0))
    claims = [c for r in rs for c in r.get('claims', [])]
    st = Counter('proved' if c['status'] == 'proved' else 'refuted' if c['status'].startswith('false')
                 else 'open' for c in claims)
    print(f'{len(rs)} verified theories ({sum((r.get("score") or 0) > 0 for r in rs)} positive score), '
          f'stages {dict(Counter(r.get("stage") for r in rs))}, arms {dict(Counter(r.get("arm") for r in rs))}')
    print(f'with a duality: {sum(bool(r.get("dualities")) for r in rs)}; claims: {dict(st)}; '
          f'E saturations certified / uncertified: {sum(c.get("certificate") is True for c in claims)} / '
          f'{sum(c.get("certificate") is False for c in claims)}; z3-unproved (E only): {sum(bool(c.get("z3_unproved")) for c in claims)}')
    print('\nTOP 15')
    for r in rs[:15]:
        cl = '; '.join(f"{c['law']} {c['status']}" for c in r.get('claims', []))
        print(f"  {r.get('score') or 0:.3f} {','.join(r.get('dualities', [])) or '-':14s} {' & '.join(r['laws'])}\n        {cl}")
    opens = [r for r in rs if any(c['status'] in ('unknown', 'open') for c in r.get('claims', []))]
    print(f'\nOPEN CLAIMS: {len(opens)} theories')
    for r in opens[:30]:
        print('  ', r['key'][:8], ' & '.join(r['laws']), '==>',
              '; '.join(c['law'] for c in r['claims'] if c['status'] in ('unknown', 'open')))


if __name__ == '__main__':
    main()
