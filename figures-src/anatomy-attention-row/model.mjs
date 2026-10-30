// Truth source for the attention-row figure. Values match
// public/interactive/week-09/attention-heads.html and week-09.mdx lecture 2:
// human-set educational heads, not taken from a trained model.
export const TOKENS = ["민지는", "제주에서", "우산을", "샀다", "그것은", "빨갛다"];
export const CURRENT = 4; // 그것은: the row whose representation is being built

export const HEADS = {
  A: { note: "우산을에 큰 비중", row: [0.05, 0.05, 0.7, 0.05, 0.1, 0.05] },
  B: { note: "가까운 위치에 큰 비중", row: [0.05, 0.05, 0.1, 0.35, 0.35, 0.1] },
  C: { note: "고른 비중", row: Array(6).fill(1 / 6) },
};
export const ORDER = ["A", "B", "C"];

export const sumOf = (row) => row.reduce((a, b) => a + b, 0);

// Self-contained (uses only HEADS and TOKENS) so build.mjs can inline it into the page.
export function readoutOf(name) {
  const row = HEADS[name].row;
  const peak = Math.max(...row);
  const tops = row.map((v, i) => (Math.abs(v - peak) < 1e-9 ? i : -1)).filter((i) => i >= 0);
  const what = tops.length === row.length ? "여섯 칸 모두 " + peak.toFixed(2) : tops.map((i) => TOKENS[i]).join("·") + " " + peak.toFixed(2);
  return "헤드 " + name + " · " + what + " · 합 " + row.reduce((a, b) => a + b, 0).toFixed(2);
}

// self-check: every row has six weights and sums to 1
for (const name of ORDER) {
  const row = HEADS[name].row;
  if (row.length !== TOKENS.length || Math.abs(sumOf(row) - 1) > 1e-9) throw new Error(`head ${name} row is not a weight row`);
}
