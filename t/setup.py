#!/usr/bin/env python3
# t/setup.py
#
# Installs frontend and backend dependencies. Run via t/setup or t\setup.cmd.

import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lib

lib.check_version()
lib.log("🚀 Setting up project...")

manager, executable = lib.package_manager()
lib.log("📦 Installing frontend dependencies with {0}...".format(manager))
lib.run([executable, "install"])

if os.path.isdir(lib.VENV_DIR):
    lib.log("🧹 Removing existing virtual environment...")
    shutil.rmtree(lib.VENV_DIR, ignore_errors=True)
    # Windows won't delete files held open by a running process, so a server
    # left running is the usual reason this fails.
    if os.path.isdir(lib.VENV_DIR):
        lib.die(
            "Could not remove " + lib.VENV_DIR,
            "Stop any running backend server and try again.",
        )

lib.log("🐍 Creating Python virtual environment...")
# sys.executable, so the venv matches the Python that passed the version check.
lib.run([sys.executable, "-m", "venv", lib.VENV_DIR])

python = lib.venv_python()
if python is None:
    lib.die(
        "The virtual environment has no interpreter in it.",
        "On Debian/Ubuntu, install it with: sudo apt install python3-venv",
    )

lib.log("📦 Installing backend dependencies...")
lib.run([python, "-m", "pip", "install", "--upgrade", "pip", "--quiet"])
lib.run([python, "-m", "pip", "install", "-r", lib.REQUIREMENTS])

lib.log("✅ Setup complete!\n\n   Next: " + lib.START_HINT + "\n")
