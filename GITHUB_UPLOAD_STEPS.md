# GitHub upload steps

## Option A: GitHub web UI

1. Create a new GitHub repository.
2. Upload all files from this folder.
3. Commit.
4. Open:

```text
notebooks/TYPEWRITER_GITHUB_MINIMAL_UI_COLAB_R1.ipynb
```

5. Click **Open in Colab** or copy the GitHub URL into Colab.

## Option B: git command line

```bash
git init
git add .
git commit -m "Add TypeWriter minimal UI Colab runner"
git branch -M main
git remote add origin https://github.com/<YOUR_ID>/<YOUR_REPO>.git
git push -u origin main
```

## Do not commit adapter ZIP

The adapter ZIP is large and should stay in Drive.

```text
TYPEWRITER_V146BF_R2E_LOW_RAM_SMALL_RECOVERY_AF1_RESULT_20260610_203138_KST.zip
```

If you later need model artifacts in GitHub, use Git LFS or a release asset, not normal git history.
