// A4 "drawing" sheet for the attention-row figure, for anatomy's scripts/print.mjs.
// Every number comes from model.mjs; every sentence matches the figure's caption.
import { HEADS, TOKENS, CURRENT } from "./model.mjs";

const item = (pattern) => `[data-item${pattern}]`;
const col = (i) => item(`="res${i}.glass"`);
const pose = (name) => ({
  actions: [["eval", "document.body.dataset.theme = 'light'"], ["key", name.toLowerCase()], ["wait", 400]],
});
const row = (name) => HEADS[name].row.map((v) => v.toFixed(2)).join(" ");

export default {
  page: "../../public/interactive/week-09/attention-row-machine.html",
  out: "attention-row-machine",
  views: { A: pose("A"), B: pose("B"), C: pose("C") },

  name: "참고 비중 혼합대",
  kicker: "9주차 강의 2 · 어텐션 가중치 한 행",
  title: "참고 비중 혼합대: '그것은' 행 읽기",
  number: "W09-2",

  parts: [
    { id: "columns", name: "계량 칸 여섯 개: 참고할 토큰(열)", select: item(`^="res"][data-item$=".glass"`), at: [321, 138] },
    { id: "valves", name: "밸브와 손잡이: 섞어 오는 몫", select: `${item('$=".valve"')}, ${item('$=".lever"')}`, at: [365, 198] },
    { id: "selector", name: "선택 다이얼: 헤드 A·B·C", select: item('^="selector"'), at: [124, 108] },
    { id: "rods", name: "연결 막대: 여섯 밸브를 함께 맞춤", select: item('$=".rod"'), at: [193, 151] },
    { id: "gutter", name: "홈통과 토큰 명판", select: item('^="gutter"'), at: [118, 152] },
    { id: "vessel", name: `혼합 용기: '${TOKENS[CURRENT]}'의 새 표현(행)`, select: item('^="vessel"'), at: [493, 187] },
    { id: "col2", select: col(2) },
    { id: "col3", select: col(3) },
    { id: "col4", select: col(4) },
  ],

  spec: [
    ["토큰 1-3", TOKENS.slice(0, 3).join(" · ")],
    ["토큰 4-6", TOKENS.slice(3).join(" · ")],
    ["현재 토큰", `${TOKENS[CURRENT]} (행의 주인)`],
    ["헤드 A", row("A")],
    ["헤드 B", row("B")],
    ["헤드 C", "여섯 칸 모두 1/6, 약 0.17"],
    ["행의 합", "세 헤드 모두 1.00"],
    ["값의 출처", "사람이 지정한 교육용 값, 학습 모델 값 아님"],
    ["칸의 뜻", "섞어 오는 정보의 몫, 정답 확률 아님"],
  ],

  main: { view: "A" },
  inset: { label: "헤드 C · 고른 비중", view: "C" },
  steps: [
    { view: "A", title: "다이얼로 헤드 A", focus: ["selector", "rods"] },
    { view: "A", title: "우산을 칸 0.70", focus: ["col2"] },
    { view: "B", title: "헤드 B: 가까운 위치", focus: ["col3", "col4"] },
    { view: "C", title: "헤드 C: 고른 비중", focus: ["columns"] },
    { view: "A", title: "합은 늘 1.00", focus: ["vessel"] },
  ],
};
