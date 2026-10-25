# Literal blank-tape trajectories (1e9 steps each) of the 12 F1-family machines at Idle priority,
# checked against the fitted rules in params.tsv (ktraj.js).  Output: traj_all.txt
$dir = "C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\neighbors_F1"
$out = Join-Path $dir "traj_all.txt"
if (Test-Path $out) { Remove-Item $out }
foreach ($line in Get-Content (Join-Path $dir "params.tsv")) {
  $f = $line -split "`t"
  $tm = $f[0]; $shape = $f[1]; $params = $f[2]
  $st = "B"; $suf = "01"
  if ($shape -eq "F,0") { $st = "F"; $suf = "0" }
  $tmp = Join-Path $dir "traj_one.txt"
  $pj = '"' + ($params -replace '"', '\"') + '"'
  $p = Start-Process -FilePath "node" -ArgumentList "..\neighbors_family_tools\ktraj.js", $tm, $pj, "1000000000", $st, $suf `
       -WorkingDirectory $dir -RedirectStandardOutput $tmp -PassThru -NoNewWindow
  try { $p.PriorityClass = 'Idle' } catch {}
  $p.WaitForExit()
  Add-Content -Path $out -Value "== $tm" -Encoding utf8
  Get-Content $tmp | Add-Content -Path $out -Encoding utf8
}
Remove-Item (Join-Path $dir "traj_one.txt")
"done"
