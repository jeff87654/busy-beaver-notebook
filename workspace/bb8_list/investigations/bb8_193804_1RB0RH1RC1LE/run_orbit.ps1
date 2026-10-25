$p = Start-Process -FilePath "C:\Users\jeffr\Downloads\bb8\third_party\venv311\Scripts\python.exe" -ArgumentList "orbit_check.py","6000000" -PassThru -NoNewWindow -RedirectStandardOutput "C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_193804_1RB0RH1RC1LE\orbit_out.txt" -WorkingDirectory "C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_193804_1RB0RH1RC1LE"
$p.PriorityClass = 'Idle'
$p.WaitForExit()
