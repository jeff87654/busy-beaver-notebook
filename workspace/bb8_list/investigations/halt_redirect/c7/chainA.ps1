$ErrorActionPreference = 'Continue'
Set-Location C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\halt_redirect\c7
function RunIdle($a, $out) { $p = Start-Process -FilePath python -ArgumentList $a -RedirectStandardOutput $out -RedirectStandardError ($out + '.err') -WindowStyle Hidden -PassThru; $p.PriorityClass = 'Idle'; $p.WaitForExit() }
New-Item -ItemType Directory -Force logs8b | Out-Null
foreach ($m in Get-Content set8_loop.txt) { RunIdle @('ord_c7.py','--machine',$m,'--policy','big','--stages','24','--maxs','300000000','--log',"logs8b/big_$m.log") 'chA_1.out' }
RunIdle @('mfc7_batch.py','set9_time.txt','f9_time_1e8.tsv','1','40','100000000') 'chA_2.out'
'A-DONE' | Out-File chA.done -Encoding ascii
