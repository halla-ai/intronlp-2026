// Week 9 lecture 2 figure: one row of attention weights as a blending bench.
// Built with the anatomy kit (MIT, vendored in ./kit). Run from the repo root:
//   node figures-src/anatomy-attention-row/build.mjs                    -> public page (theme follows the site)
//   node figures-src/anatomy-attention-row/build.mjs --theme light --out x.html   -> fixed-theme variant for checks
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import * as k from "./kit/iso-kit.mjs";
import * as A from "./kit/audit.mjs";
import { kitScript } from "./kit/inline-kit.mjs";
import { CURRENT, HEADS, ORDER, TOKENS, readoutOf } from "./model.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, "..", "..");
const argOf = (name) => {
  const at = process.argv.indexOf(name);
  return at > 0 ? process.argv[at + 1] : null;
};
const FORCED = argOf("--theme");
const OUT = argOf("--out") ?? join(ROOT, "public/interactive/week-09/attention-row-machine.html");

const WIDTH = 600;
const HEIGHT = 340;
const START = "A";

// world: x along the bench (token order), y toward the viewer, z up; 1 unit ~ 1 mm
const PLATE = { x: -150, y: -30, w: 284, d: 74, r: 8 };
const PLATE_H = 10;
const FOOT_H = 5;

const PITCH = 32;
const CX = TOKENS.map((_, i) => -96 + PITCH * i);
const PLINTH_H = 14;
const COLLAR = [14, 16.5];
const GLASS_TOP = 72;
const CAP_H = 4;
const FULL = 53; // liquid height of one full measure (weight 1.00)
const LIQ_Z = COLLAR[1];
const VALVE = { y: 0, d: 6, z: 9, h: 6 };
const LEVER_LEN = 6.5;
const ROD = { y: 1.5, d: 3, z: 10, h: 2 };

const SEL = { x: -146, y: -22, w: 30, d: 28, r: 2 };
const KNOB = [-131, -8];
const KNOB_R = 7;
const ANGLE = { A: -55, B: 0, C: 55 };

const GUT = { x: -118, x1: 96, y: 14, y1: 32, wall: 2, h: 10 };
const LIQ_TOP = 3.6;

const VESSEL_X = 112;
const VPLINTH = { x: 96, y: -22, w: 32, d: 54, r: 2 };

const P = k.fitProjection(
  [...k.boxCorners(PLATE, -PLATE_H - FOOT_H, 0), [CX[0] - 9.5, -20.5, GLASS_TOP + CAP_H], [VESSEL_X + 13, -20.5, GLASS_TOP + CAP_H]],
  WIDTH,
  HEIGHT,
  { pad: 22, azimuth: 60 },
);

const at = (point) => k.iso(point, P);
const S = (paths, style) => k.solidSvg(paths, style);
const L = (d, style) => k.lineSvg(d, style);
const D = (points, style) => k.dotsSvg(points, style);
const byDepth = (points) => [...points].sort((a, b) => k.depthOf([a[0], a[1], 0], P) - k.depthOf([b[0], b[1], 0], P));
const part = (id, html, extra = "") => `<g data-part="${id}"${extra}>${html}</g>`;

const colPlan = (cx) => ({ x: cx - 8, y: -19, w: 16, d: 16, r: 1 });
const liqPlan = (cx) => k.insetPlan(colPlan(cx), 0.8);
const collarPlan = (cx) => ({ x: cx - 9.5, y: -20.5, w: 19, d: 19, r: 1.5 });

// a solid whose paths are rewritten every frame: every slot is always present
function liveSolid(paths, { tone = "hi", lit = false, cls = "" } = {}) {
  const shades = [0, 1, 2, 3].map((n) => `<path class="iso-shade" data-shade="${n}" d="${paths.shades[n] || ""}"/>`).join("");
  return `<g class="iso-solid ${cls}"${lit ? " data-lit" : ""}><path class="iso-fill" d="${paths.fill}"/>${shades}<path class="iso-top" d="${paths.top}"/><path class="iso-line iso-crease" data-tone="faint" d="${paths.crease}"/><path class="iso-line iso-edge" data-tone="${tone}" d="${paths.outline}"/></g>`;
}

