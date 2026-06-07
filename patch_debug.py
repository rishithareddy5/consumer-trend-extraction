#!/usr/bin/env python3
"""Temporarily expose the analytics fallback error so we can see WHY it falls back.
Replaces the bare 'except Exception:' in the NEW _run_analytics with one that
shows the error in the Streamlit UI. Safe: validates syntax, backs up."""
import ast, shutil, sys

UI = "view/ui.py"
with open(UI) as f:
    src = f.read()

# The new _run_analytics ends with this exact fallback:
old = '''        except Exception:
            return _run_analytics_rulebased(query)'''

new = '''        except Exception as _e:
            import streamlit as _st
            _st.warning("text-to-pandas failed, using rule-based. Reason: " + repr(_e))
            return _run_analytics_rulebased(query)'''

if old not in src:
    print("ERROR: could not find the fallback block. No changes made.")
    sys.exit(1)

if src.count(old) != 1:
    print("ERROR: found", src.count(old), "matches, expected 1. No changes made.")
    sys.exit(1)

patched = src.replace(old, new)
try:
    ast.parse(patched)
except SyntaxError as e:
    print("ERROR: syntax error:", e); sys.exit(1)

shutil.copy(UI, UI + ".predebug")
with open(UI, "w") as f:
    f.write(patched)
print("SUCCESS: debug logging added. Backup: view/ui.py.predebug")
