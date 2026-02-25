#!/usr/bin/env python3
"""CLI entrypoint: python scripts/run_pipeline.py [--playlists] [--all]"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.pipeline.runner import main

if __name__ == "__main__":
    main()