function leverRing(cx, share) {
  const theta = (share * Math.PI) / 2; // closed across the flow (x), fully open along it (y)
  const bar = k.roundedPlan({ x: -1, y: -1, w: LEVER_LEN + 1, d: 2, r: 0.9 }, 4);
  return bar.map(([x, y]) => [cx + x * Math.cos(theta) - y * Math.sin(theta), VALVE.d / 2 + x * Math.sin(theta) + y * Math.cos(theta)]);
}
const leverPaths = (cx, share) => k.extrude(leverRing(cx, share), VALVE.z + VALVE.h, 1.2, P);
const dosePaths = (cx, share) => k.slabOf(liqPlan(cx), LIQ_Z, Math.max(0.4, FULL * share), P, 3);
const pointerPath = (deg) => {
  const a = (deg * Math.PI) / 180;
  return k.lineOnTop([KNOB[0] + Math.sin(a) * 1.4, KNOB[1] + Math.cos(a) * 1.4], [KNOB[0] + Math.sin(a) * (KNOB_R - 1.2), KNOB[1] + Math.cos(a) * (KNOB_R - 1.2)], PLINTH_H + 5, P);
};

// Every drawn item goes into the recorder with its true shape; A.settle measures depth
// wherever two items overlap and sets the painter's keys; --audit proves the geometry.
const R = A.recorder(P);
const put = (name, at, svg, shapes) => R.put({ name, at, svg, shapes: shapes.map((s) => R.solid(s)) });
const slabItem = (name, plan, z, h, svg, steps = 8) => put(name, [plan.x + plan.w / 2, plan.y + plan.d / 2, z + h / 2], svg, [A.slab(plan, z, h, { name }, steps)]);

function plate() {
  for (const [x, y] of byDepth(k.corners(PLATE, 22))) {
    const z0 = -PLATE_H - FOOT_H;
    put(`stand.foot-${x}-${y}`, [x, y, z0], S(k.cylinder(x, y, 7, z0, 1.6, P, 28), { tone: "lo" }) + S(k.cylinder(x, y, 5.4, z0 + 1.6, FOOT_H - 1.6, P, 28), { tone: "mid" }), [
      A.cylinder(x, y, 7, z0, 1.6, { name: "stand.foot" }),
      A.cylinder(x, y, 5.4, z0 + 1.6, FOOT_H - 1.6, { name: "stand.foot" }),
    ]);
  }
  const screws = k.corners(PLATE, 10);
  const svg = [
    `<path class="iso-halo" d="${k.haloOf(PLATE, -PLATE_H - FOOT_H, PLATE_H, P)}"/>`,
    S(k.slabOf(PLATE, -PLATE_H, PLATE_H, P, 8, 1.6), { tone: "mid" }),
    L(k.planOutline(k.insetPlan(PLATE, 5), 0, P), { tone: "lo" }),
    L(screws.map(([x, y]) => k.ring(x, y, 2.2, 0, P, 16)).join(""), { tone: "lo" }),
    D(screws.map(([x, y]) => at([x, y, 0])), { size: 0.5 }),
  ].join("");
  R.put({ name: "stand.plate", key: -1e6, svg, shapes: [R.solid(A.slab(PLATE, -PLATE_H, PLATE_H, { name: "stand.plate" }))] });
  // position ruler: a major tick under every reservoir
  const strip = { x: -132, y: 36, w: 232, d: 5.5, r: 1 };
  const ticks = k.topTicks(strip.x + 4, strip.x + strip.w - 4, 4, 8, strip.y + 0.8, 0.6, [1.6, 3.4], P);
  slabItem("ruler", strip, 0, 0.6, [
    S(k.slabOf(strip, 0, 0.6, P, 3), { tone: "lo", crease: "none" }),
    L(ticks.minor, { tone: "lo" }),
    L(ticks.major, { tone: "mid" }),
    D([at([strip.x + 2, strip.y + 2.75, 0.6]), at([strip.x + strip.w - 2, strip.y + 2.75, 0.6])], { size: 0.45 }),
  ].join(""), 3);
}

