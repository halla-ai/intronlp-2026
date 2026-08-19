# 언어모형과 자연어처리 2026-2

제주한라대학교 인공지능학과 - 자연어처리 입문. 프로그래밍·수학 배경 없이 시작한다

**사이트**: [intronlp-2026.halla.ai](https://intronlp-2026.halla.ai)
**저장소**: [github.com/halla-ai/intronlp-2026](https://github.com/halla-ai/intronlp-2026)

| 항목 | 내용 |
|---|---|
| 학수번호 | 131107967A |
| 대상 | 1·2학년 |
| 학점·시수 | 3학점 / 3시수 |
| 운영 | BL - 온라인 2시수(AI Professor) + 대면 1시수 |

---

## 학생이라면

- **강의계획서**: [intronlp-2026.halla.ai/syllabus](https://intronlp-2026.halla.ai/syllabus)
- **실습 노트북**: [intronlp-2026.halla.ai/notebooks](https://intronlp-2026.halla.ai/notebooks) - Colab에서 바로 열린다
- **과제 제출**: [intronlp-2026.halla.ai/assignments](https://intronlp-2026.halla.ai/assignments) - GitHub 웹에서만 해도 된다

설치할 것이 없다. 브라우저만 있으면 된다.

---

## 주차 구성

| 주 | 주제 |
|---|---|
| 1 | 자연어처리 소개와 언어모델의 개요 |
| 2 | 언어와 말뭉치, 텍스트 전처리와 단어 분포 |
| 3 | 확률론적 언어모델, N-그램 모델 |
| 4 | 숨겨진 마르코프 모델(HMM)과 시퀀스 태깅 |
| 5 | 통계적 텍스트 분류, 나이브 베이즈와 문서 분류 |
| 6 | 단어의 의미 표현, 분포적 통계와 임베딩 기초 |
| 7 | 신경망 기반 단어 임베딩, Word2Vec |
| 8 | 문장 임베딩과 텍스트 유사도 |
| 9 | 시퀀스 모델링과 트랜스포머의 등장 |
| 10 | 사전학습 언어모델, BERT와 GPT |
| 11 | 대규모 언어모델(LLM)의 시대, 특징과 활용 |
| 12 | 사전학습 모델 활용법, 프롬프트 엔지니어링 |
| 13 | NLP 응용 사례 연구 및 최신 동향 |
| 14 | 언어모델과 사회, 윤리적 이슈와 책임 있는 AI |
| 15 | 정리 및 향후 학습 안내 |

---

## 저장소 구조

```
src/content/docs/     강의 사이트 콘텐츠 (Astro + Starlight)
  weeks/              주차별 강의노트 15개
  syllabus.md         학생용 강의계획서 (학사시스템 등록본에서 파생)
notebooks/            실습 노트북. Colab 배지로 열린다
assignments/          과제 제출. week-NN/<학번>/
```

## 개발

```bash
make install    # 의존성 설치
make dev        # localhost:4321
make build      # dist/ 정적 빌드
make status     # 콘텐츠 현황
```

새 콘텐츠:

```bash
make new-week N=07       # 주차 페이지
make new-notebook N=07   # 실습 노트북 (표준 형태로 생성)
```

## 배포

`main` push 시 GitHub Actions가 빌드해 GitHub Pages로 배포한다.

## 실습 설계 원칙

노트북은 **동작하는 상태로 제공한다.** 학생은 먼저 그대로 실행해 결과를 확인하고,
표시된 **한 지점만** 바꿔 무엇이 달라지는지 본다. 밑바닥부터 작성하게 하지 않는다.

매 주차 돌아가는 결과물을 손에 쥐고 나가는 것이 목표다.
