"""
DD Custom Metrics - A Python wrapper for Datadog custom metrics with decorator support.
"""

from .metrics import DatadogMetrics
from .decorators import (
    instrument_latency,
    instrument_counter,
    instrument_gauge,
    instrument_histogram,
)

__version__ = "0.1.0"
__all__ = [
    "DatadogMetrics",
    "instrument_latency",
    "instrument_counter",
    "instrument_gauge",
    "instrument_histogram",
]