function selector() {
  const top = PLINTH_H;
  const marks = [];
  for (const name of ORDER) {
    const a = (ANGLE[name] * Math.PI) / 180;
    const dir = [Math.sin(a), Math.cos(a)];
    marks.push(L(k.lineOnTop([KNOB[0] + dir[0] * KNOB_R, KNOB[1] + dir[1] * KNOB_R], [KNOB[0] + dir[0] * (KNOB_R + 1.8), KNOB[1] + dir[1] * (KNOB_R + 1.8)], top, P), { tone: "mid" }));
    const c = [KNOB[0] + dir[0] * 10.8, KNOB[1] + dir[1] * 10.8 + 1.3];
    marks.push(k.faceTextSvg(k.topMatrix(c, top, P, "x"), name, { size: 3.6, tone: "mid", anchor: "middle" }));
  }
  slabItem("selector.block", SEL, 0, top, [
    S(k.slabOf(SEL, 0, top, P, 6, 0.8), { tone: "mid" }),
    L(k.planOutline(k.insetPlan(SEL, 2.6), top, P, 4), { tone: "faint" }),
    D([at([SEL.x + 4.5, SEL.y + 4.5, top]), at([SEL.x + SEL.w - 4.5, SEL.y + 4.5, top])], { size: 0.45 }),
    ...marks,
  ].join(""), 6);
  put("selector.knob", [KNOB[0], KNOB[1], top + 2.5], [
    S(k.cylinder(KNOB[0], KNOB[1], KNOB_R, top, 5, P, 40, 0.5), { tone: "hi", crease: "lo" }),
    L(k.knurl(KNOB[0], KNOB[1], KNOB_R, top, top + 5, 44, P, 0.3), { tone: "lo" }),
    L(k.ring(KNOB[0], KNOB[1], 1.4, top + 5, P, 16), { tone: "mid" }),
    `<path data-part="pointer" class="iso-line" data-tone="hi" data-free="end" d="${pointerPath(ANGLE[START])}" style="stroke-width:1.1"/>`,
  ].join(""), [A.cylinder(KNOB[0], KNOB[1], KNOB_R, top, 5, { name: "selector.knob" })]);
}

function reservoir(i, share) {
  const cx = CX[i];
  const plinth = { x: cx - 11, y: -22, w: 22, d: 22, r: 1.5 };
  slabItem(`res${i}.plinth`, plinth, 0, PLINTH_H, S(k.slabOf(plinth, 0, PLINTH_H, P, 4, 0.6), { tone: "mid" }) + D([at([cx - 8, -19, PLINTH_H]), at([cx + 8, -19, PLINTH_H])], { size: 0.4 }), 4);
  // linkage rod from the previous valve (or the selector) into this valve
  const from = i === 0 ? SEL.x + SEL.w : CX[i - 1] + 4;
  const rod = { x: from, y: ROD.y, w: cx - 4 - from, d: ROD.d, r: 0.4 };
  slabItem(`res${i}.rod`, rod, ROD.z, ROD.h, S(k.slabOf(rod, ROD.z, ROD.h, P, 2), { tone: "mid", crease: "none" }), 2);
  const valve = { x: cx - 4, y: VALVE.y, w: 8, d: VALVE.d, r: 1 };
  slabItem(`res${i}.valve`, valve, VALVE.z, VALVE.h, S(k.slabOf(valve, VALVE.z, VALVE.h, P, 3, 0.4), { tone: "mid" }), 3);
  const lever = leverPaths(cx, share);
  put(`res${i}.lever`, [cx, VALVE.d / 2, VALVE.z + VALVE.h + 0.6], part(`lever-${i}`, liveSolid(lever, { tone: "hi" })) + L(k.ring(cx, VALVE.d / 2, 0.9, VALVE.z + VALVE.h + 1.2, P, 12), { tone: "mid" }), [A.extruded(leverRing(cx, share), VALVE.z + VALVE.h, 1.2, { name: `res${i}.lever` })]);
  column(`res${i}`, cx, part(`dose-${i}`, liveSolid(dosePaths(cx, share), { tone: "lit", lit: true, cls: "ar-liquid" })), false);
  // spout: an arm from the valve over the gutter's back wall, a nozzle down into the channel
  const arm = { x: cx - 1.6, y: VALVE.d, w: 3.2, d: 15, r: 0.6 };
  slabItem(`res${i}.spout`, arm, 11, 2, S(k.slabOf(arm, 11, 2, P, 2, 0.3), { tone: "mid" }), 2);
  put(`res${i}.nozzle`, [cx, 19.5, 9], S(k.cylinder(cx, 19.5, 1.5, 7, 4, P, 16), { tone: "mid", crease: "none" }), [A.cylinder(cx, 19.5, 1.5, 7, 4, { name: `res${i}.nozzle` })]);
}

