# 12주차 프롬프트 엔지니어링 미니 프로젝트

- 학번: 202021023
- 실행 날짜: 2026-11-14
- 이 파일은 보고서·발표 기록 양식이며 실행 노트북이 아님
- 실제 결과만 기록, 미실행 항목은 미실행으로 표시
- 실행 방법: 11주차 노트북을 끝까지 실행한 뒤 12주차 강의자료의 제공된 실행 셀을 마지막 새 코드 셀에 그대로 복사·실행
- 코드 수정·새 TODO·별도 12주차 노트북 작성 없음
- 출력 키 A1/B1, A2/B2, A3/B3를 아래 같은 번호 질문에 연결
- ok는 실제 출력 대조, truncated는 불완전 출력 표시, unavailable은 오류와 미실행 상태 기록

## 목적과 공개 자료

- 목적: 공개 제주 안내를 근거로 방문자의 질문에 답변
- H 출처: https://www.visitjeju.net/en/detail/view?contentsid=CONT_000000000500685
- O 출처: https://m.visitjeju.net/en/detail/view?contentsid=CNTS_000000000020298
- 제공 발췌 열람일: 2026-10-11
- 가공: H의 제목 `Hallasan.` 추가, O의 첫 절 발췌 후 마침표 추가
- 추가 열람·가공 여부: 없음. 제공된 실행 셀의 두 발췌 문자열을 그대로 썼다. 원문 페이지는 다시 열람하지 않았다.
- 참고: 강의자료에 따르면 올레 페이지 상단 설명은 13.3km, 상세 본문은 11km다. 이 실험은 제공 발췌의 11km만 대조한다. 최신 코스 길이는 판단 보류다.

## 고정 조건

- 모델 ID·버전: `Qwen/Qwen2.5-0.5B-Instruct`, revision `7ae557604adf67be50417f59c2c2f167def9a775`. 11주차 일반 모델(`GENERAL`, `GENERAL_REVISION`)과 같다.
- 실행 환경·라이브러리 버전: 로컬 CPU(macOS, Apple M1), Python 3.12.13, torch 2.15.0, transformers 4.57.6, float32, CPU 스레드 2. 강의자료 검증 환경(Torch 2.14.1·Transformers 4.57.6)과 torch 버전이 다르다.
- 생성 설정·출력 길이 제한: `do_sample=False`, `max_new_tokens=64`, `set_seed(42)`. 11주차 `run_conditions`의 일반 모델 설정을 그대로 썼다. 모델 기본 생성 설정의 temperature·top_p·top_k는 무시된다는 경고가 출력됐다.
- 입력 형식: 조건마다 user 메시지 하나를 `apply_chat_template`으로 넣었다. 이 모델의 템플릿은 기본 system 문장 `You are Qwen, created by Alibaba Cloud. You are a helpful assistant.`를 앞에 붙인다. A와 B에 똑같이 붙는다.
- 공통 자료·공통 질문: 주차 강의자료와 동일, 변경 없음
- 이전 대화 포함 여부: 새 입력으로 각각 실행
- 실행 상태: 완료. 6개 조건 모두 `status: ok`
- 다운로드 오류·출력 잘림 등: 없음. 새 토큰 수는 A1 48, B1 54, A2 36, B2 30, A3 3, B3 28로 모두 상한 64 미만이다.

## 프롬프트 A와 B

- A: 강의자료의 공통 골격을 복사하고 각 질문으로 실행
- B: 같은 골격에서 질문 앞에 확인 불가 형식 예시 한 개만 추가
- 실제 사용한 A 프롬프트(A1 전문, A2·A3는 `Question:` 줄만 다름):

```text
Purpose: Answer a visitor's question using only the supplied sources.
Sources:
[H] Hallasan. At 1,950 m above sea level, it is the highest mountain in South Korea.
[O] Jeju Olle Trail Route 6 is an 11-kilometer coastal and urban trail.
Rules: Do not add facts absent from the sources.
If the sources do not answer the question, write "Not stated".
Format: Answer | Source ID | Evidence
Question: How high is Hallasan above sea level?
Answer:
```

