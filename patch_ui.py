#!/usr/bin/env python3
"""
Safely patches view/ui.py:
  - reads the file
  - finds the line:   def _run_analytics(query: str):   (indented inside tab_chat)
  - inserts the NEW _run_analytics block right BEFORE it
  - the NEW block ends with 'def _run_analytics_rulebased(query: str):' which
    seamlessly renames the existing function (the original body follows).
Result: new _run_analytics (text-to-pandas) + original renamed to _rulebased.
Validates syntax before writing.
"""
import sys, ast, shutil

UI = "view/ui.py"
BLOCK = "new_analytics_block.py"

with open(UI) as f:
    src = f.read()
with open(BLOCK) as f:
    new_block = f.read().rstrip("\n") + "\n"

# the target line we replace (original function def, 4-space indented)
target = "    def _run_analytics(query: str):\n"
if target not in src:
    print("ERROR: could not find the original 4-space-indented _run_analytics def.")
    print("Aborting — no changes made.")
    sys.exit(1)

if src.count(target) != 1:
    print("ERROR: found the target def", src.count(target), "times, expected exactly 1.")
    sys.exit(1)

# The new block already ENDS with 'def _run_analytics_rulebased(query: str):'
# so we replace the original 'def _run_analytics(query: str):' line with the
# whole new block (which terminates in the rulebased def line). The original
# body that followed now belongs to _run_analytics_rulebased.
patched = src.replace(target, new_block)

# validate
try:
    ast.parse(patched)
except SyntaxError as e:
    print("ERROR: patched file has a syntax error:", e)
    print("Aborting — no changes made.")
    sys.exit(1)

# backup current then write
shutil.copy(UI, UI + ".prepatch")
with open(UI, "w") as f:
    f.write(patched)

print("SUCCESS: view/ui.py patched and syntax-valid.")
print("Backup of pre-patch file saved as view/ui.py.prepatch")
