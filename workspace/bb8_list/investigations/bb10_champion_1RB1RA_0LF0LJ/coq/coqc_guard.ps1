# Run coqc on one file with a memory/time guard (kills only the coqc it started).
param([string]$file, [int]$maxMB = 3000, [int]$maxSec = 600, [int]$tail = 30)
$coqc = 'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
$busy = (Resolve-Path 'C:\Users\jeffr\Downloads\bb8\third_party\busycoq\verify').Path
$proofs = 'C:\Users\jeffr\Downloads\bb8\bb8_list\proofs'
$out = [System.IO.Path]::GetTempFileName(); $err = [System.IO.Path]::GetTempFileName()
$p = Start-Process -FilePath $coqc -ArgumentList @('-Q', $busy, 'BusyCoq', '-Q', $proofs, 'BB8', $file) -WorkingDirectory (Split-Path $file) -RedirectStandardOutput $out -RedirectStandardError $err -NoNewWindow -PassThru
$p.PriorityClass = 'Idle'
$t0 = Get-Date; $peak = 0; $killed = $false
while (-not $p.HasExited) {
  Start-Sleep -Milliseconds 500
  try { $p.Refresh(); $mb = [int]($p.WorkingSet64 / 1MB) } catch { $mb = 0 }
  if ($mb -gt $peak) { $peak = $mb }
  if ($mb -gt $maxMB -or ((Get-Date) - $t0).TotalSeconds -gt $maxSec) { Stop-Process -Id $p.Id -Force; $killed = $true; break }
}
$p.WaitForExit()
$secs = [int]((Get-Date) - $t0).TotalSeconds
"EXIT=$($p.ExitCode) KILLED=$killed PEAK_MB=$peak SECS=$secs"
Get-Content $out | Select-Object -Last $tail
Get-Content $err | Select-Object -Last $tail
Remove-Item $out, $err