- 실제 사용한 B 프롬프트(B1 전문, B2·B3는 `Question:` 줄만 다름):

```text
Purpose: Answer a visitor's question using only the supplied sources.
Sources:
[H] Hallasan. At 1,950 m above sea level, it is the highest mountain in South Korea.
[O] Jeju Olle Trail Route 6 is an 11-kilometer coastal and urban trail.
Rules: Do not add facts absent from the sources.
If the sources do not answer the question, write "Not stated".
Format: Answer | Source ID | Evidence
Example:
Question: What is the admission fee for Hallasan?
Answer: Not stated | None | The supplied sources do not state a fee.
Question: How high is Hallasan above sea level?
Answer:
```

- 질문 줄: 1 `How high is Hallasan above sea level?`, 2 `How long is Jeju Olle Trail Route 6?`, 3 `How many hours does it take to walk Route 6?`
- A와 B의 차이: `Format:` 줄과 `Question:` 줄 사이의 `Example:` 세 줄뿐이다.

## 실제 출력과 원문 근거

| 질문 | A 실제 출력 | B 실제 출력 | 원문 표현 | 판단 |
|---|---|---|---|---|
| How high is Hallasan above sea level? | `Answer: Hallasan is at 1,950 meters above sea level.\n\nSource ID: [H]\nEvidence: Hallasan is described as being at 1,950 meters above sea level in its official description.` | `Answer: Hallasan at 1,950 meters above sea level is the highest mountain in South Korea.\n\nSource ID: [H]\nEvidence: Hallasan is described as being at 1,950 meters above sea level in the provided sources.` | H: `At 1,950 m above sea level` | A1·B1 확인. 숫자 1,950과 단위(m, meters)가 H와 일치한다. 둘 다 세 항목을 줄로 나눠 적어 `\|` 구분 형식은 아니다. A1 Evidence의 `in its official description`은 입력에 없는 출처 설명이다. B1이 덧붙인 `the highest mountain in South Korea`는 H에 있는 내용이다. |
| How long is Jeju Olle Trail Route 6? | `Answer: 11 kilometers\n\nSource ID: O\nEvidence: Jeju Olle Trail Route 6 is an 11-kilometer coastal and urban trail.` | `Answer: Not stated \| O \| Sources indicate that Jeju Olle Trail Route 6 is 11 kilometers long.\nSource ID: O` | O: `11-kilometer` | A2 확인. `11 kilometers`가 O와 일치하고 Evidence는 O 문장을 그대로 인용했다. B2 불일치. 답 칸은 `Not stated`인데 Evidence에는 `11 kilometers long`이 있어 출력 안에서 서로 모순된다. |
| How many hours does it take to walk Route 6? | `Not stated` | `Answer: Not stated \| O \| Sources indicate that Route 6 takes approximately 3-4 hours to complete.\nSource ID: O` | 두 발췌에 소요시간 없음 | A3 확인 불가 처리. 보류 내용은 맞지만 Source ID·Evidence가 없어 형식 미준수다. B3 추측 추가. 답 칸은 `Not stated`지만 Evidence에 O에 없는 `approximately 3-4 hours`를 넣고 출처 O를 붙였다. 3-4시간의 실제 여부는 미확인이다. |

- 긴 출력은 아래에 전문 기록하고 표에는 연결 표시
- 확인 기준: 숫자·단위·출처 ID의 실제 원문 대조
- Answer·Source ID·Evidence는 모델에게 요청한 출력 항목, 판단은 사람이 대조한 뒤 적는 항목
- 자료에 없는 걷는 시간: 확인 불가 처리 여부 점검
- Not stated는 제공 발췌에 기재 없음, 실제 시간이 0이거나 해당 정보가 존재하지 않는다는 판정과 구분
- 근거 없는 내용을 예상 정답으로 채우지 않는 원칙
- 표의 출력은 노트북에 출력된 `raw` 값이다. `\n`은 줄바꿈이고, 표 안의 `\|`는 출력의 `|`다. 6개 조건 모두 `answer`와 `raw`가 같다.

### 출력 전문

