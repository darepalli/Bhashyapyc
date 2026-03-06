# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bhashyapyc.reverse_ast import reverse_translate_python_ast
from bhashyapyc import compile_to_python
from .conftest import run_python_source

PY = 'print("యెడల")\n'

def test_string_with_target_keyword_roundtrip_telugu():
    tgt, _ = reverse_translate_python_ast(PY, lang='te', source_name='str.py')
    # Forward compile back
    py2 = compile_to_python(tgt, lang='te')
    out, _ = run_python_source(py2)
    assert out.strip() == 'యెడల'
