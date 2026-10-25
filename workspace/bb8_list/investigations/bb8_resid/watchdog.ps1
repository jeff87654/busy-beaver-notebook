# watchdog.ps1 PARENTPIDS(comma) MINUTES : every 30 s kill pkf6/pkf7/zfg children of the given parents older than MINUTES; exit when parents are gone
param([string]$parents, [double]$mins = 10)
$dir = 'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_resid'
$ps = $parents.Split(',') | ForEach-Object { [int]$_ }
while ($true) {
  $alive = $ps | Where-Object { Get-Process -Id $_ -ErrorAction SilentlyContinue }
  if (-not $alive) { break }
  Get-CimInstance Win32_Process | Where-Object { ($ps -contains $_.ParentProcessId) -and ($_.Name -like 'pkf*' -or $_.Name -like 'zfg*') } | ForEach-Object {
    $pr = Get-Process -Id $_.ProcessId -ErrorAction SilentlyContinue
    if ($pr -and ((Get-Date) - $pr.StartTime).TotalMinutes -gt $mins) { Stop-Process -Id $_.ProcessId -Force; Add-Content "$dir\pids.txt" "$($_.ProcessId) $($_.Name) killed by watchdog (> $mins min)" }
  }
  Start-Sleep 30
}
