#!/usr/bin/env python3
"""Generate notebooks/week-05.ipynb and execute it in a fresh venv to verify."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB_PATH = ROOT / "notebooks" / "week-05.ipynb"

# review corpus (examples) - positive 5 / negative 5
POS = [
    "바다가 보이는 객실이 정말 좋았다",
    "조식이 맛있고 직원들이 친절했다",
    "숙소가 깨끗하고 뷰가 아주 좋았다",
    "위치가 좋고 객실이 넓었다",
    "가격 대비 만족스러운 숙박이었다",
]
NEG = [
    "방에서 냄새가 나서 힘들었다",
    "직원이 불친절하고 방이 더러웠다",
    "소음이 심해서 잠을 못 잤다",
    "에어컨이 고장 나서 불편했다",
    "사진과 다르고 좁고 낡았다",
]
TODO_DEFAULT = "객실이 넓고 조식이 맛있었다"

md = lambda t: {"cell_type": "markdown", "metadata": {}, "source": t}
code = lambda t: {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": t}

cells = [
    md("[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]"
       "(https://colab.research.google.com/github/halla-ai/intronlp-2026/blob/main/notebooks/week-05.ipynb)\n"
       "\n"
       "# 5주차 실습: 리뷰를 긍정과 부정으로 분류하기\n"
       "\n"
       "**목표.** 손으로 만든 감성 분류기로 리뷰 문장을 긍정과 부정으로 분류해 보고, "
       "모델이 어떤 단어를 보고 판단했는지 확인한다."),
    md("## 0. 준비\n"
       "\n"
       "분류 라이브러리 scikit-learn과 표를 보여 줄 pandas를 설치합니다. Colab에는 이미 설치되어 있어 바로 넘어갑니다.\n"
       "\n"
       "설치 셀에서 오류가 나면 다음 셀로 넘어가지 말고 오류의 마지막 줄을 확인하세요."),
    code("%pip -q install \"scikit-learn>=1.3\" \"pandas>=1.5.3\""),
    code("import sys\n"
         "from importlib.metadata import version\n"
         "import sklearn\n"
         "import numpy\n"
         "import pandas\n"
         "\n"
         "print(\"Python:\", sys.version.split()[0])\n"
         "print(\"scikit-learn:\", sklearn.__version__)\n"
         "print(\"NumPy:\", numpy.__version__)\n"
         "print(\"pandas:\", pandas.__version__)\n"
         "print(\"설치 확인 끝\")"),
    md("## 1. 먼저 그냥 실행해 보기\n"
       "\n"
       "아래 셀들을 위에서부터 차례로 실행하세요. 아무것도 고치지 않아도 끝까지 돌아갑니다.\n"
       "\n"
       "이 노트북의 리뷰 문장은 **설명용 예시**입니다. 관광 빅데이터 같은 진짜 데이터는 로그인이 필요해서 "
       "노트북에 넣을 수 없고, 여기서는 문장 열 개로 작은 말뭉치를 직접 만듭니다."),
    md("### 1-1. 긍정 5건, 부정 5건\n"
       "\n"
       "긍정 리뷰 다섯 문장과 부정 리뷰 다섯 문장을 나란히 놓아 봅니다."),
    code("positive = " + json.dumps(POS, ensure_ascii=False, indent=4).replace("\n]", "    ]") + "\n"
         "negative = " + json.dumps(NEG, ensure_ascii=False, indent=4).replace("\n]", "    ]") + "\n"
         "\n"
         "print(\"긍정 리뷰\", len(positive), \"건\")\n"
         "for s in positive:\n"
         "    print(\" \", s)\n"
         "print(\"부정 리뷰\", len(negative), \"건\")\n"
         "for s in negative:\n"
         "    print(\" \", s)"),
    md("### 1-2. 문장을 단어 가방으로 (Bag-of-Words)\n"
       "\n"
       "강의 1에서 본 단어 가방입니다. 문장을 띄어쓰기로 잘라 각 단어가 몇 번 나왔는지 세고, "
       "문장에서 단어 순서는 버립니다.\n"
       "\n"
       "`CountVectorizer` 는 기본 설정에서 **두 글자 이상인 단어만 남기고 한 글자짜리 단어를 버립니다.** "
       "그런데 한국어에서는 `못`, `안`, `잘` 처럼 판단에 중요한 말이 한 글자입니다. 그래서 한 글자 단어도 남기도록 설정을 하나 바꿉니다.\n"
       "\n"
       "**2주차에서 본 문제가 다시 나옵니다.** 띄어쓰기 단위로 자르기 때문에 `좋았다` 와 `좋은` 은 다른 단어가 되고, "
       "`객실이` 는 조사가 붙은 하나의 단어로 셉니다. 그래서 어미와 조사가 다르면 같은 뜻의 말도 다른 단어로 취급됩니다.\n"
       "\n"
       "표의 한 줄이 리뷰 한 건, 한 칸이 단어 하나입니다. 칸 대부분이 0인 것이 정상입니다. 리뷰 한 건에는 전체 단어 중 몇 개만 나오기 때문입니다."),
    code("reviews = positive + negative\n"
         "labels = [1] * len(positive) + [0] * len(negative)\n"
         "\n"
         "from sklearn.feature_extraction.text import CountVectorizer\n"
         "\n"
         "# 한 글자 단어(못, 안, 잘)도 버리지 않도록 자르는 규칙을 바꾼다\n"
         "vectorizer = CountVectorizer(token_pattern=r\"(?u)\\b\\w+\\b\")\n"
         "X = vectorizer.fit_transform(reviews)\n"
         "\n"
         "import pandas as pd\n"
         "vocab = vectorizer.get_feature_names_out()\n"
         "print(\"단어 가방:\", X.shape[0], \"문장 x\", X.shape[1], \"단어\")\n"
         "pd.DataFrame(X.toarray(), columns=vocab, index=[f\"리뷰{i+1}\" for i in range(len(reviews))])"),
    md("### 1-3. 분류기 학습시키기\n"
       "\n"
       "가방 위의 각 단어에 점수를 매기는 것이 로지스틱 회귀 분류기입니다. "
       "모든 점수를 0에서 출발시킨 뒤, 학습 리뷰를 맞히도록 **틀린 만큼 조금씩 고치는 일**을 여러 번 되풀이합니다. "
       "그 결과 긍정 리뷰에만 나온 단어는 + 점수를, 부정 리뷰에만 나온 단어는 - 점수를 받습니다.\n"
       "\n"
       "단어 점수와 별도로 **기본 점수**가 하나 있습니다. 문장에 아는 단어가 하나도 없을 때 남는 점수입니다.\n"
       "\n"
       "**학습 문장을 다시 보고 맞히는 것**이라 정확도가 높게 나오는 것이 정상입니다. "
       "보지 못한 새 문장에서 어떻게 되는지는 1-5에서 봅니다."),
    code("from sklearn.linear_model import LogisticRegression\n"
         "\n"
         "model = LogisticRegression()\n"
         "model.fit(X, labels)\n"
         "\n"
         "print(\"학습 문장 정확도:\", model.score(X, labels))\n"
         "print(\"기본 점수:\", round(float(model.intercept_[0]), 2))"),
    md("### 1-4. 어떤 단어에 어떤 점수가 매겨졌나\n"
       "\n"
       "점수가 가장 높은 단어 여덟 개와 가장 낮은 단어 여덟 개를 봅니다. "
       "긍정 리뷰와 부정 리뷰에서 각각 자주 나온 말이 리스트에 오는지 확인하세요.\n"
       "\n"
       "**맨 위의 단어를 눈여겨보세요.** `객실이` 나 `나서` 처럼 감정과 상관없는 말이 가장 큰 점수를 받습니다. "
       "`객실이` 는 긍정 리뷰 두 건에, `나서` 는 부정 리뷰 두 건에 나왔기 때문입니다. "
       "모델은 단어의 뜻을 모르고, **어느 쪽 리뷰에 나왔는지**만 압니다."),
    code("weights = pd.Series(model.coef_[0], index=vocab)\n"
         "print(\"긍정 쪽으로 미는 단어 (점수가 가장 높은 여덟 개)\")\n"
         "print(weights.sort_values(ascending=False).head(8))\n"
         "\n"
         "print()\n"
         "print(\"부정 쪽으로 미는 단어 (점수가 가장 낮은 여덟 개)\")\n"
         "print(weights.sort_values().head(8))"),
    md("### 1-5. 새 문장 예측하기\n"
       "\n"
       "학습에 쓰지 않은 새 문장을 넣어 봅니다. `predict_proba` 는 긍정일 확률을 알려 줍니다. "
       "새 문장마다 사람이 붙인 정답도 적어 두고, **처음 보는 문장을 몇 개나 맞히는지** 잽니다. 이것이 분류기의 진짜 실력입니다.\n"
       "\n"
       "세 번째 문장을 눈여겨보세요. `예쁘고` , `감성적인` , `숙소였다` 는 모두 학습 자료에 없던 단어입니다. "
       "학습에서 본 적이 없으니 점수도 없고, 판단에 아무 영향을 주지 않습니다. 사람에게는 명백히 긍정처럼 읽히는 문장인데도 "
       "**단어 가방에 없는 말은 분류기의 눈에 보이지 않아** 판단 근거가 없어 0.5 근처에 머뭅니다. "
       "기본 점수만 남아 0.5보다 조금 낮게 나오고, 그래서 판정은 부정으로 틀립니다."),
    code("new_reviews = [\n"
         "    \"객실이 좋았다\",\n"
         "    \"방이 더러웠다\",\n"
         "    \"예쁘고 감성적인 숙소였다\",\n"
         "]\n"
         "new_labels = [1, 0, 1]  # 사람이 붙인 정답 (1 = 긍정, 0 = 부정)\n"
         "\n"
         "X_new = vectorizer.transform(new_reviews)\n"
         "proba = model.predict_proba(X_new)[:, 1]\n"
         "\n"
         "for s, p in zip(new_reviews, proba):\n"
         "    print(f\"{s} -> 긍정 확률 {p:.2f}\")\n"
         "\n"
         "print()\n"
         "print(\"새 문장 정확도:\", round(model.score(X_new, new_labels), 2))\n"
         "print()\n"
         "print(\"단어 가방에 '예쁘고'가 있나?\", '예쁘고' in vectorizer.vocabulary_)\n"
         "print(\"단어 가방에 '감성적인'이 있나?\", '감성적인' in vectorizer.vocabulary_)"),
    md("## 2. 한 지점만 바꿔 보기\n"
       "\n"
       "아래 셀의 `TODO` 로 표시된 **한 곳만** 바꾸고 다시 실행하세요.\n"
       "\n"
       "> 바꾸기 전 결과를 먼저 확인해 두면 무엇이 달라졌는지 비교할 수 있습니다."),
    md("따옴표 안에 내 리뷰 문장을 넣습니다. 긍정 같은 문장, 부정 같은 문장, 애매한 문장을 하나씩 넣어 보세요. "
       "애매한 문장이 어떤 확률로 나오는지 눈여겨보세요.\n"
       "\n"
       "출력의 마지막 줄은 **판정에 쓰인 단어와 그 점수**입니다. 가방에 없는 단어는 이 목록에 나오지 않습니다. "
       "`직원이 친절했다` 와 `직원들이 친절했다` 처럼 조사만 다른 두 문장을 넣어 비교해 보는 것도 좋습니다."),
    code("# TODO: 따옴표 안의 리뷰 문장을 바꿔 보세요\n"
         "my_review = \"" + TODO_DEFAULT + "\"\n"
         "\n"
         "# 아래는 그대로 둡니다\n"
         "x = vectorizer.transform([my_review])\n"
         "p = model.predict_proba(x)[0, 1]\n"
         "verdict = \"긍정\" if p >= 0.5 else \"부정\"\n"
         "print(f\"내 리뷰: {my_review}\")\n"
         "print(f\"판정: {verdict} (긍정 확률 {p:.2f})\")\n"
         "\n"
         "counts = x.toarray()[0]\n"
         "used = [(vocab[i], round(float(n * model.coef_[0][i]), 2)) for i, n in enumerate(counts) if n > 0]\n"
         "used.sort(key=lambda t: -abs(t[1]))\n"
         "print(\"판정에 쓰인 단어와 점수:\", used if used else \"없음. 모두 가방에 없는 단어라 기본 점수만 남았다\")"),
    md("## 3. 확인 질문\n"
       "\n"
       "1. 1-4의 긍정 쪽 단어 여덟 개와 부정 쪽 단어 여덟 개를 옮겨 적으세요. 그중 **감정과 상관없는 단어**를 하나 골라, 왜 그 단어가 점수를 받았는지 1-1의 리뷰에서 찾아 설명하세요.\n"
       "2. 2의 내 리뷰 문장과 판정, 긍정 확률을 옮기고, 판정에 관여한 단어 중 근거가 된다고 생각하는 것 하나를 고르세요.\n"
       "3. 1-5에서 `예쁘고` 가 판정에 영향을 주지 않았습니다. 왜 그런가요? 이런 한계를 줄이려면 무엇이 필요할까요?\n"
       "\n"
       "답은 아래 셀에 글로 적으면 됩니다. 코드가 아니어도 됩니다."),
    md("*(여기에 답을 적으세요)*"),
    md("## 4. 제출\n"
       "\n"
       "1. 상단 메뉴 **파일 > .ipynb 다운로드** 로 이 노트북을 내려받습니다\n"
       "2. [저장소](https://github.com/halla-ai/intronlp-2026)의 `assignments/week-05/<내 학번>/` 에 업로드합니다\n"
       "3. Pull Request를 엽니다\n"
       "\n"
       "자세한 방법은 강의 사이트의 **과제 제출** 문서에 있습니다.\n"
       "\n"
       "---\n"
       "\n"
       "**막혔나요?** 오류 메시지의 마지막 줄을 먼저 읽어 보세요. 그래도 안 되면 AI Professor 튜터에게 묻고, "
       "그래도 막히면 저장소 Issues에 남기세요."),
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

todo_cells = [c for c in cells if c["cell_type"] == "code" and "TODO" in (c["source"] if isinstance(c["source"], str) else "")]
assert len(todo_cells) == 1, f"expected 1 TODO cell, got {len(todo_cells)}"
print("TODO cells: 1 (shape check passed)")

# execute in a fresh venv
with tempfile.TemporaryDirectory(prefix="week05-venv-") as workdir:
    work = Path(workdir)
    venv = work / "venv"
    subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
    py = venv / "bin" / "python"
    subprocess.run([
        str(py), "-m", "pip", "install", "-q", "--disable-pip-version-check",
        "ipykernel>=6.29,<7", "nbclient>=0.10,<1", "nbformat>=5.10,<6",
        "scikit-learn>=1.3", "pandas>=1.5.3",
    ], check=True)

    script = (
        "import nbformat\n"
        "from nbclient import NotebookClient\n"
        "nb = nbformat.read(r'" + str(NB_PATH) + "', as_version=4)\n"
        "client = NotebookClient(nb, timeout=300, kernel_name='python3', allow_errors=False)\n"
        "client.execute()\n"
        "print('EXECUTION OK')\n"
        "for i, c in enumerate(nb.cells):\n"
        "    if c.cell_type != 'code':\n"
        "        continue\n"
        "    for out in c.get('outputs', []):\n"
        "        if out.get('output_type') == 'stream':\n"
        "            print(f'--- cell {i} ---')\n"
        "            print(out.get('text', ''), end='')\n"
    )
    result = subprocess.run([str(py), "-c", script], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        sys.exit(1)
