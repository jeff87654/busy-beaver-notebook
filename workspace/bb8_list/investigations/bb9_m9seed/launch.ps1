# usage: launch.ps1 <outfile> <args...>   starts m9s.exe at Idle priority, appends PID to pids.txt
param([string]$out, [string]$errf, [string]$inf, [Parameter(ValueFromRemainingArguments=$true)][string[]]$rest)
$dir = 'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_m9seed'
$a = @{ FilePath = "$dir\m9s_v3.exe"; ArgumentList = $rest; RedirectStandardOutput = "$dir\$out"; RedirectStandardError = "$dir\$errf"; WorkingDirectory = $dir; PassThru = $true; WindowStyle = 'Hidden' }
if ($inf -ne '-') { $a.RedirectStandardInput = "$dir\$inf" }
$p = Start-Process @a
$p.PriorityClass = 'Idle'
Add-Content "$dir\pids.txt" ("{0} m9s {1} -> {2} ({3})" -f $p.Id, ($rest -join ' '), $out, (Get-Date -Format s))
Write-Output $p.Id
