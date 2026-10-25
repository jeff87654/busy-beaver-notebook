$d = "C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\longcensus"; $exe = "C:\Users\jeffr\Downloads\bb8\bb8_list\neighbors\dlscan2.exe"
$ps = @(); foreach ($k in 0..3) { $p = Start-Process $exe -ArgumentList "$d\sample_$k.txt","$d\long_$k.tsv","500000000","20000" -PassThru -WindowStyle Hidden; $p.PriorityClass = 'Idle'; $ps += $p }
$b = Start-Process $exe -ArgumentList "$d\sample_all.txt","$d\base.tsv","5000000","20000" -PassThru -WindowStyle Hidden; $b.PriorityClass = 'Idle'
$ps + $b | ForEach-Object { $_.WaitForExit() }
Set-Content "$d\done.txt" "done" -Encoding ascii
