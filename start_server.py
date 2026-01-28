#!/usr/bin/env python3
"""
Script to build the Angular app and start the FastAPI server.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and check for errors."""
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str))
    if result.returncode != 0:
        print(f"Command failed with return code {result.returncode}")
        sys.exit(result.returncode)
    return result


def main():
    # Change to the ui directory
    ui_dir = Path(__file__).parent / "ui"
    
    print("Building Angular application...")
    
    # Install npm packages if node_modules doesn't exist
    if not (ui_dir / "node_modules").exists():
        print("Installing npm packages...")
        run_command(["npm", "install"], cwd=ui_dir)
    
    # Build the Angular app
    print("Building Angular app...")
    run_command(["npx", "ng", "build"], cwd=ui_dir)
    
    print("Angular build completed successfully")
    
    # Install Python dependencies
    print("Installing Python dependencies...")
    
    # Check if virtual environment exists, create if not
    venv_dir = Path(__file__).parent / "venv"
    if not venv_dir.exists():
        print("Creating virtual environment...")
        run_command([sys.executable, "-m", "venv", "venv"])
    
    # Determine the Python executable in the virtual environment
    if os.name == 'nt':  # Windows
        python_exe = str(venv_dir / "Scripts" / "python.exe")
    else:  # Unix/Linux/MacOS
        python_exe = str(venv_dir / "bin" / "python")
    
    # Install requirements
    run_command([python_exe, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Start the server
    print("Starting FastAPI server...")
    run_command([python_exe, "server.py"])


if __name__ == "__main__":
    main()