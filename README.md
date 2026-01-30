# jb-deepseek-ocr

Document OCR with markdown conversion using DeepSeek's vision-language model, built for [jb-serve](https://github.com/calobozan/jb-serve).

## What is jb-serve?

[jb-serve](https://github.com/calobozan/jb-serve) is a tool server that manages Python-based AI tools with automatic environment isolation, GPU resource management, and a REST API. This tool is designed to run on jb-serve.

## Features

- **OCR**: Extract text from images
- **Document to Markdown**: Convert document images to structured markdown
- **Table extraction**: Understands tables and formatting
- **GPU accelerated**: Uses CUDA with bfloat16 for fast inference

## Requirements

- NVIDIA GPU with ~16GB VRAM (tested on RTX 3090)
- CUDA 11.8+

## Installation

First, install jb-serve if you haven't:

```bash
# See https://github.com/calobozan/jb-serve for full setup
go install github.com/calobozan/jb-serve/cmd/jb-serve@latest
```

Then install this tool:

```bash
jb-serve install https://github.com/calobozan/jb-deepseek-ocr
# or from local path
jb-serve install ~/projects/jb-deepseek-ocr
```

The model (~7GB) will be downloaded automatically during setup.

## Usage

### Via CLI

```bash
# Extract text
jb-serve call deepseek-ocr.ocr image=/path/to/document.png

# Convert to markdown
jb-serve call deepseek-ocr.to_markdown image=/path/to/document.png
```

### Via REST API

```bash
# Start the service
curl -X POST http://localhost:9800/v1/tools/deepseek-ocr/start

# OCR - Extract text
curl -X POST http://localhost:9800/v1/tools/deepseek-ocr/ocr \
  -F "image=@document.png" \
  -F 'params={"prompt": "Free OCR."}'

# Convert to Markdown
curl -X POST http://localhost:9800/v1/tools/deepseek-ocr/to_markdown \
  -F "image=@document.png"
```

## Methods

### `ocr`

Extract text from an image with customizable prompts.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| image | file | required | Image to process |
| prompt | string | "Free OCR." | OCR prompt |
| base_size | int | 1024 | Base image size |
| image_size | int | 640 | Processing size |
| crop_mode | bool | true | Enable crop mode for detail |

### `to_markdown`

Convert a document image directly to Markdown format.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| image | file | required | Document image |
| base_size | int | 1024 | Base image size |
| image_size | int | 640 | Processing size |
| crop_mode | bool | true | Enable crop mode |

## Image Size Presets

| Preset | base_size | image_size | crop_mode | Use Case |
|--------|-----------|------------|-----------|----------|
| Tiny   | 512       | 512        | false     | Fast, low quality |
| Small  | 640       | 640        | false     | Balanced |
| Base   | 1024      | 1024       | false     | High quality |
| Gundam | 1024      | 640        | true      | Best quality/speed (default) |

## Model

Uses [deepseek-ai/DeepSeek-OCR](https://huggingface.co/deepseek-ai/DeepSeek-OCR) from Hugging Face.

## License

MIT
