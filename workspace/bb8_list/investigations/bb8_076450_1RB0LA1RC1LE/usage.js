// Transition usage counts over a literal run from the blank tape. Usage: node usage.js maxSteps [variant]
const VARIANT = process.argv[3] === 'variant';
const TM = VARIANT ? "1RB0LA_1RC1LE_0RD1RE_1LA---_1LG1RF_0LH0LG_1RH1LB_1RA0RG"
                   : "1RB0LA_1RC1LE_0RD1RE_1LA---_1LG1RF_1RH0LG_1RH1LB_1RA0RG";
const T = TM.split("_").map(ch => [0, 3].map(i => { const e = ch.substr(i, 3); if (e === "---") return null; return [+e[0], e[1] === "R" ? 1 : -1, e.charCodeAt(2) - 65]; }));
const N = 1 << 24; const tape = new Uint8Array(N);
let pos = N >> 1, st = 0; const cnt = {}, last = {};
const maxSteps = +(process.argv[2] || 1e7);
for (let s = 1; s <= maxSteps; s++) {
  const r = tape[pos]; const e = T[st][r]; const key = 'ABCDEFGH'[st] + r;
  if (!e) { console.log('HALT', s - 1); break; }
  cnt[key] = (cnt[key] || 0) + 1; last[key] = s;
  tape[pos] = e[0]; pos += e[1]; st = e[2];
}
for (const k of Object.keys(cnt).sort()) console.log(k, cnt[k], 'last at step', last[k]);
