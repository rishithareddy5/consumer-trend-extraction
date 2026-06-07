#!/usr/bin/env python3
"""Make all hero badges the same blue by removing the 'green'/'yellow'
modifier classes from the last two badges. Validates syntax, backs up."""
import ast, shutil, sys
UI = "view/ui.py"
with open(UI) as f:
    src = f.read()

changes = 0
# 16 Trend Labels badge: green -> plain blue
a1 = '<span class="badge green">16 Trend Labels</span>'
b1 = '<span class="badge">16 Trend Labels</span>'
if a1 in src:
    src = src.replace(a1, b1); changes += 1

# Accuracy badge: yellow -> plain blue (handle the exact text present)
import re
# match the yellow accuracy badge regardless of the exact % text
pat = re.compile(r'<span class="badge yellow">([^<]*Accuracy[^<]*)</span>')
m = pat.search(src)
if m:
    src = pat.sub(r'<span class="badge">\1</span>', src, count=1); changes += 1

if changes == 0:
    print("NOTE: no green/yellow badges found (maybe already uniform). No changes.")
    sys.exit(0)

try:
    ast.parse(src)
except SyntaxError as e:
    print("ERROR: syntax error:", e); sys.exit(1)
shutil.copy(UI, UI + ".prebadges")
with open(UI, "w") as f:
    f.write(src)
print(f"SUCCESS: {changes} badge(s) set to blue. Backup: view/ui.py.prebadges")
