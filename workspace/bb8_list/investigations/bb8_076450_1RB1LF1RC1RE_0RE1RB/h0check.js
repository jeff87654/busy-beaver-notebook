// Check that every H0 transition (literal run from the blank tape) is executed at the left end of the word,
// i.e. with no 1 at or to the left of the head's left neighbour. Usage: [TM=...] node h0check.js maxSteps
const TM = process.env.TM || "1RB1LF_1RC1RE_1RD0LG_0RE1RB_1LA0LC_0RG1LA_---0LH_0LC1LC";
const T = TM.split("_").map(ch => [0, 3].map(i => { const e = ch.substr(i, 3); if (e === "---") return null; return [+e[0], e[1] === "R" ? 1 : -1, e.charCodeAt(2) - 65]; }));
const Nn = 1 << 24; const tape = new Uint8Array(Nn);
let pos = Nn >> 1, st = 0, first1 = Nn, last1 = -1, h0 = 0, bad = 0;
const maxSteps = +(process.argv[2] || 1e8);
for (let s = 1; s <= maxSteps; s++) {
  const r = tape[pos]; const e = T[st][r];
  if (!e) { console.log('HALT'); break; }
  if (st === 7 && r === 0) { h0++; if (pos - 1 >= first1) { bad++; if (bad < 5) console.log('H0 not at left end, step', s); } }
  tape[pos] = e[0];
  if (e[0] === 1) { if (pos < first1) first1 = pos; if (pos > last1) last1 = pos; }
  else if (pos === first1) { while (first1 <= last1 && tape[first1] === 0) first1++; }
  else if (pos === last1) { while (last1 >= first1 && tape[last1] === 0) last1--; }
  pos += e[1]; st = e[2];
}
console.log(TM, 'H0 uses', h0, 'not at left end', bad);
