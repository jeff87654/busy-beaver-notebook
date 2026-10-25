# Clean build of the BB(4,3) proof, in dependency order, at Idle priority (PIDs logged in pids.txt)
$dir = "C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb43_1RB1RD1LC"
Remove-Item "$dir\coq\*.vo","$dir\coq\*.vok","$dir\coq\*.vos","$dir\coq\*.glob" -ErrorAction SilentlyContinue
foreach ($f in @("BB43.v","Individual43.v","BB43_rules.v","BB43_run.v","BB43_score.v","probe.v")) {
  powershell -NoProfile -File "$dir\coqc_idle.ps1" $f | Select-String -NotMatch -Pattern "deprecat|instead|^File "
}
