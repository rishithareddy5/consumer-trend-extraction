#!/usr/bin/env python3
"""Remove debug UI (RAW MODEL / PARSED SPEC info boxes and the yellow fallback
warning) so the demo is clean. Validates syntax, backs up."""
import ast, shutil, sys
UI = "view/ui.py"
with open(UI) as f:
    src = f.read()

# 1. Remove the spec debug info lines
dbg = '''            import streamlit as _stdbg
            _stdbg.info("RAW MODEL: " + raw)
            spec = _validate_spec(_parse_spec(raw))
            _stdbg.info("PARSED SPEC: " + repr(spec))
            out = _run_spec(df, spec)'''
clean_dbg = '''            spec = _validate_spec(_parse_spec(raw))
            out = _run_spec(df, spec)'''

# 2. Quiet the yellow fallback warning (keep the fallback, just no visible warning)
warn = '''        except Exception as _e:
            import streamlit as _st
            _st.warning("text-to-pandas failed, using rule-based. Reason: " + repr(_e))
            return _run_analytics_rulebased(query)'''
clean_warn = '''        except Exception:
            return _run_analytics_rulebased(query)'''

changed = 0
if dbg in src:
    src = src.replace(dbg, clean_dbg); changed += 1
if warn in src:
    src = src.replace(warn, clean_warn); changed += 1

if changed == 0:
    print("NOTE: nothing to clean (already clean?). No changes.")
    sys.exit(0)

try:
    ast.parse(src)
except SyntaxError as e:
    print("ERROR: syntax error:", e); sys.exit(1)
shutil.copy(UI, UI + ".precleanup")
with open(UI, "w") as f:
    f.write(src)
print(f"SUCCESS: removed {changed} debug block(s). Backup: view/ui.py.precleanup")
