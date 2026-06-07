#!/usr/bin/env python3
"""Fix the /generate endpoint: pass input_ids as keyword and ensure 2D tensor."""
import ast, shutil, sys

API = "controller/api.py"
with open(API) as f:
    src = f.read()

old = '''        input_ids = tokenizer.apply_chat_template(
            [{"role": "user", "content": req.prompt}],
            add_generation_prompt=True,
            return_tensors="pt",
        ).to(model.device)

        # Disable the LoRA adapter so we use the base model for JSON generation.
        try:
            ctx = model.disable_adapter()
        except Exception:
            import contextlib
            ctx = contextlib.nullcontext()

        with torch.inference_mode():
            with ctx:
                out = model.generate(
                    input_ids,
                    max_new_tokens=req.max_new_tokens,
                    do_sample=False,
                    pad_token_id=tokenizer.eos_token_id,
                )

        text = tokenizer.decode(out[0][input_ids.shape[1]:], skip_special_tokens=True)
        return {"text": text}'''

new = '''        prompt_str = tokenizer.apply_chat_template(
            [{"role": "user", "content": req.prompt}],
            tokenize=False,
            add_generation_prompt=True,
        )
        enc = tokenizer(prompt_str, return_tensors="pt").to(model.device)

        # Disable the LoRA adapter so we use the base model for JSON generation.
        try:
            ctx = model.disable_adapter()
        except Exception:
            import contextlib
            ctx = contextlib.nullcontext()

        with torch.inference_mode():
            with ctx:
                out = model.generate(
                    **enc,
                    max_new_tokens=req.max_new_tokens,
                    do_sample=False,
                    pad_token_id=tokenizer.eos_token_id,
                )

        text = tokenizer.decode(
            out[0][enc["input_ids"].shape[1]:], skip_special_tokens=True
        )
        return {"text": text}'''

if old not in src:
    print("ERROR: could not find the generate body to fix. No changes made.")
    sys.exit(1)

patched = src.replace(old, new)
try:
    ast.parse(patched)
except SyntaxError as e:
    print("ERROR: syntax error:", e); sys.exit(1)

shutil.copy(API, API + ".pregenfix")
with open(API, "w") as f:
    f.write(patched)
print("SUCCESS: /generate fixed (uses tokenizer + **enc). Backup: controller/api.py.pregenfix")