// collar, glass with its liquid and scale, cap: one item, so the liquid stays inside its glass
function column(id, cx, liquid, vessel) {
  const collar = collarPlan(cx);
  slabItem(`${id}.collar`, collar, COLLAR[0], COLLAR[1] - COLLAR[0], S(k.slabOf(collar, COLLAR[0], COLLAR[1] - COLLAR[0], P, 4, 0.4), { tone: "mid" }), 4);
  const glass = k.slabOf(colPlan(cx), COLLAR[1], GLASS_TOP - COLLAR[1], P, 3);
  slabItem(`${id}.glass`, colPlan(cx), COLLAR[1], GLASS_TOP - COLLAR[1], S(glass, { tone: "lo", className: "ar-glass" }) + liquid + L(glass.crease, { tone: "lo" }) + scale(cx, vessel), 3);
  const cap = vessel ? { x: cx - 9.5, y: -20.5, w: 23.5, d: 19, r: 1.5 } : collar;
  const dots = vessel ? [[cx - 6.5, -6.5], [cx + 11.5, -11]] : [[cx - 6.5, -6.5], [cx + 6.5, -17.5]];
  slabItem(`${id}.cap`, cap, GLASS_TOP, CAP_H, S(k.slabOf(cap, GLASS_TOP, CAP_H, P, 4, 0.5), { tone: "mid" }) + D(dots.map(([x, y]) => at([x, y, GLASS_TOP + CAP_H])), { size: 0.4 }), 4);
}

// graduated strip on the glass front: a tick every 0.1 of one full measure, 0.5 and 1.0 major
function scale(cx, vessel) {
  const sx = cx + 3.6;
  const out = [S(k.slabOf({ x: sx, y: -3, w: 2.6, d: 0.5, r: 0 }, COLLAR[1], GLASS_TOP - COLLAR[1], P, 1), { tone: "mid", crease: "none" })];
  const minor = [];
  const major = [];
  for (let t = 1; t <= 10; t++) {
    const z = LIQ_Z + (FULL * t) / 10;
    (t % 5 ? minor : major).push(k.segment([sx, -3, z], [sx - (t % 5 ? 1.6 : 3.4), -3, z], P));
  }
  out.push(L(minor.join(""), { tone: "lo" }), L(major.join(""), { tone: vessel ? "hi" : "mid" }));
  if (vessel) out.push(k.faceTextSvg(k.sideMatrix([sx - 4.2, -3], LIQ_Z + FULL - 1.1, P, "left"), "1.00", { size: 2.8, tone: "hi", anchor: "end" }));
  return out.join("");
}

function plateText(cx, y, z, words, { size = 6, tone = "mid" } = {}) {
  return k.faceTextSvg(k.sideMatrix([cx, y], z, P, "left"), words, { size, tone, anchor: "middle" });
}

function gutter() {
  const { x, x1, y, y1, wall, h } = GUT;
  const back = { x, y, w: x1 - x, d: wall, r: 0.5 };
  slabItem("gutter.back", back, 0, h, S(k.slabOf(back, 0, h, P, 2, 0.4), { tone: "mid" }), 2);
  const end = { x, y: y + wall, w: wall, d: y1 - y - wall * 2, r: 0 };
  slabItem("gutter.end", end, 0, h, S(k.slabOf(end, 0, h, P, 1, 0.4), { tone: "mid" }), 1);
  const floor = { x: x + wall, y: y + wall, w: x1 - x - wall, d: y1 - y - wall * 2, r: 0 };
  slabItem("gutter.run", floor, 0, LIQ_TOP, [
    S(k.slabOf(floor, 0, 2, P, 1), { tone: "lo", crease: "none" }),
    S(k.slabOf(floor, 2, LIQ_TOP - 2, P, 1), { tone: "lo", className: "ar-liquid", crease: "none" }),
    L(k.lineOnTop([x + wall, (y + y1) / 2], [x1, (y + y1) / 2], LIQ_TOP, P), { tone: "mid", flow: true, className: "ar-flow" }),
  ].join(""), 1);
  const front = { x, y: y1 - wall, w: x1 - x, d: wall, r: 0.5 };
  slabItem("gutter.front", front, 0, h, S(k.slabOf(front, 0, h, P, 2, 0.4), { tone: "mid" }), 2);
  // engraved token plates on the front wall, one under each reservoir
  CX.forEach((cx, i) => {
    const plan = { x: cx - 14, y: y1, w: 28, d: 0.7, r: 0.4 };
    const tone = i === CURRENT ? "hi" : "mid";
    slabItem(`gutter.plate${i}`, plan, 1, 8, S(k.slabOf(plan, 1, 8, P, 2), { tone, crease: "none" }) + D([at([cx - 12.6, y1 + 0.7, 4.6]), at([cx + 12.6, y1 + 0.7, 4.6])], { size: 0.4 }) + plateText(cx, y1 + 0.7, 2.6, TOKENS[i], { tone }), 2);
  });
}

