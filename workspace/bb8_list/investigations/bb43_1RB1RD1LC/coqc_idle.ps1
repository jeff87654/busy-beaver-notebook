# usage: coqc_idle.ps1 <File.v>   -- compiles coq/<File.v> at Idle priority, logs PID to pids.txt, prints time + output
param([string]$f)
$dir = "C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb43_1RB1RD1LC"
$coq = Join-Path $dir "coq"
$bc = "C:\Users\jeffr\Downloads\bb8\third_party\busycoq\verify"
$src = Join-Path $coq $f
$out = Join-Path $coq ("log_" + ($f -replace '\.v$','') + ".txt")
$sw = [Diagnostics.Stopwatch]::StartNew()
$p = Start-Process -FilePath "C:\Coq-Platform~8.20~2025.01\bin\coqc.exe" -ArgumentList @("-Q","`"$bc`"","BusyCoq","-Q","`"$coq`"","TM43","`"$src`"") -WorkingDirectory $coq -RedirectStandardOutput $out -RedirectStandardError "$out.err" -NoNewWindow -PassThru
$h = $p.Handle
try { $p.PriorityClass = 'Idle' } catch {}
Add-Content -Path "$dir\pids.txt" -Value ("{0} {1} coqc {2}" -f $p.Id,(Get-Date -Format s),$f)
$p.WaitForExit()
$sw.Stop()
"exit=$($p.ExitCode) time=$([math]::Round($sw.Elapsed.TotalSeconds,1))s"
Get-Content $out
Get-Content "$out.err"
