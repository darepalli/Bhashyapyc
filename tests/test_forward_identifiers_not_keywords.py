# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bhashyapyc import compile_to_python
from .conftest import run_python_source

def test_telugu_identifier_named_like_keyword_prefix():
    # Identifier that contains a keyword as substring should not be rewritten
    src = (
        'విధి యెడలఫంక్షన్(ఎన్):\n'
        '    తిరిగి ఎన్\n\n'
        'print(యెడలఫంక్షన్(5))\n'
    )
    py = compile_to_python(src, lang='te')
    out, _ = run_python_source(py)
    assert out.strip() == '5'