function vessel() {
  const cx = VESSEL_X;
  slabItem("vessel.sump", VPLINTH, 0, PLINTH_H, [
    S(k.slabOf(VPLINTH, 0, PLINTH_H, P, 6, 0.8), { tone: "mid", inner: L(k.sideSeam(VPLINTH, 4, P, 6), { tone: "faint" }) }),
    D([at([VPLINTH.x + 4, VPLINTH.y + VPLINTH.d - 4, PLINTH_H]), at([VPLINTH.x + VPLINTH.w - 4, VPLINTH.y + VPLINTH.d - 4, PLINTH_H]), at([VPLINTH.x + VPLINTH.w - 4, VPLINTH.y + 4, PLINTH_H])], { size: 0.45 }),
  ].join(""), 6);
  // riser from the sump up into the cap, beside the column's right side
  const riser = { x: cx + 10, y: -12.5, w: 3, d: 3, r: 0.6 };
  slabItem("vessel.riser", riser, PLINTH_H, GLASS_TOP - PLINTH_H, S(k.slabOf(riser, PLINTH_H, GLASS_TOP - PLINTH_H, P, 2), { tone: "mid" }), 2);
  column("vessel", cx, part("mix", S(k.slabOf(liqPlan(cx), LIQ_Z, FULL, P, 3), { tone: "hi", className: "ar-liquid ar-mix" })), true);
  // pump motor on the sump
  put("vessel.motor", [cx - 4, 20, PLINTH_H + 4.5], S(k.cylinder(cx - 4, 20, 6, PLINTH_H, 9, P, 36, 0.4), { tone: "mid" }) + L(k.knurl(cx - 4, 20, 6, PLINTH_H, PLINTH_H + 9, 30, P, 0.3), { tone: "lo" }), [A.cylinder(cx - 4, 20, 6, PLINTH_H, 9, { name: "vessel.motor" })]);
  put("vessel.motor-cap", [cx - 4, 20, PLINTH_H + 9.8], S(k.cylinder(cx - 4, 20, 3.2, PLINTH_H + 9, 1.6, P, 24), { tone: "mid" }), [A.cylinder(cx - 4, 20, 3.2, PLINTH_H + 9, 1.6, { name: "vessel.motor-cap" })]);
  // the vessel's plate: the current token, whose new representation this is
  const plan = { x: cx - 14, y: VPLINTH.y + VPLINTH.d, w: 28, d: 0.7, r: 0.4 };
  slabItem("vessel.plate", plan, 1.2, 10.8, S(k.slabOf(plan, 1.2, 10.8, P, 2), { tone: "hi", crease: "none" }) + plateText(cx, plan.y + 0.7, 6.6, TOKENS[CURRENT], { tone: "hi" }) + plateText(cx, plan.y + 0.7, 2.4, "새 표현", { size: 3.6, tone: "mid" }), 2);
}

const startRow = HEADS[START].row;
plate();
selector();
TOKENS.forEach((_, i) => reservoir(i, startRow[i]));
gutter();
vessel();
A.settle(R, P);
R.items.sort((a, b) => a.key - b.key);
A.auditOrExit(R, P);

const svg = k.figureSvg({
  width: WIDTH,
  height: HEIGHT,
  label:
    "참고 비중 혼합대. 받침 위에 여섯 계량 칸이 토큰 순서(민지는, 제주에서, 우산을, 샀다, 그것은, 빨갛다)로 서 있고, 칸마다 밸브와 주둥이가 앞쪽 홈통으로 이어진다. 홈통은 오른쪽 혼합 용기로 모이며, 이 용기는 현재 토큰 '그것은'의 새 표현이다. 왼쪽 선택 다이얼 하나가 연결 막대로 여섯 밸브를 함께 맞춘다. 칸의 액체 높이가 각 위치의 비중이고, 여섯 칸을 합치면 언제나 혼합 용기 한 칸, 1.00이 된다.",
  body: R.items.map((item) => `<g data-item="${item.name}">${item.svg}</g>`),
});

