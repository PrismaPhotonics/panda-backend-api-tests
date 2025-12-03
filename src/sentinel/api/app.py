"""
Sentinel API Application
========================

Flask/FastAPI application providing REST endpoints for Sentinel.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

try:
    from flask import Flask, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

from src.sentinel.main.sentinel_service import SentinelService
from config.config_manager import ConfigManager


class SentinelAPI:
    """
    REST API for Automation Run Sentinel.
    
    Provides endpoints for:
    - Run queries
    - Webhook ingestion
    - Health checks
    - Statistics
    """
    
    def __init__(self, sentinel_service: SentinelService):
        """
        Initialize API.
        
        Args:
            sentinel_service: SentinelService instance
        """
        self.sentinel_service = sentinel_service
        self.logger = logging.getLogger(__name__)
        
        if FLASK_AVAILABLE:
            self.app = Flask(__name__)
            self._register_routes()
        else:
            self.logger.warning("Flask not available, API will not be functional")
            self.app = None
    
    def _register_routes(self):
        """Register API routes."""
        if not self.app:
            return
        
        # Health check
        self.app.route("/health", methods=["GET"])(self.health)
        self.app.route("/ready", methods=["GET"])(self.ready)
        
        # Run endpoints
        self.app.route("/api/runs", methods=["GET"])(self.list_runs)
        self.app.route("/api/runs/<run_id>", methods=["GET"])(self.get_run)
        self.app.route("/api/runs/<run_id>/anomalies", methods=["GET"])(self.get_run_anomalies)
        
        # Webhook endpoints
        self.app.route("/api/webhooks/github", methods=["POST"])(self.github_webhook)
        self.app.route("/api/webhooks/jenkins", methods=["POST"])(self.jenkins_webhook)
        self.app.route("/api/webhooks/generic", methods=["POST"])(self.generic_webhook)
        
        # Statistics
        self.app.route("/api/stats", methods=["GET"])(self.get_stats)
    
    def health(self):
        """Health check endpoint."""
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "automation-run-sentinel"
        })
    
    def ready(self):
        """Readiness check endpoint."""
        return jsonify({
            "status": "ready",
            "timestamp": datetime.now().isoformat()
        })
    
    def list_runs(self):
        """List runs with optional filters."""
        pipeline = request.args.get("pipeline")
        environment = request.args.get("environment")
        status = request.args.get("status")
        limit = int(request.args.get("limit", 100))
        offset = int(request.args.get("offset", 0))
        
        runs = self.sentinel_service.query_runs(
            pipeline=pipeline,
            environment=environment,
            status=status,
            limit=limit,
            offset=offset
        )
        
        return jsonify({
            "runs": runs,
            "count": len(runs)
        })
    
    def get_run(self, run_id: str):
        """Get a specific run."""
        context = self.sentinel_service.get_run(run_id)
        if not context:
            return jsonify({"error": "Run not found"}), 404
        
        # Convert to dict
        run_data = {
            "run_id": context.run_id,
            "pipeline": context.pipeline,
            "environment": context.environment,
            "branch": context.branch,
            "commit": context.commit,
            "status": context.status.value,
            "start_time": context.start_time.isoformat() if context.start_time else None,
            "end_time": context.end_time.isoformat() if context.end_time else None,
            "duration_seconds": context.duration_seconds(),
            "total_tests": context.total_tests(),
            "passed_tests": context.passed_tests(),
            "failed_tests": context.failed_tests(),
            "anomalies_count": len(context.anomalies),
            "suites": list(context.suites.keys())
        }
        
        return jsonify(run_data)
    
    def get_run_anomalies(self, run_id: str):
        """Get anomalies for a run."""
        context = self.sentinel_service.get_run(run_id)
        if not context:
            return jsonify({"error": "Run not found"}), 404
        
        anomalies = [
            {
                "anomaly_id": a.anomaly_id,
                "severity": a.severity.value,
                "category": a.category.value,
                "title": a.title,
                "description": a.description,
                "timestamp": a.timestamp.isoformat(),
                "affected_component": a.affected_component
            }
            for a in context.anomalies
        ]
        
        return jsonify({
            "run_id": run_id,
            "anomalies": anomalies,
            "count": len(anomalies)
        })
    
    def github_webhook(self):
        """Handle GitHub Actions webhook."""
        try:
            webhook_data = request.json
            context = self.sentinel_service.detect_run_from_webhook(webhook_data)
            
            if context:
                return jsonify({
                    "status": "detected",
                    "run_id": context.run_id
                }), 200
            else:
                return jsonify({
                    "status": "not_detected",
                    "message": "Run not detected from webhook data"
                }), 200
        
        except Exception as e:
            self.logger.error(f"Error processing GitHub webhook: {e}", exc_info=True)
            return jsonify({"error": str(e)}), 500
    
    def jenkins_webhook(self):
        """Handle Jenkins webhook."""
        try:
            webhook_data = request.json
            context = self.sentinel_service.detect_run_from_webhook(webhook_data)
            
            if context:
                return jsonify({
                    "status": "detected",
                    "run_id": context.run_id
                }), 200
            else:
                return jsonify({
                    "status": "not_detected",
                    "message": "Run not detected from webhook data"
                }), 200
        
        except Exception as e:
            self.logger.error(f"Error processing Jenkins webhook: {e}", exc_info=True)
            return jsonify({"error": str(e)}), 500
    
    def generic_webhook(self):
        """Handle generic webhook."""
        try:
            webhook_data = request.json
            context = self.sentinel_service.detect_run_from_webhook(webhook_data)
            
            if context:
                return jsonify({
                    "status": "detected",
                    "run_id": context.run_id
                }), 200
            else:
                return jsonify({
                    "status": "not_detected",
                    "message": "Run not detected from webhook data"
                }), 200
        
        except Exception as e:
            self.logger.error(f"Error processing generic webhook: {e}", exc_info=True)
            return jsonify({"error": str(e)}), 500
    
    def get_stats(self):
        """Get service statistics."""
        active_runs = self.sentinel_service.get_active_runs()
        
        return jsonify({
            "active_runs": len(active_runs),
            "timestamp": datetime.now().isoformat()
        })
    
    def run(self, host="0.0.0.0", port=5000, debug=False, threaded=False):
        """Run the API server."""
        if not self.app:
            raise RuntimeError("Flask not available, cannot run API server")
        
        self.app.run(host=host, port=port, debug=debug, threaded=threaded)


def create_api_app(config_manager: ConfigManager, config: Optional[Dict] = None):
    """
    Create and configure API application.
    
    Args:
        config_manager: ConfigManager instance
        config: Sentinel configuration
        
    Returns:
        Flask app instance
    """
    # Create sentinel service
    sentinel_service = SentinelService(config_manager, config)
    sentinel_service.start()
    
    # Create API
    api = SentinelAPI(sentinel_service)
    
    return api.app if api.app else None




