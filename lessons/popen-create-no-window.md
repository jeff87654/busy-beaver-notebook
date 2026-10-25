---
name: popen-create-no-window
description: "Agent-launched exes pop a visible console window on the user's screen unless Popen uses CREATE_NO_WINDOW (0x08000000); put it in every agent brief"
metadata:
  type: feedback
---
2026-10-24: twoslot8's pkf8t.exe runs opened a new Windows Terminal/OpenConsole window per process on the user's
screen ("a lot of tabs keep opening"). Cause: subprocess.Popen from a console-less parent; DETACHED_PROCESS (0x08)
does not help. Fix: creationflags = 0x08000000 (CREATE_NO_WINDOW) | 0x40 (IDLE_PRIORITY_CLASS); never shell 'start',
os.startfile or PowerShell Start-Process for workers.
**Why:** the user works on the same desktop; popups are disruptive and closing a window kills the run.
**How to apply:** include the flag requirement in every agent brief that runs exes; grep new agent folders for
creationflags without 0x08000000. Related: [[kill-only-own-pids]], [[gpp-path-pitfall]].
