// Literal simulation (no acceleration) from a canonical-style start, reporting macro events.
// usage: node macro.js <mode> <args...>
//   mode W <word> [maxSteps]       : 0^inf <word> B>0 0^inf
//   mode Y <M> [maxSteps]          : 0^inf A>0 (01)^M 0^inf
// Events: Y(M) = A>0 at the left edge followed by exactly (01)^M;
//         canonical  prefix (010)^a (01110111|0) 1^n 01010 B>0  (prefix <= 4 chars, n >= 2)
// Stops at HALT, at a level start L(p,A) = p (010)^A 0 111 01010 B>0 with p in {1,11} and A >= AMIN (env, default 12),
// or at maxSteps.
const TM = process.env.TM || "1RB0RF_1RC0LF_0RD0RB_1LE1LG_0LA0LC_0LD1RH_1RA1LC_1RF---";
const AMIN = +(process.env.AMIN || 12);
const T = TM.split("_").map(ch => [0, 3].map(i => { const e = ch.substr(i, 3); if (e === "---") return null; return [+e[0], e[1] === "R" ? 1 : -1, e.charCodeAt(2) - 65]; }));
const mode = process.argv[2];
let word, st, maxSteps;
if (mode === 'W') { word = process.argv[3]; maxSteps = +(process.argv[4] || 1e9); st = 1; }
else { const M = +process.argv[3]; word = '0' + '01'.repeat(M); maxSteps = +(process.argv[4] || 1e9); st = 0; }
const N = Math.max(1 << 20, 64 * word.length + (1 << 16));
const tape = new Uint8Array(N);
const base = N >> 2;
for (let i = 0; i < word.length; i++) tape[base + i] = +word[i];
let pos = mode === 'W' ? base + word.length : base;
let lo = base, hi = base + word.length - 1, steps = 0;
if (pos > hi) hi = pos;
const R = /^(.*?)((?:010)*)(01110111|0)(1+)01010$/;
const Yre = /^(?:01)+$/;
const out = [];
function str(a, b) { let s = ''; for (let i = a; i < b; i++) s += tape[i] ? '1' : '0'; return s; }
let result = null;
while (steps < maxSteps) {
  const e = T[st][tape[pos]];
  if (!e) { result = ['HALT', steps]; break; }
  tape[pos] = e[0]; pos += e[1]; st = e[2]; steps++;
  if (pos < lo) lo = pos;
  if (st === 0 && pos === lo && tape[pos] === 0) {
    let j = hi; while (tape[j] === 0) j--;
    if (j > pos && (j - pos) % 2 === 0) { const s = str(pos + 1, j + 1); if (Yre.test(s)) out.push(['Y', s.length / 2, steps]); }
  }
  if (pos > hi) {
    hi = pos;
    if (st === 1) {
      let i = lo; while (tape[i] === 0) i++;
      if (pos - i < 5e6) {
        const s = str(i, pos);
        const m = R.exec(s);
        if (m && m[1].length <= +(process.env.PMAX || 16) && m[4].length >= 2) {
          const ev = [m[1], m[2].length / 3, m[3] === '01110111' ? 'P' : 'Q', m[4].length, steps];
          if (ev[1] >= AMIN && ev[2] === 'Q' && ev[3] === 3) { result = ['L', ev[0], ev[1], steps]; break; }
          out.push(ev);
        }
      }
    }
  }
  if (pos < 2 || pos > N - 3) { result = ['OVERFLOW', steps]; break; }
}
if (!result) result = ['LIMIT', steps];
console.log(JSON.stringify({ result, via: out.map(x => x.slice(0, 4)).slice(0, 40), nvia: out.length }));
