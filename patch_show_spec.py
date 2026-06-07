#!/usr/bin/env python3
"""Temporarily show the raw model output + parsed spec in the UI, so we can see
exactly what the live flow produces."""
import ast, shutil, sys
UI = "view/ui.py"
with open(UI) as f:
    src = f.read()

# Insert a st.info right after we get raw + spec, before _run_spec
anchor = '''            raw = r.json()["text"]
            spec = _validate_spec(_parse_spec(raw))
            out = _run_spec(df, spec)'''

new = '''            raw = r.json()["text"]
            import streamlit as _stdbg
            _stdbg.info("RAW MODEL: " + raw)
            spec = _validate_spec(_parse_spec(raw))
            _stdbg.info("PARSED SPEC: " + repr(spec))
            out = _run_spec(df, spec)'''

if anchor not in src:
    print("ERROR: anchor not found. No changes.")
    sys.exit(1)
patched = src.replace(anchor, new)
try:
    ast.parse(patched)
except SyntaxError as e:
    print("ERROR:", e); sys.exit(1)
shutil.copy(UI, UI + ".preshowspec")
with open(UI, "w") as f:
    f.write(patched)
print("SUCCESS: spec debug added. Backup: view/ui.py.preshowspec")
