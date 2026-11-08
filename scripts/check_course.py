#!/usr/bin/env python3
"""Check lesson structure, notebook contracts and generated source consistency."""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SECTIONS = ["이번 주차", "온라인 (2시수)", "대면 (1시수)", "학습활동", "자주 하는 오해 Q&A", "스스로 점검", "이번 주 용어 정리", "이번 주 읽기", "실습 노트북"]
NOTEBOOK_WEEKS = set(range(1, 12)) | {14}


def source(cell: dict) -> str:
    text = cell["source"]
    return text if isinstance(text, str) else "".join(text)


def generated_cells(path: Path) -> list[dict]:
    # Evaluate only definitions through the cells assignment. Never run file writes,
    # dependency installation or the generator's notebook execution harness.
    nodes = []
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        nodes.append(node)
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "cells" for t in node.targets):
            break
    else:
        raise AssertionError(f"cells assignment missing: {path}")
    namespace = {"__file__": str(path)}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), namespace)
    return namespace["cells"]


def main() -> None:
    figures = set()
    for week in range(1, 16):
        path = ROOT / f"src/content/docs/weeks/week-{week:02d}.mdx"
        text = path.read_text(encoding="utf-8")
        assert re.findall(r"^## (.+)$", text, re.M) == SECTIONS, path
        qa = text.split("## 자주 하는 오해 Q&A", 1)[1].split("## 스스로 점검", 1)[0]
        assert qa.count("<summary>") >= 8, f"Q&A coverage: {path}"
        assert text.count("<details>") == text.count("</details>"), path
        assert text.count("<summary>") == text.count("</summary>"), path
        assert "기본" in text and ("심화" in text or "확장" in text or "더 확인할" in text), path
        for target in re.findall(r"from\s+['\"]([^'\"]+\.(?:webp|png|svg))['\"]", text):
            assert (path.parent / target).is_file(), (path, target)
        for target in re.findall(r'src="(/interactive/[^"#]+)"', text):
            assert (ROOT / "public" / urlsplit(target).path.lstrip("/")).is_file(), (path, target)
            figures.add(target)
        for target in re.findall(r"\]\((/worksheets/[^)#]+)(?:#[^)]*)?\)", text):
            assert (ROOT / "public" / urlsplit(target).path.lstrip("/")).is_file(), (path, target)
        badge = f"https://colab.research.google.com/github/halla-ai/intronlp-2026/blob/main/notebooks/week-{week:02d}.ipynb"
        assert (badge in text) == (week in NOTEBOOK_WEEKS), (path, "notebook mapping")
    paths = sorted((ROOT / "notebooks").glob("week-*.ipynb"))
    assert {int(p.stem[-2:]) for p in paths} == NOTEBOOK_WEEKS
    generators = 0
    for path in paths:
        nb = json.loads(path.read_text(encoding="utf-8"))
        cells = nb["cells"]
        assert path.name in source(cells[0]) and "colab.research.google.com/github/" in source(cells[0]), path
        code = [c for c in cells if c["cell_type"] == "code"]
        assert sum("TODO" in source(c) for c in code) == 1, path
        for cell in code:
            assert cell.get("execution_count") is None and not cell.get("outputs"), path
            python = "\n".join(line if not line.lstrip().startswith(("%", "!")) else "" for line in source(cell).splitlines())
            ast.parse(python, filename=str(path))
        generator = ROOT / f"scripts/gen_week{path.stem[-2:]}.py"
        if generator.exists():
            expected = generated_cells(generator)
            assert [(c["cell_type"], source(c)) for c in expected] == [(c["cell_type"], source(c)) for c in cells], f"generator drift: {path}"
            generators += 1
    print(f"PASS: 15 lessons, {len(paths)} notebooks, {generators} generators, {len(figures)} interactive paths")


if __name__ == "__main__":
    main()
