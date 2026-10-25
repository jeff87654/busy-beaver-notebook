$p = Start-Process -FilePath "C:\Users\jeffr\Downloads\bb8\third_party\venv311\Scripts\python.exe" -ArgumentList "check.py","BB8_193804_1RB0RH_1RC1LE.v" -PassThru -NoNewWindow -RedirectStandardOutput "C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_193804_1RB0RH1RC1LE\check_out.txt" -RedirectStandardError "C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_193804_1RB0RH1RC1LE\check_err.txt" -WorkingDirectory "C:\Users\jeffr\Downloads\bb8\bb8_list\proofs"
$p.PriorityClass = 'Idle'
$p.WaitForExit()
