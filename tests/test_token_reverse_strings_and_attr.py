# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bhashyapyc import reverse_translate_python

def test_token_reverse_keeps_strings_and_attr_te():
    py = 's = "if True"\nmodule.print("x")\nprint("ok")\n'
    te = reverse_translate_python(py, lang='te')
    # string literal should contain 'if True' unchanged
    assert '"if True"' in te
    # attribute access 'module.print' must remain 'print' (not Telugu token)
    assert 'module.print' in te
    # bare print must translate
    assert 'ముద్రించు("ok")' in te
