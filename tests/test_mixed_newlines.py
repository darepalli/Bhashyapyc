# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bhashyapyc import compile_to_python
from tests.conftest import run_python_source

SRC = (
    'विधि ग(x):\r\n'
    '    प्रत्यावर्तय x\r\n\r'
    'print(ग(9))\n'
)

def test_mixed_newlines():
    py = compile_to_python(SRC, lang='sa')
    out, _ = run_python_source(py)
    assert out.strip() == '9'
