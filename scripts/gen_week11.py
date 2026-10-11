#!/usr/bin/env python3
"""Generate the CPU-only week 11 notebook; generation itself needs no dependencies."""
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
        [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/halla-ai/intronlp-2026/blob/main/notebooks/week-11.ipynb)

        # 11주차 실습: 예시 유무와 일반·추론형 모델 비교

        **목표.** 제주 공개 안내를 근거로 답하는 두 공개 모델을 CPU에서 실행하고, few-shot 예시 유무와 답의 근거를 비교.

        기본값 그대로 전체 실행. 코드를 새로 작성하거나 모델을 학습하는 활동 없음. 선택 활동은 `use_examples` 한 곳의 True/False 변경. 영어 자료와 짧은 질문으로 무료 CPU 런타임 사용. 한국어 실무 성능 평가와 구분.

        원문: [제주관광공사 VisitJeju 올레 6코스 안내](https://m.visitjeju.net/en/detail/view?contentsid=CNTS_000000000020298), 열람 2026-10-11. 첫 절 `Jeju Olle Trail Route 6 is an 11-kilometer coastal and urban trail` 발췌 후 마침표 추가. 이 절에는 요금이 없으므로 요금 답의 기준은 UNKNOWN. 무료라고 추측하는 것도 근거 없는 답.

        원문은 9-10주차와 동일한 공개 발췌. 질문·출력 형식·few-shot 예시는 수업용 가공. 실제 후기나 기업 데이터 아님. [데이터 출처](https://intronlp-2026.halla.ai/reference/data/) 참조.

        같은 페이지의 상단 설명은 13.3km, 상세 본문은 11km로 표기가 다릅니다. 이 실습은 제공한 상세 본문 발췌에 대한 답을 확인하며 최신 코스 길이를 확정하지 않습니다. 원문 간 불일치는 추가 확인 전 판단 보류 대상입니다.
    '''),
    md('''
        ## 0. 준비

        처음 실행 시 모델 파일 총 수 GB 다운로드 필요. CPU 두 스레드, float32, 모델 한 개씩 로드. 수 분 이상 걸릴 수 있으므로 중복 실행 금지. 설치·다운로드 실패는 unavailable 표시 후 진행하며, 실제 결과를 대신 만들지 않음.
    '''),
    code('''
        import os
        import sys
        import subprocess
        import gc
        import time
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        os.environ["OMP_NUM_THREADS"] = "2"
        os.environ["HF_HUB_ETAG_TIMEOUT"] = "20"
        os.environ["HF_HUB_DOWNLOAD_TIMEOUT"] = "60"
        setup_error = None
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                            "torch>=2.6,<3", "transformers>=4.51,<5",
                            "safetensors>=0.4"], check=True, timeout=600)
            import torch
            import transformers
            from transformers import AutoTokenizer, AutoModelForCausalLM, set_seed
            torch.set_num_threads(2)
            print("device: cpu; threads: 2; dtype: float32")
            print("torch:", torch.__version__, "transformers:", transformers.__version__)
        except Exception as exc:
            setup_error = f"{type(exc).__name__}: {exc}"
            print("unavailable:", setup_error)
    '''),
    md('''
        ## 1. 공개 원문과 확인 기준

        아래 영어 공개 원문을 근거로 모델의 출력을 확인하는 실습.
    '''),
    code('''
        SOURCE = "Jeju Olle Trail Route 6 is an 11-kilometer coastal and urban trail."
        QUESTION = "How many kilometers is Route 6, and what is its admission fee?"
        RULE = ("Use only the source. If it does not state a value, write UNKNOWN. "
                "Reply in this format: KM=<number>; FEE=<value or UNKNOWN>. "
                "Then quote the short evidence from the source.")
        EXAMPLES = [
            {"role": "user", "content": "Source: " + SOURCE +
             "\\nQuestion: What route number is this, and what is its opening time?\\n" +
             "Reply: ROUTE=<number>; TIME=<value or UNKNOWN>. Quote evidence."},
            {"role": "assistant", "content":
             "ROUTE=6; TIME=UNKNOWN. Evidence: Jeju Olle Trail Route 6."},
            {"role": "user", "content": "Source: " + SOURCE +
             "\\nQuestion: Is the trail coastal or inland? Quote evidence."},
            {"role": "assistant", "content":
             "Coastal. Evidence: coastal and urban trail."},
        ]
        def messages(with_examples):
            turns = list(EXAMPLES) if with_examples else []
            return turns + [{"role": "user", "content":
                             "Source: " + SOURCE + "\\nQuestion: " + QUESTION + "\\n" + RULE}]
        print("공개 원문:", SOURCE)
        print("질문:", QUESTION)
        print("확인 기준: KM=11; FEE=UNKNOWN")
        print("근거: 11-kilometer. 발췌에 요금 기재 없음.")
    '''),
    md('''
        ## 2. 예시 유무 한 곳만 선택

        True이면 예시 두 개를 먼저 보여 주는 입력, False이면 예시 없는 입력 선택. 두 조건의 실제 결과를 모두 만들어 비교하고, 선택한 조건도 별도로 표시. 기본값 그대로 실행 가능. 변경 후 이 셀과 일반 모델 셀을 다시 실행하면 선택 표시가 바뀜.
    '''),
    code('''
        # TODO: True 또는 False 한 곳만 선택
        use_examples = True
        if not isinstance(use_examples, bool):
            print("선택값 확인: True/False 사용. 기본 True로 복구.")
            use_examples = True
        print("선택:", "few-shot" if use_examples else "zero-shot")
    '''),
    md('''
        ## 3. 일반 모델: 예시 없는 입력과 예시 있는 입력

        [Qwen2.5-0.5B-Instruct 모델 카드](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct), Apache-2.0. 완성된 모델의 추론만 실행. 모델 파일 버전 고정. 두 조건에서 질문과 원문·출력 규칙은 같고, 앞의 예시만 다름. 예시는 새 지식을 학습시키거나 모델 내부의 숫자를 바꾸는 작업이 아님.
    '''),
    code('''
        GENERAL = "Qwen/Qwen2.5-0.5B-Instruct"
        GENERAL_REVISION = "7ae557604adf67be50417f59c2c2f167def9a775"
        REASONING = "Qwen/Qwen3-0.6B"
        REASONING_REVISION = "c1899de289a04d12100db370d81485cdf75e47ca"

        def run_conditions(name, revision, conditions, thinking=False):
            if setup_error is not None:
                return {label: {"status": "unavailable", "error": setup_error}
                        for label in conditions}
            tokenizer = model = None
            results = {}
            try:
                tokenizer = AutoTokenizer.from_pretrained(name, revision=revision)
                model = AutoModelForCausalLM.from_pretrained(
                    name, revision=revision, torch_dtype=torch.float32,
                    use_safetensors=True).to("cpu")
                model.eval()
                for label, turns in conditions.items():
                    try:
                        options = {"enable_thinking": True} if thinking else {}
                        prompt = tokenizer.apply_chat_template(
                            turns, tokenize=False, add_generation_prompt=True, **options)
                        inputs = tokenizer(prompt, return_tensors="pt")
                        budget = 256 if thinking else 64
                        generation = {"do_sample": True, "temperature": 0.6,
                                      "top_p": 0.95, "top_k": 20} if thinking else {
                                      "do_sample": False}
                        set_seed(42)
                        start = time.monotonic()
                        with torch.inference_mode():
                            output = model.generate(**inputs, max_new_tokens=budget,
                                pad_token_id=tokenizer.eos_token_id, **generation)
                        ids = output[0, inputs["input_ids"].shape[-1]:].tolist()
                        raw = tokenizer.decode(ids, skip_special_tokens=True)
                        end_id = tokenizer.convert_tokens_to_ids("</think>") if thinking else None
                        has_end = thinking and end_id is not None and end_id in ids
                        ended = bool(ids and ids[-1] == tokenizer.eos_token_id)
                        limited = len(ids) >= budget and not ended
                        if thinking and has_end:
                            split = ids.index(end_id)
                            process = tokenizer.decode(ids[:split], skip_special_tokens=True)
                            answer = tokenizer.decode(ids[split + 1:], skip_special_tokens=True).strip()
                        elif thinking:
                            process, answer = raw, None
                        else:
                            process, answer = None, raw.strip()
                        result = {"status": "truncated" if limited or (thinking and not has_end)
                                  else "ok", "model": name, "revision": revision,
                                  "raw": raw, "visible_process": process, "answer": answer,
                                  "new_tokens": len(ids), "budget": budget,
                                  "seconds": round(time.monotonic() - start, 2),
                                  "thinking_closed": bool(has_end) if thinking else None}
                        results[label] = result
                        del output, inputs
                    except Exception as exc:
                        results[label] = {"status": "unavailable",
                                         "error": f"{type(exc).__name__}: {exc}"}
            except Exception as exc:
                results = {label: {"status": "unavailable",
                           "error": f"{type(exc).__name__}: {exc}"} for label in conditions}
            finally:
                del model, tokenizer
                gc.collect()
                print("모델 참조 해제:", name)
            return results

        general_results = run_conditions(GENERAL, GENERAL_REVISION,
                                          {"zero-shot": messages(False),
                                           "few-shot": messages(True)})
        for label, result in general_results.items():
            print(label, result)
        selected_label = "few-shot" if use_examples else "zero-shot"
        print("선택한 조건:", selected_label, general_results[selected_label])
    '''),
    md('''
        ## 4. 같은 질문을 추론형 모델에 입력

        일반 모델 메모리를 해제한 뒤 [Qwen3-0.6B 모델 카드](https://huggingface.co/Qwen/Qwen3-0.6B)의 thinking 모드 사용. Apache-2.0, `enable_thinking=True`. 모델 카드 권고에 따라 temperature=0.6, top_p=0.95, top_k=20의 샘플링 사용. seed=42는 비교를 위한 값이며 환경 간 완전한 동일성 보장 아님.

        예시 없는 동일 질문과 원문 사용. 일반 모델의 zero-shot과 대조. 최대 새 토큰 256개로 CPU 사용량 제한. 보이는 풀이가 길어도 내부 상태의 충실한 기록이라는 증거는 아님. 모델·크기·세대·생성 설정도 달라 추론형 방식 하나의 효과만 분리한 실험이 아님.

        `</think>` 전에 길이 제한에 도달하면 truncated, answer=None. 이때 visible_process는 도중 풀이이며 최종 답으로 채점하지 않음. 닫힘 표시 뒤의 답도 중간에 잘릴 수 있으므로 상태와 원문 출력 함께 확인.
    '''),
    code('''
        reasoning_results = run_conditions(REASONING, REASONING_REVISION,
                                            {"reasoning": messages(False)}, thinking=True)
        reasoning_result = reasoning_results["reasoning"]
        print("일반 zero-shot:", general_results["zero-shot"])
        print("추론형 동일 질문:", reasoning_result)
        print("확인 기준: KM=11; FEE=UNKNOWN, 근거는 11-kilometer")
        print("unavailable은 결과 없음, truncated는 불완전 출력. 정답으로 대체 금지.")
    '''),
    md('''
        ## 5. 확인 질문과 제출

        1. 일반 모델의 zero-shot과 few-shot에서 KM=11, FEE=UNKNOWN, 근거 인용이 각각 지켜졌는가? 바뀌지 않거나 더 나빠진 경우도 실제 출력 그대로 기록.
        2. 일반 모델과 추론형 모델의 동일 질문에서 최종 답, 보이는 풀이, 새 토큰 수의 차이는? truncated이면 최종 답 미완료로 기록. 긴 풀이 자체를 정확성의 증거로 사용하지 않음.
        3. 요금을 숫자나 무료로 답했다면 어떤 원문 근거가 있는가? 없다면 미확인으로 분류하고 공식 요금 자료 대조 전 안내 보류.

        실제 출력과 세 질문의 답을 포함한 노트북 제출. 제출 경로 `assignments/week-11/<학번>/`, 학번만 사용. unavailable이면 오류와 미완료 단계 표시 후 환경을 해결해 재실행. 출력은 실제 실행 결과만 사용. 현 실험의 소수 질문으로 모델 전체 성능이나 관광 업무 적합성 단정 금지.
    '''),
]
notebook = {'cells': cells, 'metadata': {'kernelspec': {'display_name': 'Python 3',
              'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python'}},
            'nbformat': 4, 'nbformat_minor': 0}
if __name__ == '__main__':
    (ROOT / 'notebooks/week-11.ipynb').write_text(
        json.dumps(notebook, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
