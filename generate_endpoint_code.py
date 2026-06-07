

class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=4000)
    max_new_tokens: int = 160


@app.post("/generate")
def generate(req: GenerateRequest):  # pragma: no cover
    """Free-form generation using the BASE model (LoRA adapter disabled).
    Used by the Smart Chat analytics path to turn an analyst question into a
    JSON query-spec. Returns {"text": "..."}.
    """
    if trend_model is None:
        raise HTTPException(status_code=503, detail="Model is still loading.")
    try:
        model = trend_model.model
        tokenizer = trend_model.tokenizer

        input_ids = tokenizer.apply_chat_template(
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
        return {"text": text}
    except Exception as e:
        log.exception("generate failed")
        raise HTTPException(status_code=500, detail=str(e)) from e
