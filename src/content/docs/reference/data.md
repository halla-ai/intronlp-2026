---
title: 데이터 출처
description: 실습에 쓰는 공개 데이터
---

실습에는 아래 공개 데이터만 쓴다. AI Hub 자료를 뺀 나머지는 노트북이 필요할 때 내려받으므로 미리 준비할 것이 없다.

| 소스 | 내용 |
|---|---|
| AI Hub 「한국어 방언 발화(제주도)」 | 방언과 표준어 대응쌍. 교육용 사용 가능 |
| [제주데이터허브](https://www.jejudatahub.net) | 제주 민간 개방 포털 |
| [제주 관광 빅데이터 서비스 플랫폼](https://data.ijto.or.kr) | 관광 분야 특화 |
| [공공데이터포털](https://www.data.go.kr) | 제주 행정정보 |
| [제주관광공사 VisitJeju 한라산 안내](https://www.visitjeju.net/en/detail/view?contentsid=CONT_000000000500685) | 9주차 영어 안내문의 짧은 발췌. 페이지 제목을 붙이고 한 토큰을 가려 문맥 관찰. 2026-10-11 열람 |
| [제주관광공사 VisitJeju 올레 6코스 안내](https://m.visitjeju.net/en/detail/view?contentsid=CNTS_000000000020298) | 10주차 영어 안내문의 첫 절 발췌. 감정분류와 이어쓰기의 과제 적합성 관찰. 2026-10-11 열람 |
| [fastText 한국어 단어 벡터](https://fasttext.cc/docs/en/crawl-vectors.html) (cc.ko.300) | 웹 문서로 미리 학습된 단어 벡터. CC BY-SA 3.0. 7주차 노트북이 앞부분만 내려받는다 |
| [paraphrase-multilingual-MiniLM-L12-v2](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2) | 문장을 384칸 벡터로 바꾸는 미리 학습된 다국어 모델. Apache-2.0. 8주차 노트북이 내려받는다 |
| [bert-tiny](https://huggingface.co/prajjwal1/bert-tiny) | 작은 영어 BERT 사전학습 모델. MIT. 9주차의 어텐션 관찰과 빈칸 채우기용 |
| [DistilBERT SST-2](https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english) | 영어 감정분류에 맞게 추가 학습된 모델. Apache-2.0. 10주차의 긍정·부정 분류용 |
| [DistilGPT2](https://huggingface.co/distilbert/distilgpt2) | 작은 영어 GPT-2 계열 사전학습 모델. Apache-2.0. 10주차의 짧은 이어쓰기용 |

## 알아둘 것

- 제주도의 행정 내부망 빅데이터 플랫폼은 학생이 접근할 수 없다. 위 개방 포털만 쓴다
- **도내 기업의 데이터는 쓰지 않는다.** 수업에서 기업이 등장할 때는 "이런 조건을 가진 조직"이라는 상정일 뿐이며, 기업이 데이터를 제공하지 않는다
- 데이터 원본은 이 저장소에 담지 않는다. 라이선스와 용량 때문이다
- 9-10주차의 기본 모델 입력은 위 공식 공개 안내문의 짧은 발췌를 사용한다. 빈칸 치환·제목 추가와 절 단위 발췌를 명시하며, 원문 복원이 곧 사실 검증이라는 뜻은 아니다
- 구조 설명용 문장과 긍정·부정 표현의 통제 예시는 수업용 보조 자료다. 실제 관광객 후기·기업 데이터가 아니다. 작은 영어 모델의 구조·사용법을 관찰하며 한국어 제주 서비스의 성능을 평가하지 않는다
- **AI Hub 자료는 각자 이용 승인을 받아야 한다.** 승인에 시간이 걸리므로 되도록 일찍, 늦어도 쓰는 주차가 되기 전에 신청한다. 음성 파일은 받지 않고 방언·표준어 텍스트 대응쌍만 내려받는다. 받은 자료는 공개 저장소나 수업 플랫폼에 올리지 않고 각자의 Colab 세션에만 둔다. 승인이 늦어지면 노트북에 들어 있는 설명용 표본으로 먼저 실습한다
