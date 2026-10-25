param([string]$f)
$p = Start-Process -FilePath "C:\Users\jeffr\Downloads\bb8\third_party\venv311\Scripts\python.exe" -ArgumentList "coqc_scratch.py",$f -PassThru -NoNewWindow -RedirectStandardOutput "coq_out.txt" -WorkingDirectory "C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_193804_1RB0RH1RC1LE"
$p.PriorityClass = 'Idle'
$p.WaitForExit()
