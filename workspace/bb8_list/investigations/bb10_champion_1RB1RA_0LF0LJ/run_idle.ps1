param([string]$exe, [string]$args2, [string]$out)
$p = Start-Process -FilePath $exe -ArgumentList $args2 -RedirectStandardOutput $out -NoNewWindow -PassThru
$p.PriorityClass = 'Idle'
$p.Id | Out-File -Encoding ascii ($out + '.pid')
$p.WaitForExit()
