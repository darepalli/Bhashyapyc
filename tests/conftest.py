# -*- coding: utf-8 -*-
import sys, io, types
from contextlib import redirect_stdout


def run_python_source(src: str):
    """Execute Python source in isolated globals and return (stdout, globals)."""
    g = {"__name__": "__main__"}
    buf = io.StringIO()
    with redirect_stdout(buf):
        exec(compile(src, '<compiled>', 'exec'), g, g)
    return buf.getvalue(), g
