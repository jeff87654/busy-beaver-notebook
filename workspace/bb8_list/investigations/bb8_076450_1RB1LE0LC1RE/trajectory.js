// Literal simulation from the blank tape (no acceleration) of
//   1RB1LE_0LC1RE_0RA0LD_1RA1LC_1LF0RC_1RG1LC_0LH1LG_1LB---
// At every configuration with state G reading 0 and blank tape to its left, the word to the right is parsed as
//   P(j,t,s) = 1^(6j+5) (01)^t S_s   (S_0 = empty, S_1 = 11)       or   Y(n) = 1^n
// (P(j,0,0) = Y(6j+5) and P(j,0,1) = Y(6j+7) are reported as Y). Each family configuration must be the
// predicted successor of the previous one:
//   P(j,t+1,s) -> P(3j+4,t,s);  Y(6j+5) -> Y(18j+28);  Y(6j+4) -> Y(18j+21);
//   Y(6j+3) -> P(1,3j+1,1);     Y(6j+1) -> P(1,3j,0)
// Usage: node trajectory.js maxSteps [printEvery]
const TM = process.env.TM || "1RB1LE_0LC1RE_0RA0LD_1RA1LC_1LF0RC_1RG1LC_0LH1LG_1LB---";
const T = TM.split("_").map(ch => [0, 3].map(i => { const e = ch.substr(i, 3); if (e === "---") return null; return [+e[0], e[1] === "R" ? 1 : -1, e.charCodeAt(2) - 65]; }));
const Nn = 1 << 26; const tape = new Uint8Array(Nn);
let pos = Nn >> 1, st = 0, first1 = Nn, last1 = -1;
const maxSteps = +(process.argv[2] || 1e7);
const printEvery = +(process.argv[3] || 1);
const G = 6;
function key(f) { return f.join(','); }
function norm(f) { // canonical: P(j,0,0) -> Y(6j+5), P(j,0,1) -> Y(6j+7)
  if (f[0] === 'P' && f[2] === 0) return ['Y', 6 * f[1] + 5 + 2 * f[3]];
  return f;
}
function succ(f) {
  if (f[0] === 'P') return norm(['P', 3 * f[1] + 4, f[2] - 1, f[3]]);
  const n = f[1], r = n % 6, j = (n - r) / 6;
  if (r === 5) return ['Y', 18 * j + 28];
  if (r === 4) return ['Y', 18 * j + 21];
  if (r === 3) return norm(['P', 1, 3 * j + 1, 1]);
  if (r === 1) return norm(['P', 1, 3 * j, 0]);
  return null;
}
function parse() {
  let i = first1;
  while (i <= last1 && tape[i] === 1) i++;
  let n = i - first1;
  if (i > last1) return ['Y', n];
  let t = 0;
  while (i + 1 <= last1 && tape[i] === 0 && tape[i + 1] === 1) { t++; i += 2; }
  let s = 0;
  if (i + 1 === last1 && tape[i] === 1 && tape[i + 1] === 1) { s = 1; i += 2; }
  if (i !== last1 + 1) return null;
  if (n % 6 !== 5) return null;
  return norm(['P', (n - 5) / 6, t, s]);
}
let prev = null, prevStep = 0, found = 0, bad = 0, s = 0;
for (s = 1; s <= maxSteps; s++) {
  const r = tape[pos]; const e = T[st][r];
  if (!e) { console.log('HALT at step', s - 1, 'state', String.fromCharCode(65 + st), r); bad++; break; }
  tape[pos] = e[0];
  if (e[0] === 1) { if (pos < first1) first1 = pos; if (pos > last1) last1 = pos; }
  else if (pos === first1) { while (first1 <= last1 && tape[first1] === 0) first1++; }
  else if (pos === last1) { while (last1 >= first1 && tape[last1] === 0) last1--; }
  pos += e[1]; st = e[2];
  if (pos <= 0 || pos >= Nn - 1) { console.log('tape overflow'); break; }
  if (st === G && tape[pos] === 0 && pos < first1) {
    const f = parse();
    if (!f) continue;
    let tag = '';
    if (prev) {
      const p = succ(prev);
      if (!p || key(p) !== key(f)) { tag = ' MISMATCH predicted ' + (p ? key(p) : 'none'); bad++; }
    }
    found++;
    if (tag || found <= 40 || found % printEvery === 0 || f[0] === 'Y') console.log(`step ${s}: ${f[0]}(${f.slice(1)})  [+${s - prevStep}]${tag}`);
    prev = f; prevStep = s;
  }
}
console.log(`ran ${s - 1} steps; last: ${prev} at step ${prevStep}; found ${found} family configurations, ${bad} mismatches`);
