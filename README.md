# TYPEWRITER_GITHUB_SPLIT_ADAPTER_UI_COLAB_R1

Colab notebook for TypeWriter minimal input/output UI using split adapter parts stored in GitHub.

## Required repo layout

```text
adapter_parts/
  adapter.part000
  adapter.part001
  ...
notebooks/TYPEWRITER_GITHUB_SPLIT_ADAPTER_UI_COLAB_R1.ipynb
```

## Flow

1. Open the notebook in Colab.
2. Runtime -> Change runtime type -> GPU.
3. Run cells from top.
4. `0A` clones the GitHub repo.
5. `0B` rejoins adapter parts and verifies SHA256.
6. Final cell launches minimal Gradio UI.
