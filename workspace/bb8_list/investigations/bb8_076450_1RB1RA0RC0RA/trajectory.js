// Literal simulation from the blank tape (no acceleration) of
//   1RB1RA_0RC0RA_0LD1RC_1RE1LE_1LF0LG_1LB0RD_0LH1LF_1RF---   (or TM env var)
// At every configuration with state B reading 0 right of the last 1, preceded by "0 1", the tape is parsed as
//   K(ds; a; b) = 0^inf 1^d1 0 ... 0 1^dn 0 1^a 0 1^b 0 1 B> 0^inf     (ds printed top digit first)
// and compared with the successor predicted from the previous family configuration:
//   a>=1: K(ds;a-1;4b+4);  a=0, last digit x+1: K(..,x;4b+3;1);
//   a=0, k trailing zero digits, 1<=k<=4b: K(..,y,4b+3-k,1^(k-1);1;1);  a=0, no digits: K(2,1^(4b);1;1)
// Usage: node trajectory.js maxSteps
const TM = process.env.TM || "1RB1RA_0RC0RA_0LD1RC_1RE1LE_1LF0LG_1LB0RD_0LH1LF_1RF---";
const T = TM.split("_").map(ch => [0, 3].map(i => { const e = ch.substr(i, 3); if (e === "---") return null; return [+e[0], e[1] === "R" ? 1 : -1, e.charCodeAt(2) - 65]; }));
const Nn = 1 << 25; const tape = new Uint8Array(Nn);
let pos = Nn >> 1, st = 0, first1 = Nn, last1 = -1;
const maxSteps = +(process.argv[2] || 1e8);
function parse() {
  // runs separated by single zeros, from first1 to pos-3 ; tape[pos-1]=1, tape[pos-2]=0 checked by caller
  const runs = []; let cur = 0;
  for (let i = first1; i <= pos - 3; i++) { if (tape[i] === 1) cur++; else { runs.push(cur); cur = 0; } }
  runs.push(cur);
  if (runs.length < 2) return null;
  const ds = runs.slice(0, runs.length - 2);
  if (ds.length && ds[0] === 0) return null;
  return [ds, runs[runs.length - 2], runs[runs.length - 1]];
}
function key(f) { return f ? JSON.stringify(f) : 'null'; }
function predict(f) {
  let [ds, a, b] = f; ds = ds.slice();
  if (a >= 1) { if (!ds.length && a === 1) return [[2].concat(Array(4 * (4 * b + 4)).fill(1)), 1, 1]; return [ds, a - 1, 4 * b + 4]; }
  let k = 0; while (k < ds.length && ds[ds.length - 1 - k] === 0) k++;
  if (k === ds.length) return [[2].concat(Array(4 * b).fill(1)), 1, 1];
  const i = ds.length - 1 - k; let out;
  if (k === 0) { ds[ds.length - 1]--; out = [ds, 4 * b + 3, 1]; }
  else if (k <= 4 * b) { ds[i]--; ds = ds.slice(0, i + 1).concat([4 * b + 3 - k], Array(k - 1).fill(1)); out = [ds, 1, 1]; }
  else return null;
  while (out[0].length && out[0][0] === 0) out[0].shift();
  return out;
}
function show(f) { const ds = f[0]; let s = ds.length > 12 ? ds.slice(0, 6).join(',') + ',...(' + ds.length + ' digits)' : ds.join(','); return `K(${s}; ${f[1]}; ${f[2]})`; }
let prev = null, prevStep = 0, found = 0, bad = 0, s;
for (s = 1; s <= maxSteps; s++) {
  const r = tape[pos]; const e = T[st][r];
  if (!e) { console.log('HALT at step', s - 1); bad++; break; }
  tape[pos] = e[0];
  if (e[0] === 1) { if (pos < first1) first1 = pos; if (pos > last1) last1 = pos; }
  else if (pos === first1) { while (first1 <= last1 && tape[first1] === 0) first1++; }
  else if (pos === last1) { while (last1 >= first1 && tape[last1] === 0) last1--; }
  pos += e[1]; st = e[2];
  if (pos <= 0 || pos >= Nn - 1) { console.log('tape overflow'); break; }
  if (st === 1 && tape[pos] === 0 && pos === last1 + 1 && tape[pos - 2] === 0) {
    const f = parse();
    if (!f) continue;
    let tag = '';
    if (prev) { const p = predict(prev); if (key(p) !== key(f)) { tag = ' MISMATCH predicted ' + (p ? show(p) : 'none'); bad++; } }
    found++;
    console.log(`step ${s}: ${show(f)}  [+${s - prevStep}]${tag}`);
    prev = f; prevStep = s;
  }
}
console.log(`ran ${s - 1} steps; found ${found} family configurations, ${bad} mismatches`);
