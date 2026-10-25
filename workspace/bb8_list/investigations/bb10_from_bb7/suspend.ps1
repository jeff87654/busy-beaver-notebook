# suspend.ps1 -Action suspend|resume -PidFile <file with one pid per line>
# Reversibly pauses (NtSuspendProcess) or resumes (NtResumeProcess) our own enumeration processes by PID.
param([string]$Action, [string]$PidFile)
Add-Type -TypeDefinition @"
using System; using System.Runtime.InteropServices;
public static class NtProc {
  [DllImport("ntdll.dll")] public static extern int NtSuspendProcess(IntPtr h);
  [DllImport("ntdll.dll")] public static extern int NtResumeProcess(IntPtr h);
  [DllImport("kernel32.dll")] public static extern IntPtr OpenProcess(int access, bool inherit, int pid);
  [DllImport("kernel32.dll")] public static extern bool CloseHandle(IntPtr h);
}
"@
foreach ($id in (Get-Content $PidFile | Where-Object { $_ -match '^\d+$' })) {
  $p = Get-Process -Id $id -ErrorAction SilentlyContinue
  if (-not $p) { "$id not running"; continue }
  $h = [NtProc]::OpenProcess(0x0800, $false, [int]$id)   # PROCESS_SUSPEND_RESUME
  if ($Action -eq 'suspend') { $r = [NtProc]::NtSuspendProcess($h) } else { $r = [NtProc]::NtResumeProcess($h) }
  [void][NtProc]::CloseHandle($h)
  "$Action $id ($($p.ProcessName)) status=$r"
}
