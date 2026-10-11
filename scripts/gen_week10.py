#!/usr/bin/env python3
"""Generate week 10 notebook without installing packages or downloading models."""
from pathlib import Path
from textwrap import dedent
import json

ROOT = Path(__file__).resolve().parents[1]


def md(text):
    return {'cell_type': 'markdown', 'metadata': {}, 'source': dedent(text).strip()}


def code(text):
    return {'cell_type': 'code', 'metadata': {}, 'source': dedent(text).strip(),
            'execution_count': None, 'outputs': []}


cells = [
    md('''
        [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/halla-ai/intronlp-2026/blob/main/notebooks/week-10.ipynb)

        # 10주차 실습: 사전학습 모델로 분류하고 이어 쓰기

        **목표.** 이미 학습된 영어 모델로 제주 관련 설명용 문장의 감정을 분류하고 짧은 글을 이어 씁니다. 모델을 학습시키지 않습니다. CPU만 사용하며, 필수 작업은 그대로 실행하고 결과 읽기입니다. 입력 문장 한 곳의 교체는 선택 활동입니다.

        영어를 쓰는 이유: 한국어 대형 모델 대신 비교적 작은 공개 영어 모델로 무료 CPU 환경에서 사용법을 확인하기 위함입니다. 한국어 실무 성능을 검증하는 실습은 아닙니다.

        기본 입력은 [제주관광공사 VisitJeju 올레 6코스 안내](https://m.visitjeju.net/en/detail/view?contentsid=CNTS_000000000020298)의 첫 절을 짧게 발췌한 `Jeju Olle Trail Route 6 is an 11-kilometer coastal and urban trail`입니다(열람 2026-10-11). 원문은 뒤에 경로 설명이 이어지며, 실습에서는 절 끝에 마침표를 추가했습니다. 이 발췌는 학습 과제의 입력이며 최신 운영 정보를 보증하지 않습니다.

        `wonderful`과 `not wonderful` 문장은 부정 표현을 비교하기 위해 사람이 작성한 통제 예시입니다. 공식 원문, 실제 관광객 후기, 기업 데이터가 아닙니다. [공개 데이터 출처](https://intronlp-2026.halla.ai/reference/data/)에서 원문과 사용 범위를 확인하세요.
    '''),
    md('''
        ## 0. 준비

        설치가 안 되더라도 아래 셀은 끝까지 진행하고, 모델 결과를 `unavailable`로 표시합니다. 이는 실행 흐름 확인이지 모델 추론 성공이 아닙니다. 성공 확인에는 1-2, 1-3, 2의 실제 출력이 필요합니다. 처음에는 수백 MB의 모델 파일을 내려받아 시간이 걸립니다.
    '''),
    code('''
        import os
        import sys
        import subprocess
        import gc

        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        os.environ["OMP_NUM_THREADS"] = "2"
        os.environ["HF_HUB_ETAG_TIMEOUT"] = "20"
        os.environ["HF_HUB_DOWNLOAD_TIMEOUT"] = "60"
        setup_error = None
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-q",
                 "torch>=2.6,<3", "transformers>=4.48,<5", "safetensors>=0.4"],
                check=True, timeout=600,
            )
            import torch
            from transformers import pipeline
            torch.set_num_threads(2)
        except Exception as exc:
            setup_error = f"{type(exc).__name__}: {exc}"
            print("설치/불러오기 unavailable:", setup_error)
    '''),
    md('''
        ## 1-1. 모델의 과제부터 확인

        | 용도 | 공개 모델 | 학습된 과제 | 라이선스 |
        |---|---|---|---|
        | 분류 | distilbert/distilbert-base-uncased-finetuned-sst-2-english | 영어 영화평의 긍정/부정(SST-2) | Apache-2.0 |
        | 생성 | distilbert/distilgpt2 | 영어 글의 다음 토큰 예측 | Apache-2.0 |

        [분류 모델 카드](https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english), [생성 모델 카드](https://huggingface.co/distilbert/distilgpt2). 모델 버전을 고정해 같은 파일을 사용합니다. 분류기는 BERT 계열의 경량 모델을 감정분류에 이미 미세조정한 것입니다. 관광 주제 분류기가 아닙니다.
    '''),
    code('''
        CLASSIFIER = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
        CLASSIFIER_REVISION = "714eb0fa89d2f80546fda750413ed43d93601a13"
        GENERATOR = "distilbert/distilgpt2"
        GENERATOR_REVISION = "2290a62682d06624634c1f46a6ad5be0f47f38aa"

        def load_model(task, name, revision):
            if setup_error is not None:
                return None, setup_error
            try:
                return pipeline(task, model=name, revision=revision, device=-1,
                                model_kwargs={"use_safetensors": True}), None
            except Exception as exc:
                return None, f"{type(exc).__name__}: {exc}"

        def classify(text):
            model, error = load_model("sentiment-analysis", CLASSIFIER, CLASSIFIER_REVISION)
            if model is None:
                return {"status": "unavailable", "error": error}
            try:
                output = model(text, truncation=True, max_length=128)[0]
                return {"status": "ok", "label": output["label"], "score": output["score"]}
            except Exception as exc:
                return {"status": "unavailable", "error": f"{type(exc).__name__}: {exc}"}
            finally:
                del model
                gc.collect()

        def continue_text(text):
            model, error = load_model("text-generation", GENERATOR, GENERATOR_REVISION)
            if model is None:
                return {"status": "unavailable", "error": error}
            try:
                output = model(text, max_new_tokens=32, do_sample=False,
                               pad_token_id=model.tokenizer.eos_token_id,
                               return_full_text=False)[0]["generated_text"]
                return {"status": "ok", "continuation": output}
            except Exception as exc:
                return {"status": "unavailable", "error": f"{type(exc).__name__}: {exc}"}
            finally:
                del model
                gc.collect()
    '''),
    md('''
        ## 1-2. 제주 관련 예시 문장의 감정 분류

        공식 안내의 발췌 문장과 사람이 작성한 감정 통제 예시 두 개를 비교합니다. 문장이 긍정/부정을 나타내는지 사람이 먼저 예상하세요. `score`는 이 모델의 두 라벨 중 선택한 라벨에 부여한 점수입니다. 실제 정확도, 관광지 품질, 중립 여부를 알려 주지 않습니다. 이 모델에는 `NEUTRAL` 라벨이 없습니다.
    '''),
    code('''
        examples = [
            "Jeju Olle Trail Route 6 is an 11-kilometer coastal and urban trail.",
            "The walk by the sea in Jeju was wonderful.",
            "The walk by the sea in Jeju was not wonderful.",
        ]
        classification_results = []
        for text in examples:
            result = classify(text)
            classification_results.append({"text": text, **result})
            print(text)
            print(result)
        print("주의: 중립 문장도 두 라벨 중 하나로 분류됩니다. score는 정확도가 아닙니다.")
    '''),
    md('''
        ## 1-3. 문장의 뒤를 이어 쓰기

        공식 안내의 발췌 문장을 시작 문장으로 사용합니다. 실제 원문의 다음 문장을 복원하는 실습이 아니며, 이어 쓴 부분은 모델의 새로운 출력입니다. 분류 모델 메모리를 해제한 뒤 생성 모델을 불러옵니다. 최대 32개의 새 토큰만 생성합니다. `do_sample=False`는 매 단계에서 가장 높은 점수의 토큰을 고르는 설정입니다. 계속 같은 말을 반복하거나 제주와 무관한 글을 쓸 수 있습니다.

        출력에는 입력 뒤에 새로 붙은 부분만 나옵니다. 이것은 질문에 답하는 대화 모델이 아니라 글을 이어 쓰는 모델입니다. 주소, 운영시간, 교통편 등이 나오면 공식 자료와 대조하기 전에는 확인되지 않은 주장입니다.
    '''),
    code('''
        prompt = "Jeju Olle Trail Route 6 is an 11-kilometer coastal and urban trail."
        generation_result = continue_text(prompt)
        print("입력:", prompt)
        print("생성:", generation_result)
        print("생성된 내용은 사실 검증 전 관광 안내로 사용하지 않습니다.")
    '''),
    md('''
        ## 2. 한 지점만 바꿔 보기

        선택 활동입니다. 바꾸려면 아래의 입력 문장만 바꾸세요. 기본값 그대로도 실행됩니다. 제주 관련 짧은 영어 문장을 사용해 같은 입력의 감정 라벨과 이어쓰기를 비교하세요. 위의 세 문장을 복사해도 됩니다. 이 셀을 여러 번 실행해 비교하되, 다른 코드는 바꾸지 않습니다.
    '''),
    code('''
        # TODO: 아래 따옴표 안의 입력 문장 하나만 바꿔 보세요
        student_text = "Jeju Olle Trail Route 6 is an 11-kilometer coastal and urban trail."

        # 아래 코드는 그대로 둡니다
        print("내 입력:", student_text)
        if not isinstance(student_text, str) or not student_text.strip() or len(student_text) > 300:
            print("입력 확인: 1~300자의 짧은 영어 문장을 넣으세요.")
        else:
            student_classification = classify(student_text)
            student_generation = continue_text(student_text)
            print("감정 분류:", student_classification)
            print("새로 이어 쓴 부분:", student_generation)
            print("score는 정확도가 아니며, 이어 쓴 부분의 사실성도 보장하지 않습니다.")
    '''),
    md('''
        ## 3. 확인 질문

        1. `wonderful`과 `not wonderful`의 실제 라벨/점수를 기록하고, 예상과 비교하세요. 실패했다면 `unavailable`과 오류 마지막 줄을 기록하세요. 숫자를 만들어 채우지 않습니다.
        2. 중립 설명문이 긍정/부정 중 하나가 된 이유를 모델의 라벨 목록과 학습 과제로 설명하세요.
        3. 선택 활동을 했다면 내 문장을 바꾼 전후의 라벨과 이어 쓴 부분을 기록하세요. 바꾸지 않았다면 기본 입력의 분류 결과와 이어 쓴 부분을 기록하세요. 생성문에서 공식 출처를 대조해야 하는 주장을 찾거나, 그런 주장이 없다면 없다고 기록하세요.
        4. 중간 프로젝트에서 필요한 과제와 이 모델의 학습 과제가 같은지 설명하세요. 다음 수정은 데이터 정리, 모델 선택, 사람 검토 중 하나로 제안하세요.
    '''),
    md('*(여기에 답을 적으세요)*'),
    md('''
        ## 4. 제출

        실행 결과와 답을 포함한 노트북을 내려받아 `assignments/week-10/<학번>/`에 업로드하고 Pull Request를 엽니다. 이름과 연락처는 폴더에 넣지 않습니다. 제출 방법은 강의 사이트의 과제 제출 안내를 참고하세요.

        `unavailable`만 나온 경우는 모델 실험 미완료입니다. 오류 기록을 보존하고 연결/설치 문제를 해결한 뒤 1-2부터 다시 실행하세요. 후속 셀이 끝났다는 사실과 모델 추론 성공을 구분합니다.
    '''),
]
assert sum(c['cell_type'] == 'code' and 'TODO' in c['source'] for c in cells) == 1
nb = {'cells': cells, 'metadata': {'colab': {'provenance': []},
      'kernelspec': {'display_name': 'Python 3', 'name': 'python3'},
      'language_info': {'name': 'python'}}, 'nbformat': 4, 'nbformat_minor': 0}
path = ROOT / 'notebooks/week-10.ipynb'
path.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print(f'written: {path}; TODO cells: 1')
