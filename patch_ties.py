#!/usr/bin/env python3
"""Make Key Findings honest about ties. When 2+ trends share the top count,
say they are tied instead of naming just one. Validates syntax, backs up."""
import ast, shutil, sys
UI = "view/ui.py"
with open(UI) as f:
    src = f.read()

old = '''            top_trend = filtered["trend_label"].value_counts().head(1)
            if len(top_trend):
                tname = top_trend.index[0].replace("_", " ")
                result["insight"] = ("Across <b>" + str(n) + "</b> records, the dominant trend is <b>"
                                     + tname + "</b> (" + str(int(top_trend.iloc[0])) + " records)."
                                     + "<br><br><b>OEM Recommendation:</b> prioritise <b>" + tname
                                     + "</b> initiatives for this segment.")'''

new = '''            _vc = filtered["trend_label"].value_counts()
            if len(_vc):
                _topn = int(_vc.iloc[0])
                _tied = [t for t in _vc.index if int(_vc[t]) == _topn]
                if len(_tied) == 1:
                    tname = _tied[0].replace("_", " ")
                    result["insight"] = ("Across <b>" + str(n) + "</b> records, the dominant trend is <b>"
                                         + tname + "</b> (" + str(_topn) + " records)."
                                         + "<br><br><b>OEM Recommendation:</b> prioritise <b>" + tname
                                         + "</b> initiatives for this segment.")
                else:
                    _names = [t.replace("_", " ") for t in _tied]
                    if len(_names) == 2:
                        _joined = "<b>" + _names[0] + "</b> and <b>" + _names[1] + "</b>"
                    else:
                        _joined = ("<b>" + "</b>, <b>".join(_names[:-1]) + "</b> and <b>"
                                   + _names[-1] + "</b>")
                    result["insight"] = ("Across <b>" + str(n) + "</b> records, "
                                         + str(len(_tied)) + " trends are tied at the top \\u2014 "
                                         + _joined + ", each with <b>" + str(_topn) + "</b> records. "
                                         + "No single trend dominates this segment."
                                         + "<br><br><b>OEM Recommendation:</b> monitor these "
                                         + str(len(_tied)) + " trends together, as demand is evenly spread.")'''

if old not in src:
    print("ERROR: dominant-trend block not found. No changes.")
    sys.exit(1)
src = src.replace(old, new)

try:
    ast.parse(src)
except SyntaxError as e:
    print("ERROR: syntax error:", e); sys.exit(1)
shutil.copy(UI, UI + ".preties")
with open(UI, "w") as f:
    f.write(src)
print("SUCCESS: Key Findings now reports ties honestly. Backup: view/ui.py.preties")
