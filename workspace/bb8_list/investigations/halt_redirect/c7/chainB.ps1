$ErrorActionPreference = 'Continue'
Set-Location C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\halt_redirect\c7
function RunIdle($a, $out) { $p = Start-Process -FilePath python -ArgumentList $a -RedirectStandardOutput $out -RedirectStandardError ($out + '.err') -WindowStyle Hidden -PassThru; $p.PriorityClass = 'Idle'; $p.WaitForExit() }
RunIdle @('mfc7_batch.py','set9_max.txt','f9_max80.tsv','1','80','3000000') 'chB_1.out'
RunIdle @('branch_c7.py','mf_out.tsv','f9_max80.tsv','f9_time_1e8.tsv','--out','br2_out.tsv','--st','30','--maxs','3e7','--minst','1','--levels','3') 'chB_2.out'
'B-DONE' | Out-File chB.done -Encoding ascii
