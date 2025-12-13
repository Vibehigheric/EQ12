"""
EdgeFinder - Core package initialization
Ethical repository reconnaissance tool for EQ12 system enhancement
"""

__version__ = "1.0.0"
__author__ = "EQ12 Development Team"
__license__ = "MIT"

from .cli import EdgeFinderCLI, main
from .config import Config
from .models import AnalysisResult, Candidate, SearchResult

__all__ = [
    "AnalysisResult",
    "Candidate",
    "Config",
    "EdgeFinderCLI",
    "SearchResult",
    "main",
]
