"""
Shared pytest configuration for the CausalLens test suite.
"""

from pathlib import Path
import sys

# Add src to Python's import path so the tests can import project modules without requiring CausalLens to be installed as a Python package.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = PROJECT_ROOT / "src"

if str(SOURCE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIRECTORY))