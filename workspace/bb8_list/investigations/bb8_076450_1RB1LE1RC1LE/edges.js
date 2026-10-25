// Literal simulation; print left-edge events (new leftmost cell) whose state is B (resets), compressed.
// Usage: node edges.js maxSteps [TM] [states]
const TM = process.argv[3] || "1RB1LE_1RC1LE_0RD1RE_1LA---_1LG1RF_0LH0LG_1RH1LB_0RA0RG";
const want = process.argv[4] || "B";
const T = TM.split("_").map(ch => [0, 3].map(i => { const e = ch.substr(i, 3); if (e === "---") return null; return [+e[0], e[1] === "R" ? 1 : -1, e.charCodeAt(2) - 65]; }));
const N = 1 << 24; const tape = new Uint8Array(N);
let pos = N >> 1, st = 0, lo = pos, hi = pos;
const maxSteps = +process.argv[2];
function rle(a, b) { // run-length on 2-cell tokens roughly
  let s = []; let i = a;
  const str = Array.from(tape.subarray(a, b + 1)).join('');
  return comp(str);
}
function comp(s) {
  let out = []; let i = 0;
  while (i < s.length) {
    let best = null;
    for (let L = 1; L <= 6; L++) {
      const u = s.substr(i, L); if (u.length < L) break;
      let k = 1; while (s.substr(i + k * L, L) === u) k++;
      if (k >= 2 && k * L >= Math.max(4, 2 * L) && (!best || k * L > best[1] * best[0].length)) best = [u, k];
    }
    if (best) { out.push('(' + best[0] + ')^' + best[1]); i += best[0].length * best[1]; }
    else { out.push(s[i]); i++; }
  }
  return out.join(' ');
}
for (let s = 1; s <= maxSteps; s++) {
  const r = tape[pos]; const e = T[st][r];
  if (!e) { let a = lo, b = hi; while (tape[a] === 0 && a < b) a++; while (tape[b] === 0 && b > a) b--; console.log('HALT at step', s - 1, 'state', String.fromCharCode(65 + st), r, 'pos', pos - a, comp(Array.from(tape.subarray(a, b + 1)).join('')).slice(0, 400)); process.exit(0); }
  tape[pos] = e[0]; pos += e[1]; st = e[2];
  if (pos > hi) hi = pos;
  if (pos < lo) {
    lo = pos;
    if (want.includes(String.fromCharCode(65 + st))) {
      let b = hi; while (tape[b] === 0 && b > pos) b--;
      const w = comp(Array.from(tape.subarray(pos + 1, b + 1)).join(''));
      console.log(s, String.fromCharCode(65 + st) + tape[pos], w.length > 300 ? w.slice(0, 300) + '...' : w);
    }
  }
  if (pos < 10 || pos > N - 10) { console.log('tape overflow at', s); process.exit(1); }
}
console.log('no halt within', maxSteps);
