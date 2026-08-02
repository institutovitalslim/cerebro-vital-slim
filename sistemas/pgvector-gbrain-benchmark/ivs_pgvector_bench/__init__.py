"""Benchmark governado de pgvector versus o baseline operacional do GBrain."""

from .core import HashEmbedding, compute_metrics, decide

__all__ = ["HashEmbedding", "compute_metrics", "decide"]
