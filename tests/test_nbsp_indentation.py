# -*- coding: utf-8 -*-
import sys, pytest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bhashyapyc import compile_to_python

NBSP = '\u00A0'

SRC = (
    'విధి ఎ( ):\n'
    f'{NBSP}{NBSP}{NBSP}{NBSP}ముద్రించు("x")\n'
)

def test_nbsp_indent_rejected():
    with pytest.raises(SyntaxError):
        compile_to_python(SRC, lang='te')
