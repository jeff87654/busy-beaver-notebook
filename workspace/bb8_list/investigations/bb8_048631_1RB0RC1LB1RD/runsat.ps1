$M = "1RB---_0RC1LG_1LB1RD_0RE1RA_1RF0LC_1LE1RG_0LH1RE_0RB1LG"
$out = "C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_048631_1RB0RC1LB1RD\sat_runs.txt"
foreach ($p in @(@(4,7),@(7,4),@(3,8),@(8,3),@(5,8),@(8,5))) {
  $proc = Start-Process -FilePath python -ArgumentList "sat2dfa.py",$M,$p[0],$p[1] -WorkingDirectory "C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_048631_1RB0RC1LB1RD" -RedirectStandardOutput "$out.tmp" -NoNewWindow -PassThru
  $proc.PriorityClass = 'Idle'
  if (-not $proc.WaitForExit(240000)) { $proc.Kill(); Add-Content $out "$($p[0]) $($p[1]) TIMEOUT" } else { Get-Content "$out.tmp" | Add-Content $out }
}
