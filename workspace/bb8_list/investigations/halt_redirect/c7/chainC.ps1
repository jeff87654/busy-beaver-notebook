$ErrorActionPreference = 'Continue'
Set-Location C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\halt_redirect\c7
function RunIdle($a, $out) { $p = Start-Process -FilePath python -ArgumentList $a -RedirectStandardOutput $out -RedirectStandardError ($out + '.err') -WindowStyle Hidden -PassThru; $p.PriorityClass = 'Idle'; $p.WaitForExit() }
RunIdle @('mfc7_batch.py','set_lvl1.txt','f_lvl1_b20.tsv','1','30','30000000','20') 'chC_1.out'
RunIdle @('mfc7_batch.py','set_lvl1.txt','f_lvl1_b34.tsv','1','30','60000000','34') 'chC_2.out'
RunIdle @('mfc7_batch.py','set_all.txt','mf_b20.tsv','3','14','10000000','20') 'chC_3.out'
'C-DONE' | Out-File chC.done -Encoding ascii
