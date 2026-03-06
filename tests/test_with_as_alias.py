# -*- coding: utf-8 -*-
import sys, io
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bhashyapyc.reverse_ast import reverse_translate_python_ast
from bhashyapyc import compile_to_python
from .conftest import run_python_source

PY = (
    'def readfirst(p):\n'
    '    with open(p, "w") as f: pass\n'
    '    with open(p, "r") as f: return f.read()\n'
    'print(type(readfirst).__name__)\n'
)

def test_with_as_alias_roundtrip_telugu(tmp_path):
    p = tmp_path/"file.txt"
    # Create empty file; function will open and close
    p.write_text('', encoding='utf-8')
    tgt, _ = reverse_translate_python_ast(PY.replace('p)', f'"{p}" )'), lang='te', source_name='with.py')
    py2 = compile_to_python(tgt, lang='te')
    out, _ = run_python_source(py2)
    assert 'function' in out.strip()
