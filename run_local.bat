@echo off
set ADAPTER=%TYPEWRITER_ADAPTER_ZIP%
if "%ADAPTER%"=="" set ADAPTER=.\artifacts\TYPEWRITER_V146BF_R2E_LOW_RAM_SMALL_RECOVERY_AF1_RESULT_20260610_203138_KST.zip

python app.py --adapter-zip "%ADAPTER%" --data-dir .\data --host 127.0.0.1 --port 7860 --allow-download