const CSS = `
html,body{background:var(--anatomy-page)}
.iso{--ar-ko:"Pretendard","Apple SD Gothic Neo","Noto Sans KR","Malgun Gothic",sans-serif}
.iso-page{width:min(650px,100% - 32px);margin:12px auto 16px}
.iso-figure{margin:0}
.iso-plate-corner{font-family:var(--ar-ko);letter-spacing:.02em}
.iso-plate-corner[data-corner="title"],.iso-plate-corner[data-corner="hint"]{text-transform:none;letter-spacing:.04em}
.iso-face-text{font-family:var(--ar-ko);letter-spacing:0;font-weight:600}
.iso-legend{font-family:var(--ar-ko)}
.ar-glass>.iso-fill{fill:var(--ar-glass);fill-opacity:.55}
.ar-glass>.iso-shade,.ar-glass>.iso-top{fill:var(--ar-glass);fill-opacity:.35}
.ar-liquid{--anatomy-face:var(--ar-liq-0);--anatomy-lit-top:var(--ar-liq-top);--anatomy-lit-shade:var(--ar-liq-1)}
.ar-liquid>.iso-fill{fill:var(--ar-liq-0)}
.ar-liquid>.iso-shade{fill:var(--ar-liq-1)}
.ar-liquid>.iso-top{fill:var(--ar-liq-top)}
.iso{--ar-glass:#1a1d20;--ar-liq-0:#3b4146;--ar-liq-1:#454c52;--ar-liq-top:#5b636a}
.iso[data-theme="light"]{--ar-glass:#eef1f3;--ar-liq-0:#a9b2ba;--ar-liq-1:#b8c0c7;--ar-liq-top:#cdd4da}
.ar-flow{opacity:.8}
.iso-stage{outline:none;border-radius:2px}
.iso-stage:focus-visible{outline:1px solid var(--anatomy-muted);outline-offset:6px}
.ar-controls{display:flex;flex-wrap:wrap;gap:6px;justify-content:center;margin:14px 0 0}
.ar-controls button{font:500 13px/1 var(--ar-ko);color:var(--anatomy-text);background:var(--anatomy-card);border:1px solid var(--anatomy-mid);border-radius:4px;padding:8px 12px;cursor:pointer;min-height:36px}
.ar-controls button[aria-pressed="true"]{color:var(--anatomy-strong);border-color:var(--anatomy-hi);box-shadow:inset 0 0 0 1px var(--anatomy-hi)}
.ar-controls button:focus-visible{outline:2px solid var(--anatomy-hi);outline-offset:2px}
.ar-row{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:4px;margin:10px 0 0;padding:0;list-style:none;font:12px/1.35 var(--ar-ko);text-align:center;color:var(--anatomy-muted)}
.ar-row li{padding:4px 0;border-top:1px solid var(--anatomy-lo)}
.ar-row b{display:block;font:500 12.5px/1.3 var(--anatomy-mono);color:var(--anatomy-text);font-variant-numeric:tabular-nums}
.ar-row li[data-current] span{color:var(--anatomy-strong)}
.ar-row li[data-peak] b{color:var(--anatomy-strong)}
@media (max-width:420px){.iso-page{width:calc(100% - 24px)}.ar-row{font-size:11px}.ar-row b{font-size:11.5px}.iso-plate .iso-svg{width:116%;margin:0 -8%}.iso-plate{overflow:hidden}}
`;

const rowItems = TOKENS.map((word, i) => `<li${i === CURRENT ? " data-current" : ""}><span>${word}</span><b data-cell="${i}">${startRow[i].toFixed(2)}</b></li>`).join("");
const controls = ORDER.map((name) => `<button type="button" data-head="${name}" aria-pressed="${name === START}">헤드 ${name}</button>`).join("");

