# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bhashyapyc import compile_to_python
from tests.conftest import run_python_source

BOM = '\ufeff'

SRC = BOM + (
    'विधि ए(न):\n'
    '    प्रत्यावर्तय न\n\n'
    'print(ए(4))\n'
)

def test_bom_prefix_sanskrit():
    py = compile_to_python(SRC, lang='sa')
    out, _ = run_python_source(py)
    assert out.strip() == '4'
