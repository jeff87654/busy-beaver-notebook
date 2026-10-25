// Literal simulation from the blank tape (no acceleration) of
//   1RB0LA_1RC1LE_0RD1RE_1LA---_1LG1RF_1RH0LG_1RH1LB_1RA0RG            (default, main)
//   1RB0LA_1RC1LE_0RD1RE_1LA---_1LG1RF_0LH0LG_1RH1LB_1RA0RG            (argument "variant", F0 = 0LH)
// At every step where the head (state E, reading 0) reaches a new leftmost cell, the word to its right is parsed.
// Main:    word = 1 (1010)^k 1^c 0 1  with k = 5m+2, c = 5q+1           -> VF(m,q)
//          successors: VF(m,q+1) -> VF(2m+1,q); VF(m,0) -> VF(0,4m+2)
// Variant: word = 1 1 0 (1010)^k rest; k = 5m+1, rest = 1^(5q) t, t in {1101, 11101, 1101111101, 1111} -> Fa(m,q,t)
//          k = 5m, rest empty -> Fb(m)
//          successors: Fa(m,q+1,t) -> Fa(2m+1,q,t); Fa(m,0,1101) -> Fa(0,4m+1,1111); Fa(m,0,11101) -> Fa(0,4m+1,1101111101);
//                      Fa(m,0,1101111101) -> Fa(0,4m+2,11101); Fa(m,0,1111) -> Fb(2m+1); Fb(m) -> Fa(0,4m,11101)
// Each family configuration must be the predicted successor of the previous one (a skipped one shows as a mismatch).
// Usage: node trajectory.js maxSteps [variant]
const VARIANT = process.argv[3] === 'variant';
const TM = VARIANT ? "1RB0LA_1RC1LE_0RD1RE_1LA---_1LG1RF_0LH0LG_1RH1LB_1RA0RG"
                   : "1RB0LA_1RC1LE_0RD1RE_1LA---_1LG1RF_1RH0LG_1RH1LB_1RA0RG";
const T = TM.split("_").map(ch => [0, 3].map(i => { const e = ch.substr(i, 3); if (e === "---") return null; return [+e[0], e[1] === "R" ? 1 : -1, e.charCodeAt(2) - 65]; }));
const N = 1 << 26; const tape = new Uint8Array(N);
let pos = N >> 1, st = 0, lo = pos, hi = pos;
const maxSteps = +(process.argv[2] || 1e8);
const TAILS = ['1101', '11101', '1101111101', '1111'];
function lastNonzero(from) { let e = hi; while (e >= from && tape[e] === 0) e--; return e; }
function parseMain() {
  let i = pos + 1;
  if (tape[i] !== 1) return null;
  i += 1; let k = 0;
  while (tape[i] === 1 && tape[i + 1] === 0 && tape[i + 2] === 1 && tape[i + 3] === 0) { k++; i += 4; }
  const e = lastNonzero(i);
  if (e < i) {  // word 1 (1010)^k: this is 1 (1010)^(k-1) 1 0 1 = VF((k-3)/5, 0)
    return (k % 5 === 3) ? ['VF', (k - 3) / 5, 0] : null;
  }
  if (k % 5 !== 2) return null;
  let c = 0; while (tape[i] === 1) { c++; i++; }
  if (!(tape[i] === 0 && tape[i + 1] === 1 && i + 1 === e)) return null;
  if (c % 5 !== 1) return null;
  return ['VF', (k - 2) / 5, (c - 1) / 5];
}
function parseVar() {
  let i = pos + 1;
  if (tape[i] !== 1 || tape[i + 1] !== 1 || tape[i + 2] !== 0) return null;
  i += 3; let k = 0;
  while (tape[i] === 1 && tape[i + 1] === 0 && tape[i + 2] === 1 && tape[i + 3] === 0) { k++; i += 4; }
  const e = lastNonzero(i);
  if (e < i) return (k % 5 === 0) ? ['Fb', k / 5] : null;
  if (k % 5 !== 1) return null;
  let c = 0; while (tape[i + c] === 1) c++;
  const restLen = e - i + 1;
  if (restLen > c + 12) return null;
  const rest = Array.from(tape.subarray(i, e + 1)).join('');
  for (const t of TAILS) {
    const L = rest.length - t.length;
    if (L >= 0 && L % 5 === 0 && rest.endsWith(t) && /^1*$/.test(rest.slice(0, L))) return ['Fa', (k - 1) / 5, L / 5, t];
  }
  return null;
}
function succ(f) {
  if (f[0] === 'VF') { const [, m, q] = f; return q > 0 ? ['VF', 2 * m + 1, q - 1] : ['VF', 0, 4 * m + 2]; }
  if (f[0] === 'Fb') return ['Fa', 0, 4 * f[1], '11101'];
  const [, m, q, t] = f;
  if (q > 0) return ['Fa', 2 * m + 1, q - 1, t];
  return { '1101': ['Fa', 0, 4 * m + 1, '1111'], '11101': ['Fa', 0, 4 * m + 1, '1101111101'],
           '1101111101': ['Fa', 0, 4 * m + 2, '11101'], '1111': ['Fb', 2 * m + 1] }[t];
}
let prev = null, found = 0, bad = 0, s;
for (s = 1; s <= maxSteps; s++) {
  const r = tape[pos]; const e = T[st][r];
  if (!e) { console.log('HALT at step', s - 1); bad++; break; }
  tape[pos] = e[0]; pos += e[1]; st = e[2];
  if (pos > hi) hi = pos;
  if (pos < lo) {
    lo = pos;
    if (st === 4) {  // E reading 0 at a new left edge: blank tape to the left
      const f = VARIANT ? parseVar() : parseMain();
      if (f) {
        found++;
        let ok = '';
        if (prev) { const p = succ(prev); ok = (p.join() === f.join()) ? 'ok' : ('MISMATCH expected ' + p.join()); if (ok !== 'ok') bad++; }
        console.log('step', s, f.join(','), ok);
        prev = f;
      }
    }
  }
  if (pos < 8 || pos > N - 8) { console.log('tape overflow at step', s); break; }
}
console.log('done', s - 1, 'steps;', found, 'family configurations,', bad, 'mismatches');
