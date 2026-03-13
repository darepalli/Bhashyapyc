# Bhashyapyc

Project to support Python coding in Indian languages (Telugu & Sanskrit).

## VS Code Extension

Bhashyapyc is a VS Code extension that displays **bidirectional translations**
between Python and Indian languages as hover balloon popups.

### Features

- **Hover over Python code** → see the Telugu or Sanskrit translation in a popup
- **Hover over Telugu/Sanskrit code** → see the Python translation in a popup
- Supports **Telugu** (`.tepy` files) and **Sanskrit** (`.sapy` files)
- Configurable target language and Python interpreter path

### Prerequisites

- Python 3.11+ with the `bhashyapyc` package available (3.11+ required by CI; 3.9+ may work)
- Install the package: `pip install -e .` from this repository root

### Installation

1. Clone the repository
2. Run `npm install` and `npm run compile`
3. Open the folder in VS Code and press **F5** to launch the Extension Host

### Configuration

| Setting                       | Default   | Description                                      |
|-------------------------------|-----------|--------------------------------------------------|
| `bhashyapyc.pythonPath`       | `python3` | Path to the Python interpreter with bhashyapyc   |
| `bhashyapyc.targetLanguage`   | `te`      | Target language for reverse translation (`te`/`sa`) |

### Usage

- Open a `.py` file and hover over any line to see the Indian-language translation
- Open a `.tepy` or `.sapy` file and hover over any line to see the Python translation
- The popup shows the translated line highlighted with surrounding context

## Python Package

The core translation engine is a Python package under `bhashyapyc/`.  See
[`bhashyapyc/README.md`](bhashyapyc/README.md) for details on forward
compilation, reverse translation, and source maps.

### CLI Usage

```bash
# Forward: Telugu/Sanskrit → Python
python -m bhashyapyc example.tepy --emit-py out.py

# Reverse: Python → Telugu
python -m bhashyapyc example.py --reverse --lang te

# Reverse AST-aware: Python → Sanskrit with source map
python -m bhashyapyc example.py --reverse-ast --lang sa --emit-src out.sapy --emit-map out.json
```
