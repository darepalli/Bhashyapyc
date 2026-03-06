# -*- coding: utf-8 -*-
import sys, unicodedata, pytest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bhashyapyc import compile_to_python
from tests.conftest import run_python_source

# Sanskrit 'यदि' in NFC and NFD
SANS_IF_NFC = 'यदि'
SANS_IF_NFD = unicodedata.normalize('NFD', SANS_IF_NFC)

# Telugu 'విధి' in NFC and NFD
TEL_DEF_NFC = 'విధి'
TEL_DEF_NFD = unicodedata.normalize('NFD', TEL_DEF_NFC)


def test_sanskrit_if_nfc_works():
    src = f"{SANS_IF_NFC} True:\n    print(1)\n"
    py = compile_to_python(src, lang='sa')
    out, _ = run_python_source(py)
    assert out.strip() == '1'

@pytest.mark.xfail(reason='NFD decomposition not yet normalized by parser')
def test_sanskrit_if_nfd_xfail():
    src = f"{SANS_IF_NFD} True:\n    print(1)\n"
    py = compile_to_python(src, lang='sa')
    out, _ = run_python_source(py)
    assert out.strip() == '1'


def test_telugu_def_nfc_works():
    src = f"{TEL_DEF_NFC} ఫ(ఎన్):\n    తిరిగి ఎన్\n\nprint(ఫ(3))\n"
    py = compile_to_python(src, lang='te')
    out, _ = run_python_source(py)
    assert out.strip() == '3'

@pytest.mark.xfail(reason='NFD decomposition not yet normalized by parser')
def test_telugu_def_nfd_xfail():
    src = f"{TEL_DEF_NFD} ఫ(ఎన్):\n    తిరిగి ఎన్\n\nprint(ఫ(3))\n"
    py = compile_to_python(src, lang='te')
    out, _ = run_python_source(py)
    assert out.strip() == '3'
