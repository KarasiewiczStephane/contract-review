"""Comparison module for contract diff and alignment."""

from src.comparison.aligner import ClauseAligner, ClauseAlignment
from src.comparison.diff_generator import ComparisonReport, DiffGenerator

__all__ = [
    "ClauseAligner",
    "ClauseAlignment",
    "ComparisonReport",
    "DiffGenerator",
]
