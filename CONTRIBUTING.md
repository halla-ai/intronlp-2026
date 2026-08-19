# 기여 가이드

이 저장소는 두 가지 PR을 받는다. **과제 제출**과 **강의 자료 수정**이다.

---

## 과제 제출

**설치할 것이 없다.** GitHub 웹사이트에서만 해도 제출이 끝난다.

### 처음 한 번만

1. [github.com](https://github.com) 계정을 만든다
2. 이 저장소 오른쪽 위 **Fork** 를 누른다

### 매번

1. Colab에서 **파일 > .ipynb 다운로드**
2. 내 Fork에서 `assignments/week-01/` 로 이동 (주차에 맞게)
3. **Add file > Upload files** 로 파일을 끌어다 놓는다
4. 경로가 `assignments/week-01/<내 학번>/` 이 되게 적는다
5. **Commit changes**
6. **Contribute > Open pull request**
7. 제목: `[제출] 1주차 - 20260001 홍길동`

### 규칙

- 폴더 이름은 **학번만**. 이름은 PR 제목에만 적는다
- 다른 사람 폴더는 건드리지 않는다
- **이 저장소는 공개다.** 연락처나 주민번호 같은 개인정보를 넣지 않는다

### 왜 로컬 빌드가 필요 없는가

과제 PR은 `assignments/` 아래 폴더만 추가하므로 사이트 빌드에 영향이 없다.
`make build` 를 돌릴 필요가 없고, Node를 설치하지 않아도 된다. 검사는 CI가 한다.

---

## 강의 자료 수정

오타, 깨진 링크, 설명 오류를 고치는 PR은 환영한다.

```bash
git clone https://github.com/<본인>/intronlp-2026.git
cd intronlp-2026
make install
make dev        # localhost:4321 에서 확인
make build      # PR 전 통과 확인
```

- `main` 으로 PR을 보낸다
- 커밋 메시지는 한국어로 써도 된다
- 강의 자료 수정과 과제 제출을 **한 PR에 섞지 않는다**

오류만 알리고 싶다면 PR 대신 [Issues](https://github.com/halla-ai/intronlp-2026/issues)에
남겨도 된다.

---

## 질문

실습에서 막혔을 때는 순서대로 시도한다.

1. 오류 메시지의 **마지막 줄**을 읽는다
2. AI Professor 튜터에게 묻는다
3. 그래도 막히면 Issues에 남긴다 (질문 템플릿 사용)
