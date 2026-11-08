# 1-15주차 강의 자료 검수 및 개선

- 검수일: 2026-10-11
- 기준: 학사 등록본을 관리하는 `admin/depts/ai/courses/2026-2/260819-syllabus-intro-nlp-v1.md`와 저장소 실습 원칙
- 범위: 강의 15개, 실습 노트북 12개, 생성기 8개, 인터랙티브 HTML 46개, 제공 양식 3개 및 공통 안내
- 학사 계획·평가 비중·주차 배치·학생 제출물 변경 없음

## 주차별 개선

| 주차 | 확인 및 개선 | 실습 검증 |
|---|---|---|
| 1 | 확률과 점수, greedy와 샘플링, 반복 가능성과 안전성 구분. 세 번의 출력으로 내부 분포를 확정하는 설명 수정. 제공 노트북부터 실행하는 경로 명시 | 기본값 CPU 실행 통과 |
| 2 | 공개 자료와 교수 작성 네 문장 구분. 작은 표본의 Zipf 해석 보정. 파일 불용어 목록은 추가 편집 요구 대신 출력 해석. 한글 글꼴 실패 시 번호·한글 표 대조 경로 제공 | 기본값·다운로드 실패·한글 그래프 통과 |
| 3 | 유니그램 생성, 스무딩의 어휘 범위, 퍼플렉서티 비교 조건 보정. 학습 글의 세분화와 새 글 예측 성능 구분 | 기본값 CPU 실행 및 예시 횟수 대조 통과 |
| 4 | HMM 시작 확률 포함. 비터비 저장 칸과 계산 횟수 구분. 분석 결과만으로 사전 미등록 원인을 확정하는 설명 수정 | 공개 eKoNLPy 2.2.1 CPU 실행 통과 |
| 5 | 예측 확률과 실제 정답률, 문턱 변화의 불변 구간, 작은 새 문장 표본의 해석 범위 보정. 그림과 Q&A 정합 | 기본값 CPU 실행 및 분류 출력 대조 통과 |
| 6 | 서로 다른 음식 문장의 창 설명 수정. 코사인에 필요한 방향·좌표 값·비율 구분 | 기본값 CPU 실행 및 창별 수치 대조 통과 |
| 7 | 유사도·유추·PCA 지도의 해석 한계 보정. 이웃 관찰과 학습 원인 가설 구분. 공개 벡터의 시간 제한·파싱·누락·실패 상태 처리 | 직접 학습·공개 벡터·다운로드 실패·한글 그래프 통과 |
| 8 | 질문의 출발 조건, 점수 간 비교·결합 효과의 검증 범위 보정. 모델 revision 고정·CPU 두 스레드. 오답 없는 경우와 모델 실패 시 확인 질문 경로 제공 | 실제 문장 모델 CPU 실행 및 검색 출력 대조 통과 |
| 9 | 기본·심화의 결과 해석 경로 명시. 기존 실제 모델과 교육용 모형 구분 유지 | 실제 모델 CPU 실행 통과 |
| 10 | 기본·심화의 결과 해석 경로 명시. 분류 score와 정확도, 생성과 사실 검증 구분 유지 | 실제 분류·생성 CPU 실행 통과 |
| 11 | 영어 질문·답 형식의 한국어 읽기 안내. 모델의 복수 EOS를 포함한 종료 상태 판정 | 일반 모델 2조건·추론형 모델 1조건 CPU 실행 통과 |
| 12 | 영어 질문의 뜻과 확인 불가 규칙. 출력의 Evidence와 사람의 확인 상태 구분, 양식 동기화 | 지정 노트북 없음. 양식·인터랙티브 검증 |
| 13 | 복수 텍스트와 멀티모달 구분, 처리 단계별 입력 설명 | 지정 노트북 없음. 양식·인터랙티브 검증 |
| 14 | 설명 충실성과 정답 정확성 구분, 원논문 연결. 세 대응쌍의 사회적 편향·원인 일반화 금지 유지 | 실제 모델 9조건 CPU 실행 통과 |
| 15 | 누적 개념 정리에서 빠진 HMM 연결을 본문·용어·그림에 보완 | 지정 노트북 없음. 양식·인터랙티브 검증 |