A1 (`status: ok`, 새 토큰 48/64, 5.81초):

```text
Answer: Hallasan is at 1,950 meters above sea level.

Source ID: [H]
Evidence: Hallasan is described as being at 1,950 meters above sea level in its official description.
```

B1 (`status: ok`, 새 토큰 54/64, 5.06초):

```text
Answer: Hallasan at 1,950 meters above sea level is the highest mountain in South Korea.

Source ID: [H]
Evidence: Hallasan is described as being at 1,950 meters above sea level in the provided sources.
```

A2 (`status: ok`, 새 토큰 36/64, 3.28초):

```text
Answer: 11 kilometers

Source ID: O
Evidence: Jeju Olle Trail Route 6 is an 11-kilometer coastal and urban trail.
```

B2 (`status: ok`, 새 토큰 30/64, 2.59초):

```text
Answer: Not stated | O | Sources indicate that Jeju Olle Trail Route 6 is 11 kilometers long.
Source ID: O
```

A3 (`status: ok`, 새 토큰 3/64, 0.38초):

```text
Not stated
```

B3 (`status: ok`, 새 토큰 28/64, 2.3초):

```text
Answer: Not stated | O | Sources indicate that Route 6 takes approximately 3-4 hours to complete.
Source ID: O
```

## 비교와 해석

- 내용이 원문과 일치하는지: A1·B1·A2는 숫자·단위가 원문과 일치했다. B2는 원문에 거리가 있는데 답 칸에 `Not stated`를 적었다. A3는 시간을 만들지 않았다. B3는 원문에 없는 3-4시간을 근거 칸에 넣었다.
- 지정 형식을 지키는지: `Answer | Source ID | Evidence`를 한 줄 `|` 구분으로 따른 출력은 B2·B3다. 두 출력 모두 끝에 `Source ID: O` 줄을 한 번 더 붙였다. A1·A2·B1은 세 항목을 줄로 나눠 적었다. A3는 `Not stated`만 적어 Source ID·Evidence가 없다.
- 자료 밖 정보를 추가했는지: B3의 `approximately 3-4 hours`가 자료 밖 정보다. A1의 `in its official description`도 입력에 없는 출처 설명이다. B1의 `highest mountain`은 H에 있어 자료 밖 정보가 아니다.
- A/B의 구체적인 차이 또는 차이 없음:
  - 질문 1: 답의 숫자는 같다. B1은 H의 `highest mountain` 내용을 덧붙였다. Evidence의 출처 설명은 A1 `in its official description`에서 B1 `in the provided sources`로 바뀌었다. 형식은 둘 다 줄 나눔이다.
  - 질문 2: A2는 답·출처·근거가 모두 맞았다. B2는 `|` 형식을 따랐지만 답 칸이 `Not stated`로 바뀌어 근거와 모순됐다. 내용은 B에서 나빠졌다.
  - 질문 3: 둘 다 답 칸은 `Not stated`다. A3는 세 항목 형식을 지키지 않았다. B3는 형식을 따랐지만 근거 없는 시간을 추가했다. 형식은 B가 지켰고 근거는 B에서 나빠졌다.
  - B가 나아 보이는 곳은 B2·B3의 `|` 한 줄 형식과 B1의 출처 설명이다. 같은 B2·B3에서 답 내용과 근거는 나빠졌다. 이번 실험에서 few-shot이 답을 개선했다고 정리할 수 없다.
