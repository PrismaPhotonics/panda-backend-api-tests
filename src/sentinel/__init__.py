"""
Automation Run Sentinel
=======================

Autonomous monitoring and analysis service for automation runs on Kubernetes.

The Sentinel automatically detects, tracks, and analyzes automation runs,
detects anomalies, validates run structure, and sends alerts.
"""

__version__ = "1.0.0"

from src.sentinel.core.run_context import RunContext
from src.sentinel.core.run_detector import RunDetector
from src.sentinel.core.k8s_watcher import K8sWatcher
from src.sentinel.core.log_streamer import LogStreamer
from src.sentinel.core.structure_analyzer import StructureAnalyzer
from src.sentinel.core.anomaly_engine import AnomalyEngine
from src.sentinel.core.run_history_store import RunHistoryStore
from src.sentinel.core.alert_dispatcher import AlertDispatcher
from src.sentinel.main.sentinel_service import SentinelService

__all__ = [
    "RunContext",
    "RunDetector",
    "K8sWatcher",
    "LogStreamer",
    "StructureAnalyzer",
    "AnomalyEngine",
    "RunHistoryStore",
    "AlertDispatcher",
    "SentinelService",
]




