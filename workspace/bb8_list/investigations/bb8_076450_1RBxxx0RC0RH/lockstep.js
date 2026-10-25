// Lockstep literal simulation (no acceleration) of
//   M = 1RB---_0RC0RH_0LD1RC_1RE1LE_1LF0LG_1LB0RD_1LA1LF_1RB1RH          (this investigation, start A)
//   V = 1RB1RA_0RC0RA_0LD1RC_1RE1LE_1LF0LG_1LB0RD_1LH1LF_1RB---          (proved variant G0_1LH_H0_1RB, start A)
// Checks (1) that swapping the state names A <-> H in M gives exactly V, and (2) that from the blank tape
// both machines write the same symbol, move the same way and are in corresponding states (M's state
// relabeled) at every step up to maxSteps. Also counts M's transition usage.
// Usage: node lockstep.js [maxSteps]
const M = "1RB---_0RC0RH_0LD1RC_1RE1LE_1LF0LG_1LB0RD_1LA1LF_1RB1RH";
const V = "1RB1RA_0RC0RA_0LD1RC_1RE1LE_1LF0LG_1LB0RD_1LH1LF_1RB---";
const perm = { A: 'H', H: 'A' };               // relabeling of M's states
const rel = q => perm[q] || q;
// (1) textual relabeling check
const rowsM = M.split('_'), idx = q => q.charCodeAt(0) - 65;
const relRows = new Array(8);
rowsM.forEach((row, i) => {
  const q = String.fromCharCode(65 + i);
  const t = [0, 3].map(j => { const e = row.substr(j, 3); return e === '---' ? e : e.slice(0, 2) + rel(e[2]); }).join('');
  relRows[idx(rel(q))] = t;
});
const relM = relRows.join('_');
console.log('M relabeled (A<->H):', relM);
console.log('equals V:', relM === V);
// (2) lockstep literal run
const parse = TM => TM.split("_").map(ch => [0, 3].map(i => { const e = ch.substr(i, 3); if (e === "---") return null; return [+e[0], e[1] === "R" ? 1 : -1, e.charCodeAt(2) - 65]; }));
const TM_ = parse(M), TV = parse(V);
const Nn = 1 << 25; const tm = new Uint8Array(Nn), tv = new Uint8Array(Nn);
let pm = Nn >> 1, pv = Nn >> 1, sm = 0, sv = 0;       // M starts in A; V starts in A
const relIdx = q => q === 0 ? 7 : (q === 7 ? 0 : q);
const usage = {};
const maxSteps = +(process.argv[2] || 1e9);
let s, bad = 0;
// step 1: M in A, V in A (not the image H of M's A); both A0 = 1RB, so after one step both are in B.
for (s = 1; s <= maxSteps; s++) {
  const rm = tm[pm], rv = tv[pv];
  const em = TM_[sm][rm], ev = TV[sv][rv];
  const k = String.fromCharCode(65 + sm) + rm; usage[k] = (usage[k] || 0) + 1;
  if (!em || !ev) { console.log('halt at step', s - 1, 'M', !!em, 'V', !!ev); if (!!em !== !!ev) bad++; break; }
  if (em[0] !== ev[0] || em[1] !== ev[1] || relIdx(em[2]) !== ev[2] || rm !== rv || pm !== pv) {
    console.log('MISMATCH at step', s); bad++; break;
  }
  tm[pm] = em[0]; tv[pv] = ev[0]; pm += em[1]; pv += ev[1]; sm = em[2]; sv = ev[2];
  if (pm <= 0 || pm >= Nn - 1) { console.log('tape overflow at step', s); break; }
}
console.log(`ran ${s - 1} steps in lockstep; mismatches: ${bad}`);
console.log('M transition usage:', Object.keys(usage).sort().map(k => k + '=' + usage[k]).join(' '));
