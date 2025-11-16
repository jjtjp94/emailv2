#!/usr/bin/env python
"""
Launcher script for Email Drafting Tool GUI.
Run this to start the desktop application.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ui.app import main

if __name__ == "__main__":
    sys.exit(main())
