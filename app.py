#!/usr/bin/env python3
"""
TypeWriter local minimal UI.

Runs the TypeWriter notebook runtime cells in-process, then launches a tiny Gradio UI:

input box -> generate button -> output box

The adapter ZIP is not committed to git. Pass it with --adapter-zip or TYPEWRITER_ADAPTER_ZIP.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
import traceback
from types import SimpleNamespace
from typing import Dict, Iterable, List, Optional, Tuple

import gradio as gr


REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_NOTEBOOK = REPO_ROOT / "notebooks" / "TYPEWRITER_GITHUB_MINIMAL_UI_COLAB_R1.ipynb"
DEFAULT_ADAPTER_NAME = "TYPEWRITER_V146BF_R2E_LOW_RAM_SMALL_RECOVERY_AF1_RESULT_20260610_203138_KST.zip"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run TypeWriter minimal local Gradio UI.")
    parser.add_argument(
        "--notebook",
        type=Path,
        default=DEFAULT_NOTEBOOK,
        help="Path to the TypeWriter runtime notebook.",
    )
    parser.add_argument(
        "--adapter-zip",
        type=Path,
        default=None,
        help="Path to V146BF R2E adapter ZIP. Can also use TYPEWRITER_ADAPTER_ZIP.",
    )
    parser.add_argument(
        "--base-model-dir",
        type=Path,
        default=None,
        help="Optional local Qwen2.5-7B-Instruct directory. Can also use TYPEWRITER_BASE_MODEL_DIR.",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=REPO_ROOT / "data",
        help="Local cache/output directory.",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Server host. Use 0.0.0.0 for LAN access.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=7860,
        help="Server port.",
    )
    parser.add_argument(
        "--share",
        action="store_true",
        help="Create a temporary public Gradio link.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not load the model; use deterministic dry-run text.",
    )
    parser.add_argument(
        "--allow-download",
        action="store_true",
        help="Allow Hugging Face download if base model is not found locally.",
    )
    return parser.parse_args()


def find_adapter_zip(args: argparse.Namespace) -> Path:
    candidates: List[Path] = []
    if args.adapter_zip:
        candidates.append(args.adapter_zip)
    if os.environ.get("TYPEWRITER_ADAPTER_ZIP"):
        candidates.append(Path(os.environ["TYPEWRITER_ADAPTER_ZIP"]))
    candidates += [
        REPO_ROOT / "artifacts" / DEFAULT_ADAPTER_NAME,
        REPO_ROOT / DEFAULT_ADAPTER_NAME,
        Path.cwd() / "artifacts" / DEFAULT_ADAPTER_NAME,
        Path.cwd() / DEFAULT_ADAPTER_NAME,
    ]
    for p in candidates:
        if p and p.exists():
            return p.resolve()
    raise FileNotFoundError(
        "Adapter ZIP not found. Put it at ./artifacts/{name} or pass "
        "--adapter-zip /path/to/{name}".format(name=DEFAULT_ADAPTER_NAME)
    )


def read_notebook_cells(path: Path) -> List[Tuple[int, str, str]]:
    nb = json.loads(path.read_text(encoding="utf-8"))
    out: List[Tuple[int, str, str]] = []
    for i, cell in enumerate(nb.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue
        src = "".join(cell.get("source", []))
        title_match = re.search(r"#@title[^\n]*", src)
        title = title_match.group(0) if title_match else f"cell_{i}"
        out.append((i, title, src))
    return out


def should_execute_cell(index: int, title: str, src: str) -> bool:
    """Run only the runtime cells needed for local UI."""
    skip_title_patterns = [
        "1. Install dependencies",
        "2B. AF1F install base model",
        "11. Single full E2E test",
        "12. Blind stress cases",
        "12B.",
        "12C.",
        "12D.",
        "12E.",
        "13. Run blind stress",
        "13A-0.",
        "13A-2.",
        "13A-1.",
        "13A0.",
        "13A1.",
        "13A2.",
        "13A2.5.",
        "13A3.",
        "13A. AF1J",
        "13B.",
        "13C.",
        "13D.",
        "13D2.",
        "13E.",
        "13F.",
        "13F2.",
        "13G.",
        "13H.",
        "14. Save artifacts",
        "TypeWriter Minimal UI",
    ]
    if any(p in title for p in skip_title_patterns):
        return False

    # Execute runtime foundation through gate/generation definitions.
    allowed_title_patterns = [
        "0. Runtime config",
        "GitHub minimal UI defaults",
        "0C.",
        "0B.",
        "2. Mount Drive and verify stable",
        "3. Extract adapter",
        "4. Pack registry",
        "5. Input",
        "6. Tag bundle",
        "7. Pack",
        "8. Load model",
        "9. Generate body",
        "10. V146BQ gate",
    ]
    return any(p in title for p in allowed_title_patterns)


def patch_source_for_local(src: str, ns: Dict[str, object]) -> str:
    """Patch hard-coded Colab paths and harmless IPython syntax for local execution."""
    data_dir = Path(ns.get("TYPEWRITER_DATA_DIR", REPO_ROOT / "data"))
    extract_root = data_dir / "typewriter_v146bf_r2e_adapter"

    src = src.replace(
        'EXTRACT_ROOT = Path("/content/typewriter_v146bf_r2e_adapter")',
        f'EXTRACT_ROOT = Path(r"{extract_root}")',
    )

    # The verify cell sets MOUNT_DRIVE=True; local import google.colab is caught,
    # but make intent explicit.
    src = src.replace("MOUNT_DRIVE = True  #@param {type:\"boolean\"}", "MOUNT_DRIVE = False")

    # Shell escapes are skipped because install/UI cells are not executed, but keep this guard.
    lines = []
    for line in src.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("!") or stripped.startswith("%"):
            continue
        lines.append(line)
    return "\n".join(lines) + "\n"


def apply_local_overrides(ns: Dict[str, object], args: argparse.Namespace, adapter_zip: Path) -> None:
    data_dir = args.data_dir.resolve()
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "outputs").mkdir(parents=True, exist_ok=True)
    (data_dir / "hf_home").mkdir(parents=True, exist_ok=True)
    (data_dir / "models").mkdir(parents=True, exist_ok=True)

    base_model_dir = args.base_model_dir or (
        Path(os.environ["TYPEWRITER_BASE_MODEL_DIR"]) if os.environ.get("TYPEWRITER_BASE_MODEL_DIR") else None
    )
    if base_model_dir:
        base_model_dir = base_model_dir.resolve()

    ns["TYPEWRITER_DATA_DIR"] = data_dir
    ns["DRIVE_ROOT"] = data_dir
    ns["RESULTS_ROOT"] = data_dir / "results"
    ns["LOCAL_RESULTS_ROOT"] = data_dir / "outputs"
    ns["DRIVE_BASE_MODEL_DIR"] = base_model_dir or (data_dir / "models" / "Qwen2.5-7B-Instruct")
    ns["DRIVE_HF_HOME"] = data_dir / "hf_home"
    ns["DRIVE_HF_HUB_CACHE"] = data_dir / "hf_home" / "hub"
    ns["USE_DRIVE_CACHE_FIRST"] = True
    ns["ALLOW_DOWNLOAD_FALLBACK"] = bool(args.allow_download)
    ns["INSTALL_BASE_MODEL_TO_DRIVE_IF_MISSING"] = False
    ns["FORCE_REINSTALL_BASE_MODEL_TO_DRIVE"] = False
    ns["DRY_RUN_WITH_DETERMINISTIC_TEXT"] = bool(args.dry_run)

    ns["CANDIDATE_ADAPTER_PATHS"] = [
        adapter_zip,
        REPO_ROOT / "artifacts" / DEFAULT_ADAPTER_NAME,
        REPO_ROOT / DEFAULT_ADAPTER_NAME,
        Path.cwd() / "artifacts" / DEFAULT_ADAPTER_NAME,
        Path.cwd() / DEFAULT_ADAPTER_NAME,
    ]
    ns["START_ADAPTER_ZIP"] = adapter_zip

    os.environ["HF_HOME"] = str(ns["DRIVE_HF_HOME"])
    os.environ["HF_HUB_CACHE"] = str(ns["DRIVE_HF_HUB_CACHE"])
    os.environ["TRANSFORMERS_CACHE"] = str(ns["DRIVE_HF_HUB_CACHE"])


def load_runtime(args: argparse.Namespace) -> Dict[str, object]:
    adapter_zip = find_adapter_zip(args)
    cells = read_notebook_cells(args.notebook)

    ns: Dict[str, object] = {
        "__name__": "__typewriter_local_runtime__",
        "__file__": str(args.notebook.resolve()),
        "Path": Path,
        "os": os,
        "sys": sys,
    }

    print(f"[TypeWriter] notebook: {args.notebook}")
    print(f"[TypeWriter] adapter:  {adapter_zip}")
    print(f"[TypeWriter] data dir: {args.data_dir.resolve()}")

    for index, title, src in cells:
        if not should_execute_cell(index, title, src):
            continue

        # After config/default cells, local overrides must win.
        if "Runtime config" in title or "GitHub minimal UI defaults" in title or "0C." in title or "0B." in title:
            exec(compile(patch_source_for_local(src, ns), f"{args.notebook.name}:cell_{index}", "exec"), ns)
            apply_local_overrides(ns, args, adapter_zip)
            print(f"[TypeWriter] executed {index}: {title}")
            continue

        # Before adapter/model cells, make sure local paths are active.
        apply_local_overrides(ns, args, adapter_zip)
        code = patch_source_for_local(src, ns)
        exec(compile(code, f"{args.notebook.name}:cell_{index}", "exec"), ns)
        print(f"[TypeWriter] executed {index}: {title}")

    if "e2e_generate_one" not in ns:
        raise RuntimeError("Runtime loaded but e2e_generate_one() was not defined.")

    return ns


def launch_ui(ns: Dict[str, object], args: argparse.Namespace) -> None:
    e2e_generate_one = ns["e2e_generate_one"]

    def typewriter_generate(user_input: str) -> str:
        user_input = (user_input or "").strip()
        if not user_input:
            return "입력을 넣어줘."

        try:
            result = e2e_generate_one(user_input)
            return result.get("final_text", "").strip() or "[EMPTY OUTPUT]"
        except Exception:
            return "[ERROR]\n" + traceback.format_exc()

    with gr.Blocks(title="TypeWriter Local") as demo:
        gr.Markdown("## TypeWriter Local")

        user_input = gr.Textbox(
            label="입력",
            placeholder="예: 탑 17층 공략 뒤 협회 공시의 최고층 갱신 기한을 보고 루트를 바꾸는 장면",
            lines=4,
        )

        run_btn = gr.Button("생성")

        output = gr.Textbox(
            label="출력",
            lines=22,
            )

        run_btn.click(fn=typewriter_generate, inputs=user_input, outputs=output)

    demo.queue()
    demo.launch(server_name=args.host, server_port=args.port, share=args.share, debug=False)


def main() -> None:
    args = parse_args()
    ns = load_runtime(args)
    launch_ui(ns, args)


if __name__ == "__main__":
    main()
