$ErrorActionPreference = 'Continue'
Set-Location C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\halt_redirect\c7
function RunIdle($args, $out) { $p = Start-Process -FilePath python -ArgumentList $args -RedirectStandardOutput $out -RedirectStandardError ($out + '.err') -WindowStyle Hidden -PassThru; $p.PriorityClass = 'Idle'; $p.WaitForExit() }
RunIdle @('mfc7_batch.py','set8_time.txt','mf8_time_1e8.tsv','1','60','100000000') 'chain8_a.out'
RunIdle @('mfc7_batch.py','set8_loop.txt','mf8_loop_b20.tsv','1','40','10000000','20') 'chain8_b.out'
RunIdle @('mfc7_batch.py','set8_loop.txt','mf8_loop_b34.tsv','1','40','10000000','34') 'chain8_c.out'
New-Item -ItemType Directory -Force logs8 | Out-Null
foreach ($m in Get-Content set8_loop.txt) { RunIdle @('ord_c7.py','--machine',$m,'--policy','big','--stages','30','--maxs','300000000','--log',"logs8/big_$m.log") 'chain8_d.out' }
'CHAIN8-DONE' | Out-File chain8.done -Encoding ascii
