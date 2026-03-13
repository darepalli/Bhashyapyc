# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bhashyapyc import compile_to_python
from .conftest import run_python_source

TELUGU_FIB = (
    'విధి ఫిబో(ఎన్):\n'
    '    ఐతే ఎన్ <= 1:\n'
    '        తిరిగిపంపు ఎన్\n'
    '    లేకపోతే:\n'
    '        తిరిగిపంపు ఫిబో(ఎన్-1) + ఫిబో(ఎన్-2)\n\n'
    'ఫలితం = ఫిబో(10)\n'
    'print(ఫలితం)\n'
)

def test_telugu_forward_and_execute():
    py = compile_to_python(TELUGU_FIB, lang='te')
    out, g = run_python_source(py)
    assert 'def' in py
    assert out.strip() == '55'
