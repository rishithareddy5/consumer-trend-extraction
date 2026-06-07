#!/usr/bin/env python3
"""Safely appends the /generate endpoint to controller/api.py.
Validates syntax before writing. Backs up first."""
import ast, shutil, sys

API = "controller/api.py"
CODE = "generate_endpoint_code.py"

with open(API) as f:
    src = f.read()
with open(CODE) as f:
    add = f.read()

if "/generate" in src:
    print("NOTE: '/generate' already present in api.py — nothing to add.")
    sys.exit(0)

patched = src.rstrip("\n") + "\n" + add

try:
    ast.parse(patched)
except SyntaxError as e:
    print("ERROR: patched api.py has a syntax error:", e)
    print("Aborting — no changes made.")
    sys.exit(1)

shutil.copy(API, API + ".prepatch")
with open(API, "w") as f:
    f.write(patched)

print("SUCCESS: /generate endpoint added to controller/api.py and syntax-valid.")
print("Backup saved as controller/api.py.prepatch")
