"""idle.py CMD ARGS... : run a command at Idle priority, inherit stdout/stderr, return its exit code."""
import subprocess, sys
sys.exit(subprocess.call(sys.argv[1:], creationflags=0x40))
