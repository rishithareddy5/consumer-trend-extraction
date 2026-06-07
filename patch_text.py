#!/usr/bin/env python3
"""Update the stale 'routes intelligently' helper text to match the new
two-mode (Classify / Analytics) design. Validates syntax, backs up."""
import ast, shutil, sys
UI = "view/ui.py"
with open(UI) as f:
    src = f.read()

old = "Type a retailer note OR an analytics question. The system routes intelligently."
new = "Choose a mode above, then type below \u2014 Classify a single note, or ask an Analytics question about the data."

if old not in src:
    print("NOTE: the old helper text was not found (maybe already changed). No changes.")
    sys.exit(0)

src = src.replace(old, new)
try:
    ast.parse(src)
except SyntaxError as e:
    print("ERROR: syntax error:", e); sys.exit(1)
shutil.copy(UI, UI + ".pretext")
with open(UI, "w") as f:
    f.write(src)
print("SUCCESS: helper text updated. Backup: view/ui.py.pretext")
