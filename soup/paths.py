"""Where data lives. Code never hardcodes a path: everything is relative to SOUP_DATA."""
import os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = Path(os.environ.get('SOUP_DATA', REPO / 'work')).resolve()


def data(*parts):
    return DATA.joinpath(*parts)


def ensure(*parts):
    p = data(*parts)
    p.mkdir(parents=True, exist_ok=True)
    return p