const live = `
const P = ${JSON.stringify(P)};
const CX = ${JSON.stringify(CX)};
const HEADS = ${JSON.stringify(HEADS)};
const ORDER = ${JSON.stringify(ORDER)};
const TOKENS = ${JSON.stringify(TOKENS)};
const ANGLE = ${JSON.stringify(ANGLE)};
const KNOB = ${JSON.stringify(KNOB)}, KNOB_R = ${KNOB_R}, PLINTH_H = ${PLINTH_H};
const VALVE = ${JSON.stringify(VALVE)}, LEVER_LEN = ${LEVER_LEN}, LIQ_Z = ${LIQ_Z}, FULL = ${FULL};
const FORCED = ${JSON.stringify(FORCED)};
const colPlan = ${colPlan.toString()};
const liqPlan = (cx) => insetPlan(colPlan(cx), 0.8);
const leverRing = ${leverRing.toString().replace(/k\./g, "")};
const leverPaths = ${leverPaths.toString().replace(/k\./g, "")};
const dosePaths = ${dosePaths.toString().replace(/k\./g, "")};
const pointerPath = ${pointerPath.toString().replace(/k\./g, "")};
const readoutOf = ${readoutOf.toString()};

// theme: follow the course site (FigureFrame posts starlight-theme), else the system setting
const media = matchMedia("(prefers-color-scheme: light)");
let fromParent = false;
const setTheme = (light) => { document.body.dataset.theme = light ? "light" : "dark"; };
if (FORCED) setTheme(FORCED === "light"); else setTheme(media.matches);
addEventListener("message", (e) => { if (!FORCED && e.source === parent && e.data && e.data.type === "starlight-theme") { fromParent = true; setTheme(e.data.theme === "light"); } });
media.addEventListener("change", (e) => { if (!FORCED && !fromParent) setTheme(e.matches); });
if (parent !== window) parent.postMessage({ type: "figure-ready" }, "*");

const stage = document.querySelector(".iso-stage");
const svg = stage.querySelector("svg");
const readout = document.querySelector("[data-readout]");
const status = document.querySelector("[data-status]");
const buttons = [...document.querySelectorAll("[data-head]")];
const cells = [...document.querySelectorAll("[data-cell]")];
const slots = (g) => ({ fill: g.querySelector(".iso-fill"), shades: [...g.querySelectorAll(".iso-shade")], top: g.querySelector(".iso-top"), crease: g.querySelector(".iso-crease"), edge: g.querySelector(".iso-edge") });
const doses = CX.map((_, i) => slots(svg.querySelector('[data-part="dose-' + i + '"]')));
const levers = CX.map((_, i) => slots(svg.querySelector('[data-part="lever-' + i + '"]')));
const pointer = svg.querySelector('[data-part="pointer"]');
const write = (s, p) => { s.fill.setAttribute("d", p.fill); s.shades.forEach((el, n) => el.setAttribute("d", p.shades[n] || "")); s.top.setAttribute("d", p.top); s.crease.setAttribute("d", p.crease); s.edge.setAttribute("d", p.outline); };
const still = matchMedia("(prefers-reduced-motion: reduce)");

let head = "${START}";
let level = HEADS[head].row.slice();
let dial = ANGLE[head];
let frame = 0, last = 0, clock = 0, visible = false, idleTimer = 0;
let touring = !still.matches;
const HOLD = 3.4;

function choose(name, byUser) {
  if (byUser) { touring = false; clearTimeout(idleTimer); idleTimer = setTimeout(() => { touring = !still.matches; clock = 0; run(); }, 8000); }
  if (name === head) { run(); return; }
  head = name;
  buttons.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.head === name)));
  const row = HEADS[name].row;
  const peak = Math.max(...row);
  cells.forEach((cell, i) => { cell.textContent = row[i].toFixed(2); if (Math.abs(row[i] - peak) < 1e-9 && name !== "C") cell.parentElement.setAttribute("data-peak", ""); else cell.parentElement.removeAttribute("data-peak"); });
  const said = readoutOf(name) + ". " + HEADS[name].note + ".";
  stage.setAttribute("aria-valuetext", said);
  if (byUser) status.textContent = said;
  run();
}

function draw() {
  CX.forEach((cx, i) => { write(doses[i], dosePaths(cx, level[i])); write(levers[i], leverPaths(cx, level[i])); });
  pointer.setAttribute("d", pointerPath(dial));
  const row = HEADS[head].row;
  const moving = level.some((v, i) => Math.abs(v - row[i]) > 0.002);
  const sum = level.reduce((a, b) => a + b, 0);
  const text = moving ? "헤드 " + head + "로 맞추는 중 · 합 " + sum.toFixed(2) : readoutOf(head);
  if (readout.textContent !== text) readout.textContent = text;
}

function tick(now) {
  const dt = last ? Math.min((now - last) / 1000, 1 / 30) : 1 / 60;
  last = now;
  const calm = still.matches;
  if (touring && !calm) {
    clock += dt;
    const next = ORDER[Math.floor(clock / HOLD) % ORDER.length];
    if (next !== head) choose(next, false);
  }
  const row = HEADS[head].row;
  // one shared easing factor for all six valves, so the six levels always add up to 1
  const f = calm ? 1 : 1 - Math.exp(-dt / 0.32);
  level = level.map((v, i) => v + (row[i] - v) * f);
  dial = dial + (ANGLE[head] - dial) * (calm ? 1 : 1 - Math.exp(-dt / 0.18));
  const settled = level.every((v, i) => Math.abs(v - row[i]) < 5e-4) && Math.abs(dial - ANGLE[head]) < 0.05;
  if (settled) { level = row.slice(); dial = ANGLE[head]; }
  draw();
  frame = visible && (touring || !settled) ? requestAnimationFrame(tick) : 0;
}
const run = () => { if (!frame && visible) { last = 0; frame = requestAnimationFrame(tick); } };
new IntersectionObserver((entries) => { visible = entries[entries.length - 1].isIntersecting; if (visible) run(); }, { rootMargin: "120px 0px" }).observe(stage);
still.addEventListener("change", () => { touring = !still.matches; run(); });

buttons.forEach((b) => b.addEventListener("click", () => choose(b.dataset.head, true)));
stage.addEventListener("click", () => choose(ORDER[(ORDER.indexOf(head) + 1) % ORDER.length], true));
stage.addEventListener("keydown", (event) => {
  const key = event.key.toUpperCase();
  let to = null;
  if (ORDER.includes(key)) to = key;
  if (event.key === "ArrowRight" || event.key === "ArrowDown") to = ORDER[(ORDER.indexOf(head) + 1) % ORDER.length];
  if (event.key === "ArrowLeft" || event.key === "ArrowUp") to = ORDER[(ORDER.indexOf(head) + ORDER.length - 1) % ORDER.length];
  if (event.key === "Home") to = ORDER[0];
  if (event.key === "End") to = ORDER[ORDER.length - 1];
  if (to === null) return;
  event.preventDefault();
  choose(to, true);
});
addEventListener("keydown", (event) => {
  if (event.target === stage || event.target.closest?.("input,textarea,select")) return;
  const key = event.key.toUpperCase();
  if (ORDER.includes(key) && !event.metaKey && !event.ctrlKey && !event.altKey) choose(key, true);
});
stage.setAttribute("aria-valuetext", readoutOf(head) + ". " + HEADS[head].note + ".");
draw();
`;

