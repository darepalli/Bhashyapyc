# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bhashyapyc.reverse_ast import reverse_translate_python_ast
from bhashyapyc import compile_to_python
from .conftest import run_python_source

PY = (
    'from math import sqrt as r\n'
    'def go(x):\n'
    '    return r(x)\n'
    'print(go(9))\n'
)

def test_from_import_alias_roundtrip_sanskrit():
    tgt, _ = reverse_translate_python_ast(PY, lang='sa', source_name='imp.py')
    py2 = compile_to_python(tgt, lang='sa')
    out, _ = run_python_source(py2)
    assert out.strip() == '3.0'
