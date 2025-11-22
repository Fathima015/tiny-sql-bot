# model/model_api.py
import logging
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

MODEL_NAME = "google/flan-t5-base"  # or "google/flan-t5-large" if you prefer and have space

_tokenizer = None
_model = None

def load_model(device: str = "cpu"):
    global _tokenizer, _model
    if _model is None:
        print("...")
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        print(".....")
        _model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
        _model.to(device)
        _model.eval()
    return _tokenizer, _model

def generate_candidates(prompt: str,
                        max_length: int = 128,
                        num_beams: int = 6,
                        num_return_sequences: int = 6,
                        device: str = "cpu"):
    """
    Generate multiple candidate outputs (beams). Return list of decoded strings.
    We'll later filter/rerank these using the validator.
    """
    try:
        tokenizer, model = load_model(device=device)
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True).to(device)

        # Keep generation deterministic-ish with beams; return multiple candidates
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=max_length,
                num_beams=num_beams,
                num_return_sequences=num_return_sequences,
                early_stopping=True,
                no_repeat_ngram_size=3,
                temperature=1.0,
                do_sample=False,  # beam search (more stable)
            )

        texts = [tokenizer.decode(out, skip_special_tokens=True, clean_up_tokenization_spaces=True) for out in outputs]
        # dedupe while preserving order
        seen = set()
        unique = []
        for t in texts:
            t = t.strip()
            if t not in seen:
                seen.add(t)
                unique.append(t)
        return unique
    except Exception as e:
        logging.exception("Model inference failed")
        return [f"/* model error: {e} */"]
