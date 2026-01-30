"""
DeepSeek-OCR Tool for jb-serve

A vision-language model for document OCR with markdown conversion.
"""

import os
import torch
from pathlib import Path
from typing import Optional
from pydantic import Field

from jb_service import MessagePackService, method, run

# Model will be loaded on first use or during setup
MODEL = None
TOKENIZER = None
MODEL_NAME = "deepseek-ai/DeepSeek-OCR"


def get_model():
    """Lazy load the model."""
    global MODEL, TOKENIZER
    
    if MODEL is None:
        from transformers import AutoModel, AutoTokenizer
        
        print(f"Loading DeepSeek-OCR model from {MODEL_NAME}...")
        
        TOKENIZER = AutoTokenizer.from_pretrained(
            MODEL_NAME, 
            trust_remote_code=True
        )
        
        # Try flash attention, fall back to eager if not available
        try:
            MODEL = AutoModel.from_pretrained(
                MODEL_NAME,
                _attn_implementation='flash_attention_2',
                trust_remote_code=True,
                use_safetensors=True
            )
        except Exception as e:
            print(f"Flash attention not available ({e}), using eager attention")
            MODEL = AutoModel.from_pretrained(
                MODEL_NAME,
                _attn_implementation='eager',
                trust_remote_code=True,
                use_safetensors=True
            )
        
        MODEL = MODEL.eval().cuda().to(torch.bfloat16)
        print("Model loaded successfully")
    
    return MODEL, TOKENIZER


class DeepSeekOCR(MessagePackService):
    """DeepSeek-OCR document understanding service."""
    
    @method
    def setup(self) -> dict:
        """
        Download and initialize the model.
        Called automatically during jb-serve install.
        """
        try:
            model, tokenizer = get_model()
            return {
                "status": "ok",
                "model_loaded": True,
                "model_name": MODEL_NAME,
                "device": str(next(model.parameters()).device)
            }
        except Exception as e:
            return {
                "status": "error",
                "model_loaded": False,
                "error": str(e)
            }
    
    @method
    def ocr(
        self,
        image: str,
        prompt: str = "Free OCR.",
        base_size: int = 1024,
        image_size: int = 640,
        crop_mode: bool = True
    ) -> dict:
        """
        Extract text from an image using DeepSeek-OCR.
        
        Args:
            image: Path to image file
            prompt: OCR prompt (default: "Free OCR.")
            base_size: Base image size (512/640/1024/1280)
            image_size: Processing size
            crop_mode: Enable crop mode for detail extraction
        
        Returns:
            Extracted text and token count
        """
        model, tokenizer = get_model()
        
        # Format prompt with image token
        full_prompt = f"<image>\n{prompt}"
        
        # Create temp output dir
        output_path = "/tmp/deepseek_ocr_output"
        os.makedirs(output_path, exist_ok=True)
        
        # Run inference
        result = model.infer(
            tokenizer,
            prompt=full_prompt,
            image_file=image,
            output_path=output_path,
            base_size=base_size,
            image_size=image_size,
            crop_mode=crop_mode,
            save_results=False,
            test_compress=False
        )
        
        # Extract text from result
        if isinstance(result, dict):
            text = result.get('text', str(result))
            tokens = result.get('tokens', 0)
        else:
            text = str(result)
            tokens = len(tokenizer.encode(text)) if text else 0
        
        return {
            "text": text,
            "tokens": tokens
        }
    
    @method
    def to_markdown(
        self,
        image: str,
        base_size: int = 1024,
        image_size: int = 640,
        crop_mode: bool = True
    ) -> dict:
        """
        Convert a document image to Markdown format.
        
        Args:
            image: Path to document image
            base_size: Base image size
            image_size: Processing size
            crop_mode: Enable crop mode
        
        Returns:
            Markdown text and token count
        """
        # Use grounding prompt for markdown conversion
        prompt = "<|grounding|>Convert the document to markdown."
        
        result = self.ocr(
            image=image,
            prompt=prompt,
            base_size=base_size,
            image_size=image_size,
            crop_mode=crop_mode
        )
        
        return {
            "markdown": result["text"],
            "tokens": result["tokens"]
        }
    
    @method
    def health(self) -> dict:
        """Health check."""
        global MODEL
        
        if MODEL is None:
            return {"status": "ok", "model_loaded": False}
        
        return {
            "status": "ok",
            "model_loaded": True,
            "device": str(next(MODEL.parameters()).device)
        }


if __name__ == "__main__":
    run(DeepSeekOCR)
