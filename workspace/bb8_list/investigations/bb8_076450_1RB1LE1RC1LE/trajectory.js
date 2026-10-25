// Literal simulation from the blank tape (no acceleration) of
//   1RB1LE_1RC1LE_0RD1RE_1LA---_1LG1RF_0LH0LG_1RH1LB_0RA0RG            (default)
//   1RB1LE_1RC1LE_0RD1RE_1LA---_1LG1RF_1RH0LG_1RH1LB_0RA0RG            (TM=variant)
// At every configuration with state E reading 0 and a blank tape to its left, the word to the right is parsed.
// Main machine: word = 1 1 0 (1010)^k 1^c   ->  Fa(m,q,t) if k = 5m+1, c = 5q + t (t = 0 or 4);  Fb(m) if k = 5m, c = 0
//   successors: Fa(m,q+1,t) -> Fa(2m+1,q,t); Fa(m,0,4) -> Fb(2m+1); Fa(m,0,0) -> Fa(0,4m+1,4); Fb(m) -> Fa(0,4m+1,0)
// Variant: word = 1 (1010)^k 1^(5q) t with k = 5m+2 and t in {11, 111, 11 010111, 1111 0111, 1} -> VF(m,q,t)
//   successors: VF(m,q+1,t) -> VF(2m+1,q,t); VF(m,0,11) -> VF(0,4m+1,111); VF(m,0,111) -> VF(0,4m+1,11w);
//               VF(m,0,11w) -> VF(0,4m+1,1111w); VF(m,0,1111w) -> VF(0,8m+5,1); VF(m,0,1) -> VF(0,4m+2,1)
// Each family configuration must be the predicted successor of the previous one.
// Usage: node trajectory.js maxSteps [variant]
const VARIANT = process.argv[3] === 'variant';
const TM = VARIANT ? "1RB1LE_1RC1LE_0RD1RE_1LA---_1LG1RF_1RH0LG_1RH1LB_0RA0RG"
                   : "1RB1LE_1RC1LE_0RD1RE_1LA---_1LG1RF_0LH0LG_1RH1LB_0RA0RG";
const T = TM.split("_").map(ch => [0, 3].map(i => { const e = ch.substr(i, 3); if (e === "---") return null; return [+e[0], e[1] === "R" ? 1 : -1, e.charCodeAt(2) - 65]; }));
const N = 1 << 26; const tape = new Uint8Array(N);
let pos = N >> 1, st = 0, lo = pos, hi = pos;
const maxSteps = +(process.argv[2] || 1e8);
const TAILS = { '11': '11', '111': '111', '11w': '11010111', '1111w': '11110111', '1': '1' };
function parseMain() {
  let i = pos + 1;
  if (tape[i] !== 1 || tape[i + 1] !== 1 || tape[i + 2] !== 0) return null;
  i += 3; let k = 0;
  while (i + 3 <= hi + 4 && tape[i] === 1 && tape[i + 1] === 0 && tape[i + 2] === 1 && tape[i + 3] === 0) { k++; i += 4; }
  let c = 0; while (tape[i] === 1) { c++; i++; }
  for (let j = i; j <= hi; j++) if (tape[j]) return null;
  if (k % 5 === 1 && (c % 5 === 0 || c % 5 === 4)) return ['Fa', (k - 1) / 5, Math.floor(c / 5), c % 5];
  if (k % 5 === 0 && c === 0) return ['Fb', k / 5];
  return null;
}
function parseVar() {
  let i = pos + 1;
  if (tape[i] !== 1) return null;
  i += 1; let k = 0;
  while (tape[i] === 1 && tape[i + 1] === 0 && tape[i + 2] === 1 && tape[i + 3] === 0) { k++; i += 4; }
  if (k % 5 !== 2) return null;
  let e = hi; while (e > i && tape[e] === 0) e--;
  const rest = Array.from(tape.subarray(i, e + 1)).join('');
  for (const [name, t] of Object.entries(TAILS)) {
    const L = rest.length - t.length;
    if (L >= 0 && L % 5 === 0 && rest.endsWith(t) && /^1*$/.test(rest.slice(0, L))) return ['VF', (k - 2) / 5, L / 5, name];
  }
  return null;
}
function succ(f) {
  if (f[0] === 'Fa') {
    const [, m, q, t] = f;
    if (q > 0) return ['Fa', 2 * m + 1, q - 1, t];
    return t === 4 ? ['Fb', 2 * m + 1] : ['Fa', 0, 4 * m + 1, 4];
  }
  if (f[0] === 'Fb') return ['Fa', 0, 4 * f[1] + 1, 0];
  const [, m, q, t] = f;
  if (q > 0) return ['VF', 2 * m + 1, q - 1, t];
  return { '11': ['VF', 0, 4 * m + 1, '111'], '111': ['VF', 0, 4 * m + 1, '11w'], '11w': ['VF', 0, 4 * m + 1, '1111w'],
           '1111w': ['VF', 0, 8 * m + 5, '1'], '1': ['VF', 0, 4 * m + 2, '1'] }[t];
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
