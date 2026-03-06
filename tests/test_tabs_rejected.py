# -*- coding: utf-8 -*-
import sys, pytest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bhashyapyc import compile_to_python

def test_tabs_are_rejected_in_forward_parser():
    # Leading tab before 'print'
    src = 'విధి ఎ( ):\n\tముద్రించు("x")\n'
    with pytest.raises(SyntaxError):
        compile_to_python(src, lang='te')
