# TypeWriter Local Minimal UI

This repo can run the TypeWriter input/output UI locally.

UI scope:

```text
input box
→ generate button
→ output box
```

## Important

The LoRA adapter ZIP is **not committed** to git.

Put it here:

```text
./artifacts/TYPEWRITER_V146BF_R2E_LOW_RAM_SMALL_RECOVERY_AF1_RESULT_20260610_203138_KST.zip
```

or pass:

```bash
python app.py --adapter-zip /path/to/TYPEWRITER_V146BF_R2E_LOW_RAM_SMALL_RECOVERY_AF1_RESULT_20260610_203138_KST.zip
```

## Recommended environment

Linux or WSL2 Ubuntu with NVIDIA GPU is recommended.

A 7B Qwen + LoRA path is not a cute little toaster. It wants a real GPU.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements-local.txt
```

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -r requirements-local.txt
```

## Run

Linux/macOS/WSL:

```bash
./run_local.sh
```

or:

```bash
python app.py \
  --adapter-zip ./artifacts/TYPEWRITER_V146BF_R2E_LOW_RAM_SMALL_RECOVERY_AF1_RESULT_20260610_203138_KST.zip \
  --data-dir ./data \
  --allow-download
```

Windows:

```bat
run_local.bat
```

Open:

```text
http://127.0.0.1:7860
```

## Base model

By default, `app.py` tries local cache first. If `--allow-download` is used and no local model directory is found, it tries to download:

```text
Qwen/Qwen2.5-7B-Instruct
```

To use an existing local model folder:

```bash
python app.py \
  --adapter-zip ./artifacts/TYPEWRITER_V146BF_R2E_LOW_RAM_SMALL_RECOVERY_AF1_RESULT_20260610_203138_KST.zip \
  --base-model-dir /path/to/Qwen2.5-7B-Instruct
```

or set:

```bash
export TYPEWRITER_BASE_MODEL_DIR=/path/to/Qwen2.5-7B-Instruct
```

## Dry run

To test the UI without loading the model:

```bash
python app.py --dry-run --adapter-zip ./artifacts/TYPEWRITER_V146BF_R2E_LOW_RAM_SMALL_RECOVERY_AF1_RESULT_20260610_203138_KST.zip
```

## GitHub rule

Do not commit:

```text
*.zip
*.safetensors
*.bin
*.pt
data/
artifacts/
```
