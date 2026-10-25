# plaunch.ps1 JOBS NPAR : run jobs (lines "exe|args|outfile", relative to this dir) at Idle priority, NPAR at a time; PIDs -> pids.txt
param([string]$jobs, [int]$npar = 4)
$dir = 'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_resid'
$run = @()
foreach ($l in Get-Content "$dir\$jobs") {
  if ($l.Trim() -eq '') { continue }
  $f = $l.Split('|')
  while (($run | Where-Object { -not $_.HasExited }).Count -ge $npar) { Start-Sleep 2 }
  $p = Start-Process -FilePath "$dir\$($f[0])" -ArgumentList $f[1] -WorkingDirectory $dir -RedirectStandardOutput "$dir\$($f[2])" -RedirectStandardError "$dir\$($f[2]).err" -PassThru -WindowStyle Hidden
  try { $p.PriorityClass = 'Idle' } catch {}
  Add-Content "$dir\pids.txt" ("{0} {1} {2} -> {3} ({4})" -f $p.Id, $f[0], $f[1], $f[2], (Get-Date -Format s))
  $run += $p
}
$run | ForEach-Object { $_.WaitForExit() }
Add-Content "$dir\pids.txt" ("# plaunch {0} done ({1})" -f $jobs, (Get-Date -Format s))
