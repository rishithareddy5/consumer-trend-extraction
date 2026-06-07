    def _run_analytics(query: str):
        """Option B: text-to-pandas via /generate, with rule-based fallback."""
        import json as _json
        import requests as _requests

        _VALID_COLUMNS = [
            "record_id", "visit_date", "month", "week_number", "quarter", "season",
            "city", "store_type", "retailer_id", "salesperson_name",
            "consumer_demographic", "product_category", "retailer_feedback",
            "trend_signal_type", "trend_label",
        ]
        _VALID_OPS = ["count", "list", "top", "compare"]
        _FESTIVAL_MONTHS = {
            "diwali": [10, 11], "deepavali": [10, 11], "dussehra": [10], "dasara": [10],
            "holi": [3], "onam": [8, 9], "navratri": [10], "christmas": [12],
            "pongal": [1], "sankranti": [1], "eid": [3, 4], "bakrid": [6],
            "rakhi": [8], "raksha bandhan": [8], "ganesh chaturthi": [8, 9],
        }

        def _spec_prompt(question, valid_trends):
            cols = ", ".join(_VALID_COLUMNS)
            return (
                "Convert the QUESTION into ONE line of JSON. Output JSON only. No words, no markdown, no backticks.\n\n"
                "Allowed columns: " + cols + "\n"
                'Allowed operations: "count", "list", "top", "compare"\n'
                'season values: "Summer","Monsoon","Winter".  quarter: "Q1","Q2","Q3","Q4".  month: 1-12.\n'
                "trend_label values include: " + valid_trends + "\n"
                'Festivals map to "month" (e.g. diwali, holi, onam, pongal, eid, christmas).\n\n'
                'Schema: {"filters": {}, "group_by": null, "operation": "count", "target": "trend_label"}\n\n'
                "EXAMPLES:\n"
                "QUESTION: what sells during Diwali\n"
                'JSON: {"filters": {"month": "diwali"}, "group_by": null, "operation": "top", "target": "trend_label"}\n\n'
                "QUESTION: list spicy notes in Hyderabad\n"
                'JSON: {"filters": {"trend_label": "rising_spicy_flavor_preference", "city": "Hyderabad"}, "group_by": null, "operation": "list", "target": "retailer_feedback"}\n\n'
                "QUESTION: which product is popular with senior citizens in monsoon\n"
                'JSON: {"filters": {"consumer_demographic": "senior citizens", "season": "Monsoon"}, "group_by": "product_category", "operation": "top", "target": "product_category"}\n\n'
                "QUESTION: compare spicy vs sugar free across cities\n"
                'JSON: {"filters": {}, "group_by": "city", "operation": "compare", "target": "trend_label"}\n\n'
                "QUESTION: top trends in kirana stores\n"
                'JSON: {"filters": {"store_type": "Kirana Store"}, "group_by": null, "operation": "top", "target": "trend_label"}\n\n'
                "QUESTION: " + question + "\n"
                "JSON:"
            )

        def _parse_spec(raw):
            txt = raw.strip().replace("```json", "").replace("```", "")
            if "JSON:" in txt:
                txt = txt.split("JSON:")[-1]
            start = txt.find("{")
            if start == -1:
                raise ValueError("no json")
            depth, end = 0, -1
            for i in range(start, len(txt)):
                if txt[i] == "{":
                    depth += 1
                elif txt[i] == "}":
                    depth -= 1
                    if depth == 0:
                        end = i
                        break
            if end == -1:
                raise ValueError("unbalanced json")
            return _json.loads(txt[start:end + 1])

        def _validate_spec(spec):
            clean = {"filters": {}, "group_by": None, "operation": "count", "target": "trend_label"}
            for col, val in (spec.get("filters") or {}).items():
                if col not in _VALID_COLUMNS:
                    raise ValueError("bad filter col")
                clean["filters"][col] = val
            gb = spec.get("group_by")
            if gb is not None:
                if gb not in _VALID_COLUMNS:
                    raise ValueError("bad group_by")
                clean["group_by"] = gb
            op = spec.get("operation", "count")
            if op not in _VALID_OPS:
                raise ValueError("bad op")
            clean["operation"] = op
            tgt = spec.get("target", "trend_label")
            if tgt not in _VALID_COLUMNS:
                raise ValueError("bad target")
            clean["target"] = tgt
            return clean

        def _run_spec(df, spec):
            import plotly.express as px
            filtered = df.copy()
            applied = []
            for col, val in spec["filters"].items():
                if col == "month" and isinstance(val, str) and val.lower() in _FESTIVAL_MONTHS:
                    months = _FESTIVAL_MONTHS[val.lower()]
                    filtered = filtered[filtered["month"].isin(months)]
                    applied.append(col + " in " + str(months) + " (" + val + ")")
                elif isinstance(val, list):
                    filtered = filtered[filtered[col].isin(val)]
                    applied.append(col + " in " + str(val))
                else:
                    if filtered[col].dtype == object:
                        filtered = filtered[filtered[col].astype(str).str.lower() == str(val).lower()]
                    else:
                        filtered = filtered[filtered[col] == val]
                    applied.append(col + " = " + str(val))

            result = {"text": "", "chart": None, "samples": [], "insight": ""}
            n = len(filtered)
            fdesc = " AND ".join(applied) if applied else "all records"
            if n == 0:
                result["text"] = "No records found for: " + fdesc + "."
                return result
            result["text"] = "Found **" + str(n) + "** records matching: *" + fdesc + "*."

            op, tgt, gb = spec["operation"], spec["target"], spec["group_by"]

            if op == "list":
                cols = [c for c in ["record_id", "city", "consumer_demographic",
                                    "product_category", "retailer_feedback"] if c in filtered.columns]
                result["samples"] = filtered[cols].head(15).to_dict("records")
                result["insight"] = "Listing " + str(min(15, n)) + " of " + str(n) + " matching records."
                return result

            if op == "compare" and gb:
                grp = filtered.groupby([gb, "trend_label"]).size().reset_index(name="count")
                fig = px.bar(grp, x=gb, y="count", color="trend_label", barmode="group",
                             title="Comparison by " + gb)
                fig.update_layout(height=400, margin=dict(l=20, r=20, t=50, b=20))
                result["chart"] = fig
            else:
                chart_col = gb if gb else tgt
                counts = filtered[chart_col].value_counts().head(10).reset_index()
                counts.columns = [chart_col, "count"]
                fig = px.bar(counts, x="count", y=chart_col, orientation="h",
                             title=chart_col.replace("_", " ").title() + " distribution")
                fig.update_traces(marker_color="#2563EB")
                fig.update_layout(height=380, showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
                result["chart"] = fig

            top_trend = filtered["trend_label"].value_counts().head(1)
            if len(top_trend):
                tname = top_trend.index[0].replace("_", " ")
                result["insight"] = ("Across <b>" + str(n) + "</b> records, the dominant trend is <b>"
                                     + tname + "</b> (" + str(int(top_trend.iloc[0])) + " records)."
                                     + "<br><br><b>OEM Recommendation:</b> prioritise <b>" + tname
                                     + "</b> initiatives for this segment.")
            samples = filtered.sample(min(3, n), random_state=42)
            result["samples"] = samples[["record_id", "city", "consumer_demographic",
                                         "retailer_feedback"]].to_dict("records")
            return result

        try:
            df = _load_dataset()
            valid_trends = ", ".join(sorted(df["trend_label"].unique()))
            prompt = _spec_prompt(query, valid_trends)
            r = _requests.post(API_URL + "/generate",
                               json={"prompt": prompt, "max_new_tokens": 160}, timeout=60)
            r.raise_for_status()
            raw = r.json()["text"]
            spec = _validate_spec(_parse_spec(raw))
            out = _run_spec(df, spec)
            if out.get("text", "").startswith("No records") and not spec["filters"]:
                return _run_analytics_rulebased(query)
            return out
        except Exception:
            return _run_analytics_rulebased(query)

    def _run_analytics_rulebased(query: str):
