# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bhashyapyc import compile_to_python
from bhashyapyc.reverse_ast import reverse_translate_python_ast
from .conftest import run_python_source

PY_SRC = (
    'def sumsq(n):\n'
    '    s = 0\n'
    '    for i in range(n+1):\n'
    '        if i % 2 == 0:\n'
    '            s = s + i*i\n'
    '    return s\n\n'
    'print(sumsq(10))\n'
)

def _roundtrip(lang):
    # 1) Original Python executes
    out_py, _ = run_python_source(PY_SRC)
    # 2) Reverse AST to target (Telugu or Sanskrit)
    tgt_src, smap = reverse_translate_python_ast(PY_SRC, lang=lang, source_name='sumsq.py')
    assert smap['language'] == lang
    # 3) Forward compile target → Python
    py2 = compile_to_python(tgt_src, lang=lang)
    # 4) Execute compiled Python and compare outputs
    out_round, _ = run_python_source(py2)
    assert out_round.strip() == out_py.strip()


def test_roundtrip_sanskrit_ast():
    _roundtrip('sa')

def test_roundtrip_telugu_ast():
    _roundtrip('te')
