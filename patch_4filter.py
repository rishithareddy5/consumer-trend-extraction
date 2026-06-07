#!/usr/bin/env python3
"""Add a 4-filter example (with season) to _spec_prompt so the model learns
to capture all filters including season on long queries. Validates, backs up."""
import ast, shutil, sys
UI = "view/ui.py"
with open(UI) as f:
    src = f.read()

# Anchor on the sugar-free + winter example we know exists in the leaner prompt.
anchor = '''                "Q: sugar free demand in winter\\n"
                'A: {"filters": {"trend_label": "sugar_free_demand", "season": "Winter"}, "group_by": "city", "operation": "count", "target": "trend_label"}\\n'
'''
if anchor not in src:
    print("ERROR: sugar-free/winter prompt example not found. No changes.")
    sys.exit(1)

add = anchor + '''                "Q: sugar free demand among senior citizens in kirana stores in winter\\n"
                'A: {"filters": {"trend_label": "sugar_free_demand", "consumer_demographic": "senior citizens", "store_type": "Kirana Store", "season": "Winter"}, "group_by": "city", "operation": "count", "target": "trend_label"}\\n'
                "Q: protein snacks among teenagers in supermarkets in summer\\n"
                'A: {"filters": {"trend_label": "protein_snack_trend", "consumer_demographic": "teenagers", "store_type": "Supermarket", "season": "Summer"}, "group_by": "city", "operation": "count", "target": "trend_label"}\\n'
'''
src = src.replace(anchor, add)

try:
    ast.parse(src)
except SyntaxError as e:
    print("ERROR: syntax error:", e); sys.exit(1)
shutil.copy(UI, UI + ".pre4filter")
with open(UI, "w") as f:
    f.write(src)
print("SUCCESS: added two 4-filter examples (with season). Backup: view/ui.py.pre4filter")
