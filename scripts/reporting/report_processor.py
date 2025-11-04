"""
Report Processor - Process and analyze test execution results

This module provides functionality to process pytest JSON reports,
extract statistics, and prepare data for visualization.

Author: QA Automation Team
Date: 2025-10-29
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict


class ReportProcessor:
    """
    Process test execution results and extract meaningful insights.
    
    Features:
    - Parse pytest JSON reports
    - Extract test statistics
    - Group tests by category/marker
    - Calculate trends and metrics
    - Prepare data for dashboard visualization
    """
    
    def __init__(self, reports_dir: Path):
        """
        Initialize the report processor.
        
        Args:
            reports_dir: Root directory containing all reports
        """
        self.reports_dir = Path(reports_dir)
        self.runs_dir = self.reports_dir / "runs"
        self.json_dir = self.reports_dir / "json"
        
    def process_json_report(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process pytest JSON report and extract statistics.
        
        Args:
            json_data: Parsed JSON data from pytest-json-report
            
        Returns:
            Dictionary with processed results and statistics
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "total": 0,
            "pass_rate": 0.0,
            "duration": 0.0,
            "tests": [],
            "by_category": defaultdict(int),
            "by_marker": defaultdict(int),
            "failed_tests": [],
            "warnings": [],
        }
        
        # Extract summary statistics
        if "summary" in json_data:
            summary = json_data["summary"]
            results["passed"] = summary.get("passed", 0)
            results["failed"] = summary.get("failed", 0)
            results["skipped"] = summary.get("skipped", 0)
            results["errors"] = summary.get("error", 0)
            results["duration"] = summary.get("missed", 0)  # Duration in pytest-json-report
            
        elif "report" in json_data:
            # Alternative format
            report = json_data["report"]
            for test in report.get("tests", []):
                status = test.get("outcome", "unknown")
                results[f"{status}s"] = results.get(f"{status}s", 0) + 1
                
                # Extract test details
                test_info = {
                    "nodeid": test.get("nodeid", ""),
                    "status": status,
                    "duration": test.get("duration", 0),
                    "markers": test.get("markers", []),
                }
                results["tests"].append(test_info)
                
                # Track by markers
                for marker in test_info["markers"]:
                    marker_name = marker.get("name", "") if isinstance(marker, dict) else str(marker)
                    if marker_name:
                        results["by_marker"][marker_name] += 1
                
                # Track failures
                if status == "failed":
                    results["failed_tests"].append({
                        "nodeid": test_info["nodeid"],
                        "duration": test_info["duration"],
                        "error": test.get("call", {}).get("longrepr", ""),
                    })
        
        # Calculate totals and pass rate
        results["total"] = (
            results["passed"] + 
            results["failed"] + 
            results["skipped"] + 
            results["errors"]
        )
        
        if results["total"] > 0:
            results["pass_rate"] = (results["passed"] / results["total"]) * 100
        
        # Extract warnings
        if "warnings" in json_data:
            results["warnings"] = json_data["warnings"]
        
        return results
    
    def load_all_runs(self) -> List[Dict[str, Any]]:
        """
        Load all historical test runs.
        
        Returns:
            List of run metadata dictionaries
        """
        runs = []
        
        # Load from JSON directory
        if self.json_dir.exists():
            for json_file in sorted(self.json_dir.glob("run_*.json")):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        run_data = json.load(f)
                        runs.append(run_data)
                except Exception as e:
                    print(f"Warning: Failed to load {json_file}: {e}")
        
        # Sort by timestamp (newest first)
        runs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return runs
    
    def get_statistics(self, runs: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Calculate statistics across all runs.
        
        Args:
            runs: Optional list of runs (if None, loads all)
            
        Returns:
            Dictionary with aggregated statistics
        """
        if runs is None:
            runs = self.load_all_runs()
        
        if not runs:
            return {
                "total_runs": 0,
                "average_pass_rate": 0,
                "average_duration": 0,
                "trend": "unknown",
            }
        
        # Calculate averages
        pass_rates = [run.get("pass_rate", 0) for run in runs if "pass_rate" in run]
        durations = [run.get("duration", 0) for run in runs if "duration" in run]
        
        avg_pass_rate = sum(pass_rates) / len(pass_rates) if pass_rates else 0
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Calculate trend
        if len(pass_rates) >= 2:
            recent_avg = sum(pass_rates[:3]) / min(3, len(pass_rates))
            older_avg = sum(pass_rates[3:6]) / min(3, len(pass_rates) - 3) if len(pass_rates) > 3 else recent_avg
            
            if recent_avg > older_avg + 2:
                trend = "improving"
            elif recent_avg < older_avg - 2:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "unknown"
        
        return {
            "total_runs": len(runs),
            "average_pass_rate": avg_pass_rate,
            "average_duration": avg_duration,
            "latest_pass_rate": pass_rates[0] if pass_rates else 0,
            "trend": trend,
            "total_tests_run": sum(run.get("total", 0) for run in runs),
        }
    
    def group_by_category(self, runs: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group runs by test category/marker.
        
        Args:
            runs: List of run dictionaries
            
        Returns:
            Dictionary mapping category to list of runs
        """
        categories = defaultdict(list)
        
        for run in runs:
            # Extract category from run metadata or markers
            markers = run.get("by_marker", {})
            if markers:
                # Use the most common marker as category
                if markers:
                    top_marker = max(markers.items(), key=lambda x: x[1])[0]
                    categories[top_marker].append(run)
            else:
                categories["default"].append(run)
        
        return dict(categories)

