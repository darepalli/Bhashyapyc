# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bhashyapyc import compile_to_python
from .conftest import run_python_source

def test_empty_source():
    py = compile_to_python('', lang='sa')
    out, _ = run_python_source(py)
    assert out == ''

def test_comments_only():
    src = '# వ్యాఖ్య మాత్రమే\n# केवल टिप्पणी\n'
    py = compile_to_python(src, lang='te')
    out, _ = run_python_source(py)
    assert out == ''