const body = k.plateHtml({
  fig: "Fig 1",
  title: "참고 비중 혼합대",
  hint: "A·B·C로 헤드 바꾸기",
  readout: readoutOf(START),
  keys: [
    { mark: "lit", label: "계량 칸의 액체 높이: 각 위치에서 섞어 오는 비중" },
    { mark: "raised", label: "오른쪽 혼합 용기: 현재 토큰 '그것은'의 새 표현, 늘 1.00까지 참" },
  ],
  caption:
    "'그것은' 행 하나를 옮긴 혼합대. 여섯 계량 칸은 참고할 토큰(열), 오른쪽 용기는 표현을 만드는 현재 토큰 '그것은'(행). 왼쪽 다이얼 하나가 연결 막대로 여섯 밸브를 함께 다시 맞춤. 비중은 사람이 지정한 교육용 값으로 실제 모델에서 뽑은 값이 아니며 학습도 하지 않음. 한 행의 비중 합은 1. 우산을의 0.70은 이 행의 정보 결합에서 우산 위치에 큰 비중을 준다는 뜻이지 '우산이 정답일 확률 70%'가 아님.",
  body: `<div class="iso-stage" tabindex="0" role="group" aria-roledescription="헤드 선택 그림" aria-label="참고 비중 혼합대: A, B, C 키나 화살표로 교육용 헤드를 바꿈">${svg}</div><div class="ar-controls" role="group" aria-label="교육용 헤드 선택">${controls}</div><ol class="ar-row" aria-label="현재 토큰 그것은의 참고 비중">${rowItems}</ol><p class="ar-status" data-status role="status" aria-live="polite" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)"></p>`,
});

const themeNow = FORCED ?? "dark";
const boot = FORCED ? "" : `<script>document.body.dataset.theme=matchMedia("(prefers-color-scheme: light)").matches?"light":"dark"</script>`;
let html = k.pageHtml({ title: "참고 비중 혼합대", theme: themeNow, body: `<style>${CSS}</style>${body}`, script: kitScript() + live });
html = html.replace('<html lang="en">', '<html lang="ko">').replace('<main class="iso-page">', `${boot}<main class="iso-page">`);
if (!html.includes('<html lang="ko">')) throw new Error("lang patch failed");
mkdirSync(dirname(OUT), { recursive: true });
writeFileSync(OUT, html);
console.log("wrote", OUT, `(${(html.length / 1024).toFixed(0)} KB)`);