- 문맥학습과 연결한 설명: A와 B는 같은 모델·같은 가중치로 실행했다. 달라진 것은 입력에 넣은 예시 한 개뿐이다. 출력 차이는 지금 입력의 문맥에서 나온 것이고, 가중치를 학습으로 바꾸는 SFT와 다르다. B2·B3는 예시의 `Not stated | ... | ...` 모양을 따라 답 칸에 `Not stated`를 쓴 것으로 보인다. 예시가 형식은 전달했지만 언제 `Not stated`를 써야 하는지는 맞게 전달하지 못했다고 해석한다. 이 해석은 추정이며 원인은 검증하지 않았다.
- 작은 비교로 확인할 수 없는 점: 질문 3개를 조건마다 한 번씩 greedy로 실행한 결과다. 한 모델과 영어 발췌 두 개만 썼다. 통계적 성능 검증이 아니며 다른 모델·질문·한국어 입력으로 일반화할 수 없다. 1,950 m와 11km는 제공 발췌와의 일치만 확인했고 최신 공식 정보와는 대조하지 않았다(판단 보류). 올레 6코스의 실제 소요시간은 미확인이다. 강의자료 검증 환경(2026-10-11)의 A2·B2·A3·B3 핵심 양상과 이번 결과가 같았지만, 다른 환경에서도 같다는 보장은 없다.
- 인력·예산이 적은 상정 조직의 다음 선택과 비용·효과 근거: 이번 실패는 B2 내용(답과 근거의 모순), B3 근거(자료 밖 시간 추가), A3 형식(세 항목 누락)으로 나뉜다. 다음 선택으로 프롬프트 수정과 추가 평가를 먼저 제안한다. 모델을 그대로 두고 입력만 바꾸므로 학습 자료와 학습 환경이 필요 없다. 이번 6개 조건의 생성 시간은 합쳐 약 19초였다(모델 로드 제외, 한 번 측정). 예를 들어 답이 있는 경우의 예시를 함께 넣은 조건을 같은 질문으로 시험하고, 질문 수를 늘려 같은 실패가 반복되는지 기록한다(미실행 제안). 미세조정은 학습 자료 작성·학습 환경·결과 검토·유지 비용이 먼저 들고, 질문 3개 결과로는 그 효과를 판단할 수 없다. 어떤 방식을 택해도 소요시간·요금 같은 답은 공식 자료와 대조하는 사람 검토가 필요하다.

## 발표 기록

| 항목 | 설명 내용 |
|---|---|
| 목적·자료 | 방문자 질문에 제공 발췌만으로 답하기. H(한라산 공식 안내)·O(올레 6코스 공식 안내) 발췌 두 개, 열람일 2026-10-11, H 제목 추가·O 마침표 추가 |
| 고정 조건 | `Qwen/Qwen2.5-0.5B-Instruct` revision `7ae5576…`(11주차와 동일), CPU float32, `do_sample=False`, 새 토큰 최대 64, 같은 자료·질문 3개, 조건마다 새 입력 |
| 바꾼 예시 | B에만 `Question:` 앞에 한라산 입장료 예시 `Not stated \| None \| The supplied sources do not state a fee.` 한 개 추가 |
| 실제 결과 비교 | A2 `Answer: 11 kilometers`와 O 문장 인용 ↔ B2 `Answer: Not stated \| O \| Sources indicate that Jeju Olle Trail Route 6 is 11 kilometers long.`(답·근거 모순). A3 `Not stated` ↔ B3 `Answer: Not stated \| O \| Sources indicate that Route 6 takes approximately 3-4 hours to complete.`(근거 없는 시간 추가) |
| 원문 근거 확인 | 확인: A1·B1(H의 1,950 m), A2(O의 11-kilometer). 불일치: B2. 확인 불가 처리: A3(형식 미준수). 추측 추가: B3. `status: ok`는 출력을 얻었다는 뜻이고 정답 판정이 아니다 |
| 한계·다음 선택 | 질문 3개·조건마다 1회·한 모델이라 통계 검증이 아니다. 최신 길이·실제 소요시간은 미확인. 다음은 답이 있는 예시를 더한 프롬프트 수정과 질문을 늘린 추가 평가(미실행 제안) |

## 제출 확인

- 보고서와 발표 자료 준비: 보고서는 이 파일, 발표 자료(PDF 10쪽)는 같은 폴더 `links.md`의 구글 드라이브 링크. 저장소 `.gitignore`가 `*.pdf`를 제외하고 큰 바이너리 파일은 외부 링크로 내도록 안내해서 링크로 제출
- `assignments/week-12/202021023/` 경로 사용
- 이름·연락처·기업 비공개 데이터 미포함
- 별도 12주차 노트북 없음. 실행은 11주차 노트북 복사본 끝에 제공된 실행 셀을 붙여서 했다.