- 전 주차에 기본·심화 또는 기존 기본·확장 해석 경로 제공
- 전 주차 공통 H2 9개 유지, Q&A 8개 이상과 자기 점검 답안 확인
- 9·10주차 입력 변경은 선택 활동, 새 코드 작성 요구 없음
- 모든 노트북의 TODO 코드 셀 정확히 1개, 기본값 변경 없이 실행
- 제출 안내에서 학번 폴더 생성 후 파일 업로드 순서 명시. 이름·연락처 제외 및 PR 제목 형식 검사, 제목 수정 시 재검사. 자동 형식 검사와 채점·확정 구분
- 공개 발췌, 교수 작성 예시, 공개 사전학습 모델의 출처·가공 범위 구분

## 검증 결과

- `make check-course`: 강의 15개·노트북 12개·생성기 8개·인터랙티브 경로 47개 통과. 같은 HTML의 쿼리별 삽입 포함
- `make check`: 0 errors, 0 warnings, 기존 15 hints
- `make build`: 정적 페이지 21개 생성 통과
- HTML 46개의 JavaScript 문법 검사 통과
- 빌드 결과의 내부 링크·앵커 1,269개 대조 통과
- Chrome 390px·1280px: 강의 30화면, 이미지 로딩 172건, iframe 94건, 버튼·선택·범위 조작 516건 검사 통과. Q&A 펼침·닫힘, 가로 넘침·세로 잘림·페이지 JavaScript 오류 검사 포함
- 2·7주차 한글 그래프 PNG 렌더 및 문자·배치 시각 확인 통과
- 노트북 12개를 서로 다른 새 Python 3.12.13 커널에서 순차 실행, 원본 셀·TODO 변경 없음. 검증용 확인 셀만 메모리 사본 마지막에 추가
- 7주차 공개 벡터 실제 다운로드 및 8·9·10·11·14주차 실제 모델 실행 확인. unavailable 대체 경로만으로 성공 판정하지 않음
- 2·7주차 네트워크 실패 주입 실행에서 끝까지 도달하고 생략 상태 유지 확인
- 노트북 코드 셀의 저장 출력은 제거 상태 유지, 생성기와 배포 노트북 cell 원문 일치

## 검증 범위와 재확인 항목

- 이번 실행은 로컬 새 CPU 커널 검증. 인증된 실제 Colab 세션의 최초 설치·실행·제출까지 수행한 증거는 아님
- 실행 환경은 검증용 Python 환경을 공유하되 커널·작업 폴더는 노트북마다 분리. 패키지가 전혀 없는 환경 12개를 별도로 만든 검증과 구분
- GitHub 제출 화면 순서는 공식 문서와 대조. 실제 학생 계정의 Fork·제출·접수는 수행하지 않음
- 14주차 원본 PDF 전체 직접 열람 미확인은 자료에 유지. 세 대응쌍의 색인 본문 확인과 구분
- 11주차 추론 출력의 길이 제한·불완전 상태는 관찰 상태로 보존. 완료된 정답이나 성능 개선으로 바꾸지 않음
- 실제 관광 운영 정보·제주어 전체 성능·사회적 공정성·학습 말뭉치의 원인에 관한 새 검증 결과 없음
- 이 문서는 개선 브랜치의 검증 기록. 운영 사이트 반영 여부는 PR 머지·배포 후 별도 확인 대상

## 확인한 주요 원문

- [SLP 3판 N-gram Language Models](https://web.stanford.edu/~jurafsky/slp3/3.pdf)
- [SLP 3판 품사 태깅·HMM](https://web.stanford.edu/~jurafsky/slp3/17.pdf)
- [scikit-learn 확률 보정](https://scikit-learn.org/stable/modules/calibration.html)
- [scikit-learn TF-IDF](https://scikit-learn.org/stable/modules/feature_extraction.html#tfidf-term-weighting)
- [Gensim KeyedVectors](https://radimrehurek.com/gensim/models/keyedvectors.html)
- [fastText 공개 벡터의 형식·학습·라이선스](https://fasttext.cc/docs/en/crawl-vectors.html)
- [문장 임베딩 모델 카드](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)
- [LLM 설명의 충실성 원논문](https://arxiv.org/abs/2305.04388)
- [GitHub 새 파일·하위 폴더 생성](https://docs.github.com/en/repositories/working-with-files/managing-files/creating-new-files)
- [GitHub 파일 업로드](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository)
- [GitHub Fork 동기화](https://docs.github.com/en/pull-requests/how-tos/work-with-forks/syncing-a-fork)
