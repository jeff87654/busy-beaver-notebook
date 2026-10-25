// Literal simulation from the blank tape (no acceleration) with a check of every K-family configuration
// against the successor predicted by fitted rules (kfit.py --params).
//
//   node ktraj.js TM PARAMS_JSON maxSteps [STATE SUFFIX]        (default shape: B 01)
//
// K(ds; a; b) = 0^inf 1^d1 0 ... 0 1^dn 0 1^a 0 1^b SUFFIX STATE> 0^inf   (parent: suffix "01", state B)
// PARAMS_JSON = {"m1":..,"c1":..,"m2":..,"c2":..,"b2":..,"m3":..,"c3":..,"a3":..,"b3":..,"mh":..,"ch":..,
//                "P":[..],"m4":..,"c4":..,"a4":..,"b4":..}   rules as in kfit.py:
//   a>=1: K(ds;a-1;m1 b+c1)  (ds empty and a=1: next parseable configuration is the R4 result of m1 b+c1)
//   a=0, last digit x+1: K(..,x; m2 b+c2; b2);  k trailing zero digits, k < mh b+ch: K(..,y,m3 b+c3-k,1^(k-1); a3; b3)
//   k = mh b + ch: HALT;  no digits: K(P,1^(m4 b+c4); a4; b4)
const TM = process.argv[2];
const R = JSON.parse(process.argv[3]);
const maxSteps = +(process.argv[4] || 1e8);
const QS = process.argv[5] || 'B', SUF = (process.argv[6] || '01').split('').map(Number);
const qK = QS.charCodeAt(0) - 65;
const T = TM.split("_").map(ch => [0, 3].map(i => { const e = ch.substr(i, 3); if (e === "---") return null; return [+e[0], e[1] === "R" ? 1 : -1, e.charCodeAt(2) - 65]; }));
const Nn = 1 << 26; const tape = new Uint8Array(Nn);
let pos = Nn >> 1, st = 0, first1 = Nn, last1 = -1;
function parse() {
  const n = SUF.length;
  for (let i = 0; i < n; i++) if (tape[pos - n + i] !== SUF[i]) return null;
  const runs = []; let cur = 0;
  for (let i = first1; i <= pos - n - 1; i++) { if (tape[i] === 1) cur++; else { runs.push(cur); cur = 0; } }
  runs.push(cur);
  if (runs.length < 2) return null;
  const ds = runs.slice(0, runs.length - 2);
  if (ds.length && ds[0] === 0) return null;
  return [ds, runs[runs.length - 2], runs[runs.length - 1]];
}
function strip(ds) { while (ds.length && ds[0] === 0) ds.shift(); return ds; }
function r4(b) { return [strip(R.P.concat(Array(Math.max(0, R.m4 * b + R.c4)).fill(1))), R.a4, R.b4]; }
function predict(f) {
  let [ds, a, b] = f; ds = ds.slice();
  if (a >= 1) { const nb = R.m1 * b + R.c1; if (!ds.length && a === 1) return r4(nb); return [ds, a - 1, nb]; }
  let k = 0; while (k < ds.length && ds[ds.length - 1 - k] === 0) k++;
  if (k === ds.length) return r4(b);
  const i = ds.length - 1 - k;
  if (k === 0) { ds[ds.length - 1]--; return [strip(ds), R.m2 * b + R.c2, R.b2]; }
  const kh = R.mh * b + R.ch;
  if (k < kh) { ds[i]--; ds = ds.slice(0, i + 1).concat([R.m3 * b + R.c3 - k], Array(k - 1).fill(1)); return [strip(ds), R.a3, R.b3]; }
  if (k === kh) return 'HALT';
  return null;
}
function key(f) { return JSON.stringify(f); }
function show(f) { const ds = f[0]; const s = ds.length > 12 ? ds.slice(0, 6).join(',') + ',...(' + ds.length + ' digits)' : ds.join(','); return `K(${s}; ${f[1]}; ${f[2]})`; }
let prev = null, prevStep = 0, found = 0, bad = 0, s, halted = false;
for (s = 1; s <= maxSteps; s++) {
  const r = tape[pos]; const e = T[st][r];
  if (!e) { console.log('HALT at step', s - 1, prev ? 'predicted: ' + key(predict(prev)) : ''); halted = true; break; }
  tape[pos] = e[0];
  if (e[0] === 1) { if (pos < first1) first1 = pos; if (pos > last1) last1 = pos; }
  else if (pos === first1) { while (first1 <= last1 && tape[first1] === 0) first1++; }
  else if (pos === last1) { while (last1 >= first1 && tape[last1] === 0) last1--; }
  pos += e[1]; st = e[2];
  if (pos <= 0 || pos >= Nn - 1) { console.log('tape overflow'); break; }
  if (st === qK && tape[pos] === 0 && pos > last1) {
    const f = parse();
    if (!f) continue;
    let tag = '';
    if (prev) { const p = predict(prev); if (p === null || p === 'HALT' || key(p) !== key(f)) { tag = ' MISMATCH predicted ' + (p && p !== 'HALT' ? show(p) : String(p)); bad++; } }
    found++;
    console.log(`step ${s}: ${show(f)}  [+${s - prevStep}]${tag}`);
    prev = f; prevStep = s;
  }
}
console.log(`ran ${s - 1} steps; found ${found} family configurations, ${bad} mismatches${halted ? ', HALTED' : ''}`);
