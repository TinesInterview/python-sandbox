# t/lib.py
#
# Shared helpers for t/setup.py and t/start.py. Standard library only: this
# runs before backend/venv exists.

import os
import shutil
import signal
import subprocess
import sys

IS_WINDOWS = os.name == "nt"

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(REPO_ROOT, "backend")
VENV_DIR = os.path.join(BACKEND_DIR, "venv")
REQUIREMENTS = os.path.join(BACKEND_DIR, "requirements.txt")

# Windows consoles default to a code page that cannot encode emoji, which would
# turn a decorative print into a crash.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

SETUP_HINT = "t\\setup.cmd" if IS_WINDOWS else "t/setup"
START_HINT = "t\\start.cmd" if IS_WINDOWS else "t/start"


def log(message):
    print(message)
    # Both servers write to this same console; staying unbuffered keeps our
    # lines in order relative to theirs.
    sys.stdout.flush()


def die(message, *hints):
    # .format() rather than f-strings so that a stray Python 2 still reaches
    # check_version() below and prints something readable.
    print("\n❌ {0}".format(message), file=sys.stderr)
    for hint in hints:
        print("   " + hint, file=sys.stderr)
    sys.exit(1)


def check_version():
    if sys.version_info < (3, 9):
        die(
            "Python 3.9+ is required, but this is Python {0}.".format(
                sys.version.split()[0]
            ),
            "Install a newer Python from https://python.org/downloads",
        )


def venv_python(required=False):
    """The interpreter inside backend/venv, or None.

    Calling it directly is equivalent to activating the venv, which is how both
    scripts avoid needing a shell-specific `activate`. Windows puts it in
    Scripts/, everyone else in bin/.
    """
    parts = ("Scripts", "python.exe") if IS_WINDOWS else ("bin", "python")
    path = os.path.join(VENV_DIR, *parts)
    if os.path.isfile(path):
        return path
    if required:
        die("No Python virtual environment found.", "Run " + SETUP_HINT + " first.")
    return None


def package_manager():
    """(name, path) of yarn, falling back to npm.

    Yarn is what we document, but plenty of Windows installs only ship npm and
    both lockfiles are committed, so npm is a fine second choice.
    """
    for name in ("yarn", "npm"):
        # On Windows these are .cmd shims. We need the real path because we
        # spawn without a shell, which keeps paths with spaces working.
        path = shutil.which(name + ".cmd") if IS_WINDOWS else None
        path = path or shutil.which(name)
        if path:
            return name, path

    die(
        "Could not find yarn or npm on your PATH.",
        "Install Node.js 20+ from https://nodejs.org (npm is included).",
    )


def run(argv, cwd=None):
    """Run a command to completion, exiting if it fails."""
    if subprocess.call(argv, cwd=cwd or REPO_ROOT) != 0:
        die("`{0}` failed.".format(" ".join(argv)))


def spawn(argv, cwd=None):
    """Start a server.

    On POSIX the child gets its own session, so Ctrl+C comes to us alone and we
    can shut the two servers down in a defined order. Windows has no equivalent
    - every process on the console gets Ctrl+C at once - so there we just let
    that happen and have stop() clean up whatever is left.
    """
    kwargs = {} if IS_WINDOWS else {"start_new_session": True}
    return subprocess.Popen(argv, cwd=cwd or REPO_ROOT, **kwargs)


def stop(process):
    """Terminate a server and its descendants.

    Both servers spawn workers of their own (uvicorn's reloader, Next's
    compiler), so killing only the direct child leaves orphans holding ports
    8000 and 3000 - the classic "port already in use" on the next run.
    """
    if process is None or process.poll() is not None:
        return

    if IS_WINDOWS:
        # No process groups to kill; /T walks the child tree instead.
        subprocess.call(
            ["taskkill", "/pid", str(process.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        except OSError:
            process.terminate()

    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()


_interrupted = []


def interrupted():
    """True once Ctrl+C (or a SIGTERM) has been seen."""
    return bool(_interrupted)


def handle_signals():
    """Make Ctrl+C and `kill` both raise KeyboardInterrupt.

    Setting this explicitly matters: a process started in the background
    inherits SIGINT ignored, and in that case Python installs no handler at
    all - leaving a script that Ctrl+C cannot stop with two servers under it.
    """
    def interrupt(_signum, _frame):
        # Recorded as well as raised, because on Windows the servers get Ctrl+C
        # at the same time we do, and the caller needs to distinguish "shutting
        # down" from "a server crashed". A list because .append is atomic and
        # this runs in a signal handler.
        _interrupted.append(True)
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, interrupt)
    signal.signal(signal.SIGTERM, interrupt)


def ignore_signals():
    """Stop reacting to Ctrl+C, so cleanup cannot itself be interrupted."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
