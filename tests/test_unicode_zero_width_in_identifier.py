# -*- coding: utf-8 -*-
import sys, pytest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bhashyapyc import compile_to_python
from tests.conftest import run_python_source

# Use ZERO WIDTH JOINER \u200D inside an identifier; Python identifiers disallow it → expect SyntaxError
SRC = (
    'విధి పేరు\u200D(ఎన్):\n'
    '    తిరిగి ఎన్\n\n'
    'print(పేరు\u200D(2))\n'
)

@pytest.mark.xfail(reason='Zero-width joiner not a valid identifier character in Python')
def test_zero_width_joiner_identifier_xfail():
    py = compile_to_python(SRC, lang='te')
    # execution likely fails at compile step
    out, _ = run_python_source(py)
    assert out.strip() == '2'
