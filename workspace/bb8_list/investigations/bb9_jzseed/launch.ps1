# launch.ps1 <exe> <stdin-file or -> <stdout-file> <args...> : start at Idle priority, append PID to pids.txt
param([string]$exe, [string]$inf, [string]$out, [Parameter(ValueFromRemainingArguments=$true)][string[]]$rest)
$dir = 'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_jzseed'
$a = @{ FilePath = $exe; RedirectStandardOutput = "$dir\$out"; RedirectStandardError = "$dir\$out.err"; WorkingDirectory = $dir; PassThru = $true; WindowStyle = 'Hidden' }
if ($rest.Count -gt 0) { $a.ArgumentList = $rest }
if ($inf -ne '-') { $a.RedirectStandardInput = "$dir\$inf" }
$p = Start-Process @a
$p.PriorityClass = 'Idle'
Add-Content "$dir\pids.txt" ("{0} {1} {2} -> {3} ({4})" -f $p.Id, $exe, ($rest -join ' '), $out, (Get-Date -Format s))
Write-Output $p.Id
