#!/usr/bin/env python3
# t/start.py
#
# Runs the Python backend and the Next.js frontend together, shutting both down
# on Ctrl+C. Run via t/start or t\start.cmd.

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lib

lib.check_version()
lib.handle_signals()
lib.log("🚀 Starting services...")

python = lib.venv_python(required=True)
manager, executable = lib.package_manager()

backend = None
frontend = None
code = 0

try:
    lib.log("🐍 Starting Python backend on port 8000...")
    # `python -m uvicorn` rather than the bare `uvicorn` command: that console
    # script lives in the venv's bin/Scripts directory, which is not on PATH
    # unless the venv has been activated - and we deliberately never activate.
    backend = lib.spawn(
        [python, "-m", "uvicorn", "main:app", "--reload",
         "--host", "0.0.0.0", "--port", "8000"],
        cwd=lib.BACKEND_DIR,
    )

    time.sleep(1)  # let uvicorn's banner land before Next's

    lib.log("⚛️  Starting React frontend on port 3000...")
    dev = ["dev"] if manager == "yarn" else ["run", "dev"]
    frontend = lib.spawn([executable] + dev)

    lib.log("\n✅ Both running - open http://localhost:3000\n   Ctrl+C to stop.\n")

    # If either service falls over on its own, stop the other too: a
    # half-running sandbox is more confusing than a stopped one.
    while True:
        for name, process in (("backend", backend), ("frontend", frontend)):
            if process.poll() is not None:
                lib.log("\n🛑 The {0} stopped (exit code {1}).".format(
                    name, process.returncode))
                code = process.returncode or 1
                raise SystemExit
        time.sleep(0.4)

except (KeyboardInterrupt, SystemExit):
    pass

finally:
    # Ignore further interrupts: an impatient second Ctrl+C would otherwise
    # abort cleanup and orphan whichever server is still up.
    lib.ignore_signals()
    lib.log("\n🛑 Shutting down...")
    lib.stop(frontend)  # frontend first; it leaves the terminal tidier
    lib.stop(backend)

sys.exit(code)
