# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bhashyapyc import compile_to_python
from .conftest import run_python_source

SANS_FIB = (
    'विधि फिबो(एन):\n'
    '    यदि एन <= 1:\n'
    '        प्रत्यावर्तय एन\n'
    '    अन्यथा:\n'
    '        प्रत्यावर्तय फिबो(एन-1) + फिबो(एन-2)\n\n'
    'फल = फिबो(10)\n'
    'print(फल)\n'
)

def test_sanskrit_forward_and_execute():
    py = compile_to_python(SANS_FIB, lang='sa')
    out, g = run_python_source(py)
    assert 'def' in py
    assert out.strip() == '55'
