$dir = "C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb43_1RB1RD1LC"
$v = "$dir\publish\BB43\verify"
$env:BUSYCOQ = "C:/Users/jeffr/Downloads/bb8/third_party/busycoq/verify"
$env:COQC = "C:/Coq-Platform~8.20~2025.01/bin/coqc.exe"
$p = Start-Process -FilePath "C:\Program Files\Git\bin\bash.exe" -ArgumentList @("-c","`"cd '/c/Users/jeffr/Downloads/bb8/bb8_list/investigations/bb43_1RB1RD1LC/publish/BB43/verify' && ./compile_clean.sh`"") -RedirectStandardOutput "$v\compile_clean.log" -RedirectStandardError "$v\compile_clean.err" -NoNewWindow -PassThru
$h = $p.Handle
try { $p.PriorityClass = 'Idle' } catch {}
Add-Content -Path "$dir\pids.txt" -Value ("{0} {1} bash compile_clean.sh (Idle; coqc children inherit)" -f $p.Id,(Get-Date -Format s))
$p.WaitForExit()
"exit=$($p.ExitCode)"
