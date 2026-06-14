# TypeWriter Minimal UI

This repository is a minimal GitHub/Colab runner for **TypeWriter_Rebirth**.

The UI is intentionally tiny:

```text
input box
→ generate button
→ output box
```

No result viewer, no stress test panel, no batch validation UI.

## What is included

```text
notebooks/TYPEWRITER_GITHUB_MINIMAL_UI_COLAB_R1.ipynb
scripts/minimal_gradio_ui_cell.py
requirements.txt
.gitignore
GITHUB_UPLOAD_STEPS.md
```

## What is not included

The LoRA adapter ZIP is **not** included in GitHub.

Keep it in Google Drive:

```text
/content/drive/MyDrive/TypeWriter/results_v146bf_r2e_lowram/TYPEWRITER_V146BF_R2E_LOW_RAM_SMALL_RECOVERY_AF1_RESULT_20260610_203138_KST.zip
```

The notebook expects the fixed V146BF R2E adapter. Do not use V146BE/V146BH/V146BI or BP/BM/BN/BO result ZIPs as adapters.

## Quick start

1. Upload this repo to GitHub.
2. Open `notebooks/TYPEWRITER_GITHUB_MINIMAL_UI_COLAB_R1.ipynb` in Colab.
3. Runtime → Change runtime type → GPU.
4. Make sure the V146BF R2E adapter ZIP exists in Drive.
5. Run cells from top to bottom until the model/adapter is loaded.
6. Run the final cell:

```text
TypeWriter Minimal UI: input → output only
```

7. Use the Gradio URL.

## Runtime safety

Heavy stress runs are OFF by default:

```python
RUN_SINGLE_FULL_E2E = False
RUN_R14_ROTATING_BLIND = False
RUN_R16_MAX_DIVERSITY_STRESS = False
RUN_R18_GENRE_KNOWLEDGE_MAX_INPUTS = False
RUN_AF1J_BALANCED_BLIND = False
RUN_AF1K_POST_HANDLER_BLIND = False
```

The UI only generates when the user clicks the button.

## Minimal UI function

```python
def typewriter_generate(user_input):
    result = e2e_generate_one(user_input)
    return result.get("final_text", "").strip()
```


## Local run

For local execution, see:

```text
README_LOCAL.md
app.py
requirements-local.txt
run_local.sh
run_local.bat
```

Quick dry-run smoke:

```bash
python app.py --dry-run --adapter-zip ./artifacts/TYPEWRITER_V146BF_R2E_LOW_RAM_SMALL_RECOVERY_AF1_RESULT_20260610_203138_KST.zip
```
