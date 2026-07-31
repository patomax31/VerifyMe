#!/bin/bash
# Quick activation script for the face-recognition project on Linux

# Activate the Linux virtual environment
source venv_linux/bin/activate

echo "Virtual environment activated!"
echo "Python version: $(python --version)"
echo "Ready to run main.py, login.py, or registrar.py"
echo ""
echo "Commands:"
echo "  python main.py        - Launch the GUI application"
echo "  python login.py       - Run facial recognition login"
echo "  python registrar.py   - Register a new user"
echo "  python test_setup.py  - Verify all dependencies"
