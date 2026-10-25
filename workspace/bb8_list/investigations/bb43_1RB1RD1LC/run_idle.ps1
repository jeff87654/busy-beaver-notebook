# usage: run_idle.ps1 <exe> <outfile> <args...>   -- runs at Idle priority, records PID in pids.txt, waits
param([string]$exe,[string]$out,[Parameter(ValueFromRemainingArguments=$true)][string[]]$rest)
$dir = "C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb43_1RB1RD1LC"
$p = Start-Process -FilePath $exe -ArgumentList $rest -RedirectStandardOutput $out -RedirectStandardError "$out.err" -NoNewWindow -PassThru
try { $p.PriorityClass = 'Idle' } catch {}
Add-Content -Path "$dir\pids.txt" -Value ("{0} {1} {2} {3}" -f $p.Id,(Get-Date -Format s),$exe,($rest -join ' '))
$p.WaitForExit()
