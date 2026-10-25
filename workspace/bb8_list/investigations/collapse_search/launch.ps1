# usage: powershell -File launch.ps1 OUTFILE ERRFILE ARGS...   (runs cfollow.exe at Idle priority, appends PID to pids.txt)
param([string]$exe, [string]$out, [string]$err, [Parameter(ValueFromRemainingArguments=$true)][string[]]$rest)
$dir = "C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\collapse_search"
$p = Start-Process -FilePath "$dir\$exe" -ArgumentList $rest -WorkingDirectory $dir -RedirectStandardOutput "$dir\$out" -RedirectStandardError "$dir\$err" -WindowStyle Hidden -PassThru
try { $p.PriorityClass = 'Idle' } catch {}
Add-Content -Path "$dir\pids.txt" -Value ("{0}  {1}  {3} {2}" -f $p.Id, (Get-Date -Format 'yyyy-MM-dd HH:mm'), ($rest -join " "), $exe)
Write-Output $p.Id
