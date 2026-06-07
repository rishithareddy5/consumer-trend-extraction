#!/usr/bin/env python3
"""Add column-alias mapping to the validator in the new _run_analytics block,
so the model writing 'product' maps to 'product_category', etc.
Safe: validates syntax, backs up."""
import ast, shutil, sys

UI = "view/ui.py"
with open(UI) as f:
    src = f.read()

# We insert an alias-normalization step at the start of _validate_spec.
# Anchor: the def line of _validate_spec inside the new block.
anchor = '''        def _validate_spec(spec):
            clean = {"filters": {}, "group_by": None, "operation": "count", "target": "trend_label"}'''

new = '''        def _validate_spec(spec):
            _aliases = {
                "product": "product_category", "category": "product_category",
                "products": "product_category", "item": "product_category",
                "demographic": "consumer_demographic", "demo": "consumer_demographic",
                "customer": "consumer_demographic", "audience": "consumer_demographic",
                "store": "store_type", "shop": "store_type", "outlet": "store_type",
                "rep": "salesperson_name", "salesperson": "salesperson_name",
                "retailer": "retailer_id", "trend": "trend_label",
                "signal": "trend_signal_type", "date": "visit_date",
            }
            # remap aliased filter keys to real column names
            _f = spec.get("filters") or {}
            _fixed = {}
            for _k, _v in _f.items():
                _fixed[_aliases.get(_k, _k)] = _v
            spec["filters"] = _fixed
            if spec.get("group_by") in _aliases:
                spec["group_by"] = _aliases[spec["group_by"]]
            if spec.get("target") in _aliases:
                spec["target"] = _aliases[spec["target"]]
            clean = {"filters": {}, "group_by": None, "operation": "count", "target": "trend_label"}'''

if anchor not in src:
    print("ERROR: could not find _validate_spec anchor. No changes made.")
    sys.exit(1)

patched = src.replace(anchor, new)
try:
    ast.parse(patched)
except SyntaxError as e:
    print("ERROR: syntax error:", e); sys.exit(1)

shutil.copy(UI, UI + ".prealias")
with open(UI, "w") as f:
    f.write(patched)
print("SUCCESS: column aliases added. Backup: view/ui.py.prealias")
