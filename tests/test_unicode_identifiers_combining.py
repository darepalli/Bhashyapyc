# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bhashyapyc import compile_to_python
from tests.conftest import run_python_source

# Telugu identifier with combining marks (matras)
SRC = (
    'విధి లేఖనం(సంఖ్యా):\n'
    '    తిరిగిపంపు సంఖ్యా\n\n'
    'print(లేఖనం(7))\n'
)

def test_telugu_identifier_with_combining_marks_executes():
    py = compile_to_python(SRC, lang='te')
    out, _ = run_python_source(py)
    assert out.strip() == '7'
