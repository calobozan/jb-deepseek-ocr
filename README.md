# jb-deepseek-ocr

DeepSeek-OCR tool for jb-serve - Document OCR with markdown conversion using DeepSeek's vision-language model.

## Features

- **OCR**: Extract text from images
- **Document to Markdown**: Convert document images to structured markdown
- **Table extraction**: Understands tables and formatting
- **GPU accelerated**: Uses CUDA with bfloat16 for fast inference

## Requirements

- NVIDIA GPU with ~16GB VRAM (tested on RTX 3090)
- CUDA 11.8+
- jb-serve

## Installation

```bash
jb-serve install ~/projects/jb-deepseek-ocr
```

The model (~7GB) will be downloaded automatically during setup.

## Usage

### Start the service

```bash
curl -X POST http://localhost:9800/v1/tools/deepseek-ocr/start
```

### OCR - Extract text

```bash
curl -X POST http://localhost:9800/v1/tools/deepseek-ocr/ocr \
  -F "image=@document.png" \
  -F 'params={"prompt": "Free OCR."}'
```

### Convert to Markdown

```bash
curl -X POST http://localhost:9800/v1/tools/deepseek-ocr/to_markdown \
  -F "image=@document.png"
```

## Image Size Presets

| Preset | base_size | image_size | crop_mode |
|--------|-----------|------------|-----------|
| Tiny   | 512       | 512        | false     |
| Small  | 640       | 640        | false     |
| Base   | 1024      | 1024       | false     |
| Large  | 1280      | 1280       | false     |
| Gundam | 1024      | 640        | true      |

Default is "Gundam" mode (best quality/speed tradeoff).

## Model

Uses [deepseek-ai/DeepSeek-OCR](https://huggingface.co/deepseek-ai/DeepSeek-OCR) from Hugging Face.

## License

MIT
