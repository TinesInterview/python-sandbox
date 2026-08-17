# Tines

This is our a sandbox repository, containing a sample backend React app and a Python backend, to ensure candidates can run our coding challenge solution without problems.

## Prerequisites

- [Node.js](https://nodejs.org) 20+ with [Yarn](https://yarnpkg.com) (npm also works)
- [Python](https://www.python.org/downloads/) 3.9+ — on Windows, tick **"Add python.exe to PATH"** in the installer

## Getting Started

First, install all dependencies:

```bash
t/setup
```

Then, run the react and python applications:

```bash
t/start
```

On **Windows**, run the `.cmd` versions from PowerShell or Command Prompt:

```powershell
t\setup.cmd
t\start.cmd
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.
Press `Ctrl+C` to stop both services.

## Troubleshooting

**Windows: "python was not found", or the Microsoft Store opens.** Windows ships a
placeholder `python`. Install the real one from [python.org](https://www.python.org/downloads/)
with "Add python.exe to PATH" ticked, open a new terminal, and if it still happens,
turn the placeholder off under *Settings > Apps > Advanced app settings > App execution aliases*.

**Windows: "Terminate batch job (Y/N)?" after `Ctrl+C`.** Expected; both servers
have already been stopped by then. Either answer is fine.

**"Port 3000/8000 is already in use".** An earlier run is still going. Find it with
`netstat -ano | findstr :3000` on Windows, or `lsof -i :3000` elsewhere.

**Linux/WSL: "The virtual environment has no interpreter in it".** Run
`sudo apt install python3-venv`.

**WSL: yarn or python not found, though installed on Windows.** WSL does not share
programs with Windows. Either install Node and Python inside WSL, or use `t\start.cmd`
from PowerShell instead.

Still stuck? Delete `backend/venv` and `node_modules`, then re-run `t/setup`.
