#!/usr/bin/env python3
"""Execute week 04 in isolated kernels and retain evidence on failure."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import shlex
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from uuid import uuid4

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_NOTEBOOK = ROOT / "notebooks" / "week-04.ipynb"
CHECK_REQUIREMENTS = ROOT / "requirements-check.txt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--notebook", type=Path, default=DEFAULT_NOTEBOOK)
    parser.add_argument("--wheel", type=Path, help="candidate wheel to validate")
    parser.add_argument("--published", action="store_true", help="run published install")
    parser.add_argument("--both", action="store_true", help="run published and candidate")
    parser.add_argument("--keep-output", action="store_true", help="retain output notebooks")
    args = parser.parse_args()
    if args.both and not args.wheel:
        parser.error("--both requires --wheel")
    if args.published and args.wheel and not args.both:
        parser.error("use --both to run published and candidate validations together")
    return args


def assert_notebook_shape(notebook: nbformat.NotebookNode) -> None:
    todo_cells = [c for c in notebook.cells if c.cell_type == "code" and "TODO" in c.source]
    if len(todo_cells) != 1:
        raise AssertionError(f"expected one student TODO code cell, found {len(todo_cells)}")
    install_cells = [
        c for c in notebook.cells
        if c.cell_type == "code" and "%pip" in c.source and "ekonlpy" in c.source
    ]
    if len(install_cells) != 1:
        raise AssertionError(f"expected one eKoNLPy install cell, found {len(install_cells)}")


def candidate_notebook(notebook: nbformat.NotebookNode, wheel: Path) -> nbformat.NotebookNode:
    candidate = copy.deepcopy(notebook)
    wheel_arg = shlex.quote(str(wheel.resolve()))
    replacements = 0
    for cell in candidate.cells:
        if cell.cell_type != "code" or "%pip" not in cell.source or "ekonlpy" not in cell.source:
            continue
        cell.source = "\n".join(
            f"%pip install -q {wheel_arg} \"pandas>=1.5.3\""
            if line.lstrip().startswith("%pip") and "ekonlpy" in line else line
            for line in cell.source.splitlines()
        )
        replacements += 1
    if replacements != 1:
        raise AssertionError(f"candidate install substitution count: {replacements}")
    assertion = nbformat.v4.new_code_cell(
        "from importlib.metadata import distribution\n"
        "from pathlib import Path\n"
        "from urllib.parse import urlparse\n"
        "from urllib.request import url2pathname\n"
        "import json\n"
        "candidate_dist = distribution(\"ekonlpy\")\n"
        "direct_url_text = candidate_dist.read_text(\"direct_url.json\")\n"
        "assert direct_url_text, \"missing candidate provenance\"\n"
        "direct_url = json.loads(direct_url_text)\n"
        "installed_wheel = Path(url2pathname(urlparse(direct_url[\"url\"]).path)).resolve()\n"
        f"expected_wheel = Path({str(wheel.resolve())!r}).resolve()\n"
        "assert installed_wheel == expected_wheel, (installed_wheel, expected_wheel)\n"
        f"expected_hash = {hashlib.sha256(wheel.read_bytes()).hexdigest()!r}\n"
        "assert direct_url[\"archive_info\"][\"hashes\"][\"sha256\"] == expected_hash\n"
        "print(\"candidate direct_url:\", direct_url)\n"
        "print(\"candidate Requires-Dist verified:\", candidate_dist.requires or [])"
    )
    for index, cell in enumerate(candidate.cells):
        if cell.cell_type == "code" and "%pip" in cell.source and "ekonlpy" in cell.source:
            candidate.cells.insert(index + 1, assertion)
            break
    return candidate


def wheel_requirements(wheel: Path) -> list[str]:
    with zipfile.ZipFile(wheel) as archive:
        metadata_name = next(name for name in archive.namelist() if name.endswith("/METADATA"))
        metadata = archive.read(metadata_name).decode("utf-8")
    return [line.removeprefix("Requires-Dist: ") for line in metadata.splitlines() if line.startswith("Requires-Dist: ")]


def output_text(notebook: nbformat.NotebookNode) -> str:
    return "\n".join(
        output.get("text", "")
        for cell in notebook.cells if cell.cell_type == "code"
        for output in cell.get("outputs", [])
    )


def execute(notebook: nbformat.NotebookNode, label: str, keep_output: bool) -> None:
    output_handle = tempfile.NamedTemporaryFile(prefix=f"week04-{label}-", suffix=".ipynb", delete=False)
    output_path = Path(output_handle.name)
    output_handle.close()
    notebook = copy.deepcopy(notebook)
    diagnostic = nbformat.v4.new_code_cell(
        'import sys\nfrom importlib.metadata import distribution\n'
        'dist = distribution("ekonlpy")\n'
        'print("Kernel Python:", sys.executable)\n'
        'print("eKoNLPy origin:", dist.locate_file(""))\n'
        'print("eKoNLPy Requires-Dist:", dist.requires or [])'
    )
    installer_index = next(i for i, cell in enumerate(notebook.cells)
                           if cell.cell_type == "code" and "%pip" in cell.source)
    notebook.cells.insert(installer_index + 1, diagnostic)
    rerun = copy.deepcopy(notebook)
    repeated = copy.deepcopy(notebook.cells)
    for cell in repeated:
        cell.id = uuid4().hex[:8]
    rerun.cells.extend(repeated)
    passed = False
    try:
        with tempfile.TemporaryDirectory(prefix=f"week04-{label}-venv-") as workdir:
            work = Path(workdir)
            venv = work / "venv"
            subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
            venv_python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            subprocess.run([
                str(venv_python), "-m", "pip", "install", "-q", "--disable-pip-version-check",
                "-r", str(CHECK_REQUIREMENTS),
            ], check=True)
            kernels_root = work / "jupyter"
            kernel_dir = kernels_root / "kernels" / "week04-validation"
            kernel_dir.mkdir(parents=True)
            (kernel_dir / "kernel.json").write_text(json.dumps({
                "argv": [str(venv_python), "-m", "ipykernel_launcher", "-f", "{connection_file}"],
                "display_name": "Week 04 isolated validation", "language": "python",
            }), encoding="utf-8")
            old_jupyter_path = os.environ.get("JUPYTER_PATH")
            os.environ["JUPYTER_PATH"] = str(kernels_root) if not old_jupyter_path else f"{kernels_root}{os.pathsep}{old_jupyter_path}"
            try:
                client = NotebookClient(
                    rerun, timeout=900, kernel_name="week04-validation",
                    resources={"metadata": {"path": str(ROOT)}}, allow_errors=False,
                )
                client.execute()
            finally:
                if old_jupyter_path is None:
                    os.environ.pop("JUPYTER_PATH", None)
                else:
                    os.environ["JUPYTER_PATH"] = old_jupyter_path
            text = output_text(rerun)
            if "eKoNLPy origin:" not in text or "eKoNLPy Requires-Dist:" not in text:
                raise AssertionError("run did not report package origin and installed Requires-Dist metadata")
            print(f"{label} kernel: {venv_python}")
            print(f"{label} versions/origin/metadata:\n{text}")
            nbformat.write(rerun, output_path)
            passed = True
    except Exception:
        nbformat.write(rerun, output_path)
        print(f"FAIL {label}: partial executed output={output_path}", file=sys.stderr)
        raise
    if passed:
        print(f"PASS {label}: notebook executed twice in one isolated kernel; output={output_path}")
        if not keep_output:
            output_path.unlink()
    else:
        print(f"FAIL {label}: partial executed output={output_path}", file=sys.stderr)
        raise RuntimeError(f"week 04 {label} validation failed; see {output_path}")


def main() -> int:
    args = parse_args()
    notebook = nbformat.read(args.notebook.resolve(), as_version=4)
    assert_notebook_shape(notebook)
    wheel = args.wheel.resolve() if args.wheel else None
    if wheel and not wheel.is_file():
        raise FileNotFoundError(wheel)
    if wheel:
        requirements = wheel_requirements(wheel)
        scipy_requirements = [item for item in requirements if item.lower().startswith("scipy")]
        print(f"candidate wheel: {wheel}")
        print(f"candidate Requires-Dist: {requirements}")
        print(f"candidate SciPy requirement: {scipy_requirements}")
    if args.published or args.both or not wheel:
        print(f"published validation: {args.notebook.resolve()}")
        execute(copy.deepcopy(notebook), "published", args.keep_output)
    if wheel:
        print("candidate validation: in-memory installer substitution only")
        execute(candidate_notebook(notebook, wheel), "candidate", args.keep_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
