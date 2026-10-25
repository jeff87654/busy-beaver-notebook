// Independent, literal one-transition-at-a-time simulator. No macro rules.
const fs = require('node:fs');
const machines = JSON.parse(fs.readFileSync('run2_merged.json', 'utf8'));
const [expectedSteps, expectedOnes, machine] = machines.best[0];
const chunks = machine.split('_');
const transitions = chunks.flatMap(c => [0,3].map(i => ({
  write: Number(c[i]), direction: c[i+1] === 'R' ? 1 : -1,
  next: c[i+2] === 'Z' ? -1 : c.charCodeAt(i+2)-65
})));
const tape = new Uint8Array(4_000_001);
let position = 2_000_000, state = 0, steps = 0, ones = 0;
let minPosition = position, maxPosition = position;
const start = Date.now();
while (state >= 0 && steps < 200_000_000) {
  const symbol = tape[position];
  const transition = transitions[2*state+symbol];
  tape[position] = transition.write;
  ones += transition.write-symbol;
  position += transition.direction;
  state = transition.next;
  steps++;
  if (position < minPosition) minPosition = position;
  if (position > maxPosition) maxPosition = position;
  if (position < 0 || position >= tape.length) throw Error('Tape capacity exceeded');
}
const result = {machine, halted:state===-1, steps, ones,
  visitedPositions: [minPosition-2_000_000, maxPosition-2_000_000],
  elapsedSeconds:(Date.now()-start)/1000,
  expectedSteps,expectedOnes,verified:state===-1&&steps===expectedSteps&&ones===expectedOnes};
console.log(JSON.stringify(result,null,2));
fs.writeFileSync('audit_verification.json',JSON.stringify(result,null,2)+'\n');
