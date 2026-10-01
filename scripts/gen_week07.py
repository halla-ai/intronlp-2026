#!/usr/bin/env python3
"""Generate notebooks/week-07.ipynb and execute it in a fresh venv to verify."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]
NB_PATH = ROOT / "notebooks" / "week-07.ipynb"


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": dedent(text).strip("\n")}


def code(text: str) -> dict:
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
            "source": dedent(text).strip("\n")}


cells = [
    md("""
        [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/halla-ai/intronlp-2026/blob/main/notebooks/week-07.ipynb)

        # 7주차 실습: 단어 임베딩을 학습하고 비슷한 단어 찾기

        **목표.** 작은 말뭉치로 Word2Vec 임베딩을 직접 학습시켜 비슷한 단어를 찾고 지도로 그려 본다. 이어서 큰 말뭉치로 미리 학습된 한국어 벡터에서 제주 단어의 이웃을 찾아, 예상과 다른 결과가 왜 나오는지 살펴본다.
    """),
    md("""
        ## 0. 준비

        단어 임베딩 라이브러리 gensim과 그래프를 그릴 matplotlib를 설치합니다. 그래프에 한글이 깨지지 않도록 공개 한글 글꼴(나눔고딕)도 내려받습니다.

        설치 셀에서 오류가 나면 다음 셀로 넘어가지 말고 오류의 마지막 줄을 확인하세요.
    """),
    code("""
        %pip -q install "gensim>=4.3" "matplotlib>=3.7"
    """),
    code("""
        import sys
        import gensim
        import numpy
        import matplotlib

        print("Python:", sys.version.split()[0])
        print("gensim:", gensim.__version__)
        print("NumPy:", numpy.__version__)
        print("matplotlib:", matplotlib.__version__)
        print("설치 확인 끝")
    """),
    code("""
        # 그래프에 한글을 쓰기 위한 글꼴 준비 (실패해도 아래 셀은 돌아갑니다)
        import urllib.request
        import matplotlib.pyplot as plt
        from matplotlib import font_manager

        try:
            font_file, _ = urllib.request.urlretrieve(
                "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf",
                "NanumGothic-Regular.ttf")
            font_manager.fontManager.addfont(font_file)
            plt.rcParams["font.family"] = font_manager.FontProperties(fname=font_file).get_name()
            print("한글 글꼴 준비 끝")
        except Exception as e:
            print("글꼴을 내려받지 못했습니다. 그래프의 한글이 네모로 보일 수 있습니다:", e)
        plt.rcParams["axes.unicode_minus"] = False
    """),
    md("""
        ## 1. 먼저 그냥 실행해 보기

        아래 셀들을 위에서부터 차례로 실행하세요. 아무것도 고치지 않아도 끝까지 돌아갑니다.

        1-1부터 1-4까지는 **직접 만든 작은 말뭉치**로 임베딩을 학습합니다. 1-5부터 1-7까지는 **큰 말뭉치로 미리 학습된 공개 한국어 벡터**를 내려받아 씁니다.
    """),
    md("""
        ### 1-1. 학습용 말뭉치 만들기

        제주 여행 문장을 틀에 맞춰 1000개 만듭니다. 지명, 음식, 볼거리를 틀의 빈칸에 무작위로 넣습니다. 문장은 **설명용 예시**입니다.

        6주차에 `귤을` 과 `귤은` 이 다른 단어로 세어져 문제가 됐습니다. 그래서 여기서는 4주차 형태소 분석처럼 **조사를 미리 떼어** `고기국수 를` 처럼 띄워 둡니다.
    """),
    code("""
        import random

        PLACES = ["제주시", "서귀포", "성산", "애월", "중문", "우도"]
        FOODS = ["고기국수", "갈치조림", "흑돼지", "전복죽", "옥돔구이"]
        SIGHTS = ["바다", "오름", "일출", "노을"]
        PATTERNS = [
            "{p} 에서 {f} 를 먹었다",
            "{f} 를 먹으러 {p} 에 갔다",
            "{f} 는 정말 맛있다",
            "{p} 에 {s} 를 보러 갔다",
            "{p} 의 {s} 가 아름답다",
        ]

        rng = random.Random(7)  # 같은 문장이 매번 나오도록 고정
        corpus = []
        for _ in range(1000):
            pattern = rng.choice(PATTERNS)
            sentence = pattern.format(p=rng.choice(PLACES), f=rng.choice(FOODS), s=rng.choice(SIGHTS))
            corpus.append(sentence.split())

        print("문장", len(corpus), "개, 단어 종류", len({w for s in corpus for w in s}), "개")
        for s in corpus[:5]:
            print(" ", " ".join(s))
    """),
    md("""
        ### 1-2. Word2Vec 학습시키기

        Word2Vec은 **이웃 단어를 맞히는 연습**을 되풀이하며 단어마다 숫자 목록(벡터)을 만듭니다. 6주차의 동시발생 행렬 행과 달리, 칸 수를 우리가 정하고(여기서는 20칸) 대부분의 칸이 0이 아닙니다.

        - `sg=1` 은 Skip-gram입니다. 가운데 단어로 주변 단어를 맞힙니다. `sg=0` 이면 CBOW로, 주변 단어로 가운데 단어를 맞힙니다
        - `window=2` 는 6주차와 같은 창으로, 양옆 **최대** 두 칸을 이웃으로 봅니다. 학습 중에는 단어마다 창을 1~2칸 사이에서 무작위로 줄여, 가까운 이웃을 더 자주 봅니다
        - `negative=5` 는 진짜 이웃 하나마다 가짜 이웃 다섯 개를 섞어 "진짜인지 가짜인지" 가리는 연습을 시킨다는 뜻입니다(네거티브 샘플링)
    """),
    code("""
        import zlib
        from gensim.models import Word2Vec

        def stable_hash(text):
            # 실행할 때마다 같은 결과가 나오도록 고정한 해시
            return zlib.crc32(text.encode("utf-8"))

        settings = dict(vector_size=20, window=2, min_count=1, negative=5, epochs=30,
                        seed=42, workers=1, hashfxn=stable_hash)
        skipgram = Word2Vec(corpus, sg=1, **settings)
        cbow = Word2Vec(corpus, sg=0, **settings)

        vec = skipgram.wv["고기국수"]
        print("고기국수의 벡터: 칸", len(vec), "개")
        print(" ", [round(float(x), 2) for x in vec[:8]], "... (앞 8칸만)")
        print("0인 칸:", int((vec == 0).sum()), "개")
    """),
    md("""
        ### 1-3. 비슷한 단어 찾기

        `most_similar` 는 코사인 유사도가 높은 단어를 순서대로 보여 줍니다. 6주차와 같은 코사인 유사도입니다.

        음식은 음식끼리, 지명은 지명끼리 모이는지 보세요. 틀에서 뽑은 문장이라 같은 무리의 단어는 늘 같은 자리에 들어갑니다. 그래서 유사도가 거의 1에 가깝게 나옵니다.
    """),
    code("""
        for word in ["고기국수", "애월", "바다"]:
            sg_top = [w for w, s in skipgram.wv.most_similar(word, topn=4)]
            cb_top = [w for w, s in cbow.wv.most_similar(word, topn=4)]
            print(f"{word}")
            print(f"  Skip-gram: {sg_top}")
            print(f"  CBOW     : {cb_top}")

        print()
        print("고기국수 ~ 갈치조림:", round(float(skipgram.wv.similarity("고기국수", "갈치조림")), 2))
        print("고기국수 ~ 애월    :", round(float(skipgram.wv.similarity("고기국수", "애월")), 2))
    """),
    md("""
        ### 1-4. 단어를 지도로 그리기

        20칸짜리 벡터는 그대로 그릴 수 없습니다. 그래서 정보를 가장 많이 남기는 방향 두 개만 골라 2차원 지도로 줄입니다(주성분 분석). 가까이 찍힌 단어는 벡터도 비슷합니다.

        지도는 위아래나 좌우가 뒤집혀 나올 수 있습니다. 무리가 어떻게 모였는지만 보세요.
    """),
    code("""
        import numpy as np

        def to_2d(vectors):
            centered = vectors - vectors.mean(axis=0)
            _, _, vt = np.linalg.svd(centered, full_matrices=False)
            return centered @ vt[:2].T

        groups = {"지명": PLACES, "음식": FOODS, "볼거리": SIGHTS}
        words = [w for ws in groups.values() for w in ws]
        points = to_2d(np.array([skipgram.wv[w] for w in words]))

        fig, ax = plt.subplots(figsize=(8, 6))
        start = 0
        spans = []
        for name, ws in groups.items():
            xy = points[start:start + len(ws)]
            ax.scatter(xy[:, 0], xy[:, 1], label=name, s=60)
            spans.append((ws, xy))
            start += len(ws)

        # 무리 안의 점이 거의 겹쳐서, 이름은 무리 옆에 한 줄씩 세우고 선으로 잇는다
        x0, x1 = ax.get_xlim()
        y0, y1 = ax.get_ylim()
        for ws, xy in spans:
            fx = (xy[:, 0].mean() - x0) / (x1 - x0)
            fy = min(max((xy[:, 1].mean() - y0) / (y1 - y0), 0.2), 0.8)
            side = -1 if fx > 0.6 else 1
            for rank, k in enumerate(np.argsort(-xy[:, 1])):
                ty = fy + (len(ws) / 2 - rank - 0.5) * 0.05
                ax.annotate(ws[k], xy[k], xytext=(fx + side * 0.16, ty), textcoords="axes fraction",
                            fontsize=11, va="center", ha="left" if side > 0 else "right",
                            arrowprops=dict(arrowstyle="-", color="gray", lw=0.6))
        ax.legend(loc="lower center")
        ax.set_title("작은 말뭉치로 학습한 단어 지도")
        plt.show()
    """),
    md("""
        ### 1-5. 큰 말뭉치로 미리 학습된 벡터 불러오기

        직접 만든 말뭉치는 작고 틀에 박혀 있습니다. 이번에는 웹 문서로 미리 학습된 **공개 한국어 단어 벡터**(fastText cc.ko.300, 단어 200만 개, 300칸, CC BY-SA 3.0)를 씁니다. 전부 받으면 너무 크므로 **자주 나오는 단어 앞 10만 개**만 받고, 그 뒤에서는 아래 목록의 제주 단어만 골라 담습니다. 1분 안팎 걸립니다.

        목록에 넣었는데도 벡터가 없다고 나오는 단어가 있습니다. 앞쪽 60만 단어 안에 한 번도 들지 못할 만큼 드물다는 뜻입니다.
    """),
    code("""
        import gzip
        import urllib.request
        import numpy as np

        URL = "https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.ko.300.vec.gz"
        TOP, SCAN = 100_000, 600_000
        JEJU_WORDS = ["제주시", "서귀포시", "중문", "한림", "애월", "협재", "표선", "성산일출봉",
                      "올레길", "유채꽃", "돌하르방", "해녀", "흑돼지", "한라봉", "고기국수",
                      "갈치조림", "전복죽", "옥돔", "몸국", "하영", "지슬", "감저", "바당", "혼저"]

        from gensim.models import KeyedVectors

        names, rows = [], []
        with urllib.request.urlopen(URL) as response, gzip.GzipFile(fileobj=response) as stream:
            stream.readline()  # 첫 줄은 단어 수와 칸 수
            for rank in range(1, SCAN + 1):
                word, numbers = stream.readline().decode("utf-8", "replace").rstrip().split(" ", 1)
                if rank <= TOP or word in JEJU_WORDS:
                    names.append(word)
                    rows.append(np.array(numbers.split(), dtype=np.float32))

        ko = KeyedVectors(300)
        ko.add_vectors(names, np.vstack(rows))
        print("불러온 단어:", len(ko.index_to_key), "개")
        print("벡터가 있는 제주 단어:", [w for w in JEJU_WORDS if w in ko.key_to_index])
        print("벡터가 없는 제주 단어:", [w for w in JEJU_WORDS if w not in ko.key_to_index])
    """),
    md("""
        ### 1-6. 미리 학습된 벡터로 비슷한 단어 찾기

        사람이 예상하는 이웃이 나오는 단어와, 엉뚱한 이웃이 나오는 단어가 섞여 있습니다. 엉뚱한 이웃은 **그 단어가 웹 문서에서 어떤 글에 쓰였는지**를 보여 줍니다.

        - `하영` 은 제주어로 "많이"인데, 사람 이름으로도 많이 쓰입니다
        - `지슬` 은 제주어로 "감자"인데, 같은 제목의 영화가 있습니다
    """),
    code("""
        for word in ["한라산", "감귤", "고기국수", "오름", "하영", "지슬"]:
            top = [(w, round(float(s), 2)) for w, s in ko.most_similar(word, topn=5)]
            print(f"{word}: {top}")
    """),
    md("""
        ### 1-7. 단어로 계산하기

        벡터끼리 더하고 빼면 관계를 옮길 수 있다는 실험이 유명합니다. "서울에서 한국을 빼고 일본을 더하면" 일본의 수도가 나오는지 봅니다. 같은 방법이 늘 통하지는 않습니다. "왕에서 남자를 빼고 여자를 더하면" 무엇이 나오는지도 봅니다.
    """),
    code("""
        def analogy(plus, minus):
            top = ko.most_similar(positive=plus, negative=minus, topn=5)
            print(f"{' + '.join(plus)} - {' - '.join(minus)} -> {[(w, round(float(s), 2)) for w, s in top]}")

        analogy(["서울", "일본"], ["한국"])
        analogy(["왕", "여자"], ["남자"])

        ranked = [w for w, _ in ko.most_similar(positive=["왕", "여자"], negative=["남자"], topn=50)]
        print("여왕의 순위:", ranked.index("여왕") + 1 if "여왕" in ranked else "50위 밖")
    """),
    md("""
        ## 2. 한 지점만 바꿔 보기

        아래 셀의 `TODO` 로 표시된 **한 곳만** 바꾸고 다시 실행하세요.

        > 바꾸기 전 결과를 먼저 확인해 두면 무엇이 달라졌는지 비교할 수 있습니다.
    """),
    md("""
        따옴표 안에 궁금한 단어를 넣으면, 미리 학습된 벡터에서 가장 비슷한 단어 열 개를 보여 줍니다. 제주 지명, 향토 음식, 방언을 넣어 보고 **예상과 다른 결과**를 찾아보세요. 벡터가 없는 단어를 넣으면 그렇다고 알려 줍니다.
    """),
    code("""
        # TODO: 따옴표 안의 단어를 바꿔 보세요
        query = "서귀포"

        # 아래는 그대로 둡니다
        if query in ko.key_to_index:
            for rank, (w, s) in enumerate(ko.most_similar(query, topn=10), start=1):
                print(f"{rank:2d}. {w}  {s:.2f}")
        else:
            print(f"'{query}' 의 벡터가 없습니다. 웹 문서에 드물게 나왔거나 조사가 붙은 모양일 수 있습니다.")
    """),
    md("""
        ## 3. 확인 질문

        1. 1-3에서 `고기국수` 와 가장 비슷한 단어를 옮기고, 1-1의 틀 중 어느 것 때문에 그렇게 나왔는지 설명하세요.
        2. 1-6에서 `하영` 또는 `지슬` 의 이웃을 옮기고, 왜 그런 이웃이 나왔는지 말뭉치의 특성으로 설명하세요.
        3. TODO 셀에 단어 세 개를 넣어 보고, 예상과 다른 결과 하나를 골라 이유를 추측해 보세요.

        답은 아래 셀에 글로 적으면 됩니다. 코드가 아니어도 됩니다.
    """),
    md("""
        *(여기에 답을 적으세요)*
    """),
    md("""
        ## 4. 제출

        1. 상단 메뉴 **파일 > .ipynb 다운로드** 로 이 노트북을 내려받습니다
        2. [저장소](https://github.com/halla-ai/intronlp-2026)의 `assignments/week-07/<내 학번>/` 에 업로드합니다
        3. Pull Request를 엽니다

        자세한 방법은 강의 사이트의 **과제 제출** 문서에 있습니다.

        ---

        **막혔나요?** 오류 메시지의 마지막 줄을 먼저 읽어 보세요. 그래도 안 되면 AI Professor 튜터에게 묻고, 그래도 막히면 저장소 Issues에 남기세요.
    """),
]

nb = {
    "cells": cells,
    "metadata": {
        "colab": {"provenance": []},
        "kernelspec": {"display_name": "Python 3", "name": "python3"},
        "language_info": {"name": "python"},
    },
    "nbformat": 4,
    "nbformat_minor": 0,
}

NB_PATH.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(f"written: {NB_PATH}")

todo_cells = [c for c in cells if c["cell_type"] == "code" and "TODO" in c["source"]]
assert len(todo_cells) == 1, f"expected 1 TODO cell, got {len(todo_cells)}"
print("TODO cells: 1 (shape check passed)")

# execute in a fresh venv
with tempfile.TemporaryDirectory(prefix="week07-venv-") as workdir:
    work = Path(workdir)
    venv = work / "venv"
    subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
    py = venv / "bin" / "python"
    subprocess.run([
        str(py), "-m", "pip", "install", "-q", "--disable-pip-version-check",
        "ipykernel>=6.29,<7", "nbclient>=0.10,<1", "nbformat>=5.10,<6",
        "gensim>=4.3", "matplotlib>=3.7",
    ], check=True)

    script = (
        "import nbformat\n"
        "from nbclient import NotebookClient\n"
        "nb = nbformat.read(r'" + str(NB_PATH) + "', as_version=4)\n"
        "client = NotebookClient(nb, timeout=600, kernel_name='python3', allow_errors=False,\n"
        "                        resources={'metadata': {'path': r'" + str(work) + "'}})\n"
        "client.execute()\n"
        "print('EXECUTION OK')\n"
        "for i, c in enumerate(nb.cells):\n"
        "    if c.cell_type != 'code':\n"
        "        continue\n"
        "    for out in c.get('outputs', []):\n"
        "        if out.get('output_type') == 'stream':\n"
        "            print(f'--- cell {i} ---')\n"
        "            print(out.get('text', ''), end='')\n"
        "        elif out.get('output_type') == 'display_data' and 'image/png' in out.get('data', {}):\n"
        "            import base64\n"
        "            open(r'" + str(Path(tempfile.gettempdir()) / "week07-plot.png") + "', 'wb').write(base64.b64decode(out['data']['image/png']))\n"
        "            print(f'--- cell {i} --- [plot saved]')\n"
    )
    result = subprocess.run([str(py), "-c", script], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        sys.exit(1)
