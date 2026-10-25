# cpucap.ps1 - keep all BB(8)-project computation within a hard CPU cap (user decision 2026-10-08: at most 4 cores).
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File cpucap.ps1 [-Percent 25] [-Every 60]
#
# Creates a Windows job object with a hard CPU-rate cap (Percent of the whole machine; 25% = 4 of 16 logical cores)
# and every Every seconds assigns to it:
#   - every process whose executable lives under C:\Users\jeffr\Downloads\bb8 (knuth*, mxdys*, dlscan*, sim9, renum, ...),
#   - coqc.exe,
#   - python processes running one of the project's scripts (by script name, see $Scripts), any python whose command
#     line mentions the bb8 tree or a Claude job folder, and any python started with a RELATIVE script path (the
#     sessions launch them from project folders; the user's own scripts, e.g. frame_remote.py, use absolute paths),
#   - all descendants of the processes above (children started later inherit the job automatically).
# Nothing else on the machine is touched. The cap lasts while this script runs (it holds the job handle); stop it
# (pid in cpucap.pid) to lift the cap for processes started afterwards. Log: cpucap.log.
# Processes already in some job are skipped: a process can never leave a job, and adding it to ours would nest our
# job inside its job, so the two caps would multiply (restarts on 2026-10-09 did that: 25% x 25% = 1 core). The
# job name is unique per start for the same reason (a job loses its name when its last handle closes).
param([int]$Percent = 25, [int]$Every = 15)
$ErrorActionPreference = 'Continue'
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Log = Join-Path $Here 'cpucap.log'
$Root = 'C:\Users\jeffr\Downloads\bb8'
$Scripts = 'pipeline.py|rank_incremental.py|followup.py|dlscan_all.py|dlscan2_all.py|prefilter.py|maint_queue.py|nob_screen.py|' +
           'watch_champ.py|scan.py|ngcps_queue.py|bign_probe.py|ligocki_runner.py|check.py|fol2.py|zf.py|mfx.py|follow2.py|' +
           'mf35|fol.py|screen.py|batch.py'
Add-Type -TypeDefinition @"
using System; using System.Runtime.InteropServices;
public static class CapJob {
  [StructLayout(LayoutKind.Sequential)] public struct CpuRate { public uint ControlFlags; public uint CpuRateValue; }
  [DllImport("kernel32.dll", CharSet=CharSet.Unicode)] public static extern IntPtr CreateJobObject(IntPtr a, string name);
  [DllImport("kernel32.dll")] public static extern bool SetInformationJobObject(IntPtr job, int cls, ref CpuRate info, int len);
  [DllImport("kernel32.dll")] public static extern bool AssignProcessToJobObject(IntPtr job, IntPtr proc);
  [DllImport("kernel32.dll")] public static extern IntPtr OpenProcess(int access, bool inherit, int pid);
  [DllImport("kernel32.dll")] public static extern bool CloseHandle(IntPtr h);
  public static int Create(string name, uint rate, out IntPtr job) {
    job = CreateJobObject(IntPtr.Zero, name);
    if (job == IntPtr.Zero) return Marshal.GetLastWin32Error();
    CpuRate r = new CpuRate(); r.ControlFlags = 1 | 4; r.CpuRateValue = rate;   // ENABLE | HARD_CAP; units of 1/100 %
    if (!SetInformationJobObject(job, 15, ref r, Marshal.SizeOf(r))) return Marshal.GetLastWin32Error();
    return 0;
  }
  [DllImport("kernel32.dll")] public static extern bool IsProcessInJob(IntPtr proc, IntPtr job, out bool result);
  // -1: already in a job (left alone: assigning it would NEST our job inside that one, and nested CPU caps multiply)
  public static int Assign(IntPtr job, int pid) {
    IntPtr h = OpenProcess(0x1101, false, pid);                                 // SET_QUOTA | TERMINATE | QUERY_LIMITED
    if (h == IntPtr.Zero) return Marshal.GetLastWin32Error();
    bool inJob;
    if (IsProcessInJob(h, IntPtr.Zero, out inJob) && inJob) { CloseHandle(h); return -1; }
    bool ok = AssignProcessToJobObject(job, h); int e = ok ? 0 : Marshal.GetLastWin32Error();
    CloseHandle(h); return e;
  }
}
"@
function Log($m) { "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $m" | Add-Content -Path $Log -Encoding utf8 }
$job = [IntPtr]::Zero
$err = [CapJob]::Create("bb8_cpucap_$(Get-Date -Format yyyyMMddHHmmss)", [uint32]($Percent * 100), [ref]$job)
if ($err -ne 0) { Log "FATAL: job object setup failed, error $err"; exit 1 }
$PID | Set-Content -Path (Join-Path $Here 'cpucap.pid') -Encoding ascii
Log "started: hard cap $Percent% of the machine, sweep every $Every s (pid $PID)"
$done = @{}
while ($true) {
  $all = Get-CimInstance Win32_Process -Property ProcessId, ParentProcessId, Name, ExecutablePath, CommandLine
  $sel = @{}
  foreach ($p in $all) {
    if ($p.ProcessId -eq $PID) { continue }
    $exe = "$($p.ExecutablePath)"; $cmd = "$($p.CommandLine)"
    if ($exe.StartsWith($Root, [StringComparison]::OrdinalIgnoreCase) -and $p.Name -notmatch '^(powershell|bash|sh|cmd|conhost)\.exe$') { $sel[$p.ProcessId] = $p.Name }
    elseif ($p.Name -eq 'coqc.exe') { $sel[$p.ProcessId] = $p.Name }
    elseif ($p.Name -match '^pythonw?\.exe$' -and ($cmd -match "($Scripts)" -or $cmd -match '(?i)\\bb8\\|/bb8/|\\\.claude\\jobs' -or
            $cmd -match '(?i)python[w0-9.]*(\.exe)?"?\s+(-\S+\s+)*"?[^\s:"]+\.py\b')) { $sel[$p.ProcessId] = $p.Name }   # relative-path scripts: launched from a project folder
  }
  $added = $true
  while ($added) {                                                              # descendants of selected processes
    $added = $false
    foreach ($p in $all) { if (-not $sel.ContainsKey($p.ProcessId) -and $sel.ContainsKey($p.ParentProcessId) -and $p.Name -ne 'conhost.exe') { $sel[$p.ProcessId] = $p.Name; $added = $true } }
  }
  foreach ($id in $sel.Keys) {
    if ($done.ContainsKey($id)) { continue }
    $e = [CapJob]::Assign($job, [int]$id)
    if ($e -eq 0) { $done[$id] = 1; Log "capped $id $($sel[$id])" }
    elseif ($e -eq -1) { $done[$id] = 1; Log "skipped $id $($sel[$id]) (already in a job)" }
    else { $done[$id] = 1; Log "could not cap $id $($sel[$id]) (error $e)" }
  }
  $live = @{}; foreach ($p in $all) { $live[$p.ProcessId] = 1 }
  foreach ($id in @($done.Keys)) { if (-not $live.ContainsKey($id)) { $done.Remove($id) } }
  Start-Sleep -Seconds $Every
}
