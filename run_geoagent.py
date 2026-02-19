"""
Entry point for GEOAGENT
Run this from the project root: python run_geoagent.py
"""

import sys
from pathlib import Path

# Ensure we can import geospatial_agents
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from geospatial_agents.main import main

if __name__ == "__main__":
    main()
