#!/usr/bin/env bash
set -euo pipefail

python app.py \
  --adapter-zip "${TYPEWRITER_ADAPTER_ZIP:-./artifacts/TYPEWRITER_V146BF_R2E_LOW_RAM_SMALL_RECOVERY_AF1_RESULT_20260610_203138_KST.zip}" \
  --data-dir ./data \
  --host 127.0.0.1 \
  --port 7860 \
  --allow-download
