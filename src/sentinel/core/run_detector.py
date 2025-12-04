"""
Run Detector
============

Detects the start and end of automation runs from multiple sources:
- CI/CD webhooks (GitHub Actions, Jenkins, etc.)
- Kubernetes Job creation events
- Log pattern matching
"""

import logging
import re
from datetime import datetime
from typing import Dict, Optional, Callable, List
from dataclasses import dataclass

from src.sentinel.core.models import RunContext, RunStatus
from src.sentinel.core.run_context import RunContextManager


@dataclass
class RunDetectionRule:
    """Rule for detecting runs from logs."""
    pattern: str  # Regex pattern
    pipeline_extractor: Optional[str] = None  # Regex group name or pattern
    environment_extractor: Optional[str] = None
    run_id_extractor: Optional[str] = None


class RunDetector:
    """
    Detects automation run starts and ends from multiple sources.
    
    Supports:
    - CI webhook events
    - Kubernetes Job creation
    - Log pattern matching
    """
    
    def __init__(
        self,
        context_manager: RunContextManager,
        config: Optional[Dict] = None
    ):
        """
        Initialize the run detector.
        
        Args:
            context_manager: RunContextManager instance
            config: Configuration dictionary
        """
        self.context_manager = context_manager
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Detection rules from config
        self.log_rules: List[RunDetectionRule] = self._load_log_rules()
        
        # Callbacks for run start/end events
        self.on_run_start_callbacks: List[Callable[[RunContext], None]] = []
        self.on_run_end_callbacks: List[Callable[[RunContext], None]] = []
        
        # Track detected runs
        self._detected_runs: Dict[str, RunContext] = {}
    
    def _load_log_rules(self) -> List[RunDetectionRule]:
        """Load log detection rules from config."""
        rules = []
        config_rules = self.config.get("log_detection_rules", [])
        
        for rule_config in config_rules:
            rule = RunDetectionRule(
                pattern=rule_config.get("pattern", ""),
                pipeline_extractor=rule_config.get("pipeline_extractor"),
                environment_extractor=rule_config.get("environment_extractor"),
                run_id_extractor=rule_config.get("run_id_extractor")
            )
            rules.append(rule)
        
        # Default rules if none configured
        if not rules:
            rules = [
                RunDetectionRule(
                    pattern=r"RUN_START.*pipeline=(?P<pipeline>\w+).*env=(?P<env>\w+)",
                    pipeline_extractor="pipeline",
                    environment_extractor="env"
                ),
                RunDetectionRule(
                    pattern=r"TEST RUN STARTED.*run_id=(?P<run_id>\S+)",
                    run_id_extractor="run_id"
                ),
            ]
        
        return rules
    
    def register_run_start_callback(self, callback: Callable[[RunContext], None]):
        """Register a callback for run start events."""
        self.on_run_start_callbacks.append(callback)
    
    def register_run_end_callback(self, callback: Callable[[RunContext], None]):
        """Register a callback for run end events."""
        self.on_run_end_callbacks.append(callback)
    
    def detect_from_webhook(self, webhook_data: Dict) -> Optional[RunContext]:
        """
        Detect run start from CI/CD webhook.
        
        Args:
            webhook_data: Webhook payload
            
        Returns:
            Created RunContext if detected, None otherwise
        """
        try:
            # Extract metadata from webhook
            # Support GitHub Actions format
            if "workflow_run" in webhook_data:
                workflow = webhook_data["workflow_run"]
                run_id = str(workflow.get("id", ""))
                pipeline = workflow.get("name", "unknown")
                branch = workflow.get("head_branch", "")
                commit = workflow.get("head_sha", "")
                environment = self._extract_environment_from_webhook(webhook_data)
                triggered_by = workflow.get("triggering_actor", {}).get("login", "system")
                
                context = self.context_manager.create_context(
                    run_id=f"gh-{run_id}",
                    pipeline=pipeline,
                    environment=environment,
                    branch=branch,
                    commit=commit,
                    triggered_by=triggered_by,
                    ci_run_id=run_id,
                    ci_workflow_id=str(workflow.get("workflow_id", "")),
                )
                
                self._notify_run_start(context)
                return context
            
            # Support Jenkins format
            elif "build" in webhook_data:
                build = webhook_data["build"]
                run_id = str(build.get("number", ""))
                pipeline = build.get("fullDisplayName", "unknown")
                branch = build.get("branch", "")
                commit = build.get("commitId", "")
                environment = self._extract_environment_from_webhook(webhook_data)
                
                context = self.context_manager.create_context(
                    run_id=f"jenkins-{run_id}",
                    pipeline=pipeline,
                    environment=environment,
                    branch=branch,
                    commit=commit,
                    triggered_by=build.get("userId", "system"),
                    ci_run_id=run_id,
                    ci_job_id=str(build.get("id", "")),
                )
                
                self._notify_run_start(context)
                return context
            
            # Generic webhook format
            else:
                run_id = webhook_data.get("run_id") or webhook_data.get("id")
                if not run_id:
                    return None
                
                context = self.context_manager.create_context(
                    run_id=str(run_id),
                    pipeline=webhook_data.get("pipeline", "unknown"),
                    environment=webhook_data.get("environment", "unknown"),
                    branch=webhook_data.get("branch", ""),
                    commit=webhook_data.get("commit", ""),
                    triggered_by=webhook_data.get("triggered_by", "system"),
                    ci_run_id=str(run_id),
                )
                
                self._notify_run_start(context)
                return context
        
        except Exception as e:
            self.logger.error(f"Error detecting run from webhook: {e}", exc_info=True)
            return None
    
    def detect_from_k8s_job(
        self,
        job_name: str,
        namespace: str,
        labels: Dict[str, str],
        annotations: Dict[str, str]
    ) -> Optional[RunContext]:
        """
        Detect run start from Kubernetes Job creation.
        
        Args:
            job_name: Job name
            namespace: Kubernetes namespace
            labels: Job labels
            annotations: Job annotations
            
        Returns:
            Created RunContext if detected, None otherwise
        """
        try:
            # Check if this is an automation job
            job_type = labels.get("job-type") or labels.get("app.kubernetes.io/component")
            if job_type != "automation" and "test" not in job_name.lower():
                return None
            
            # Extract metadata from labels/annotations
            run_id = annotations.get("run-id") or labels.get("run-id") or job_name
            pipeline = labels.get("pipeline") or annotations.get("pipeline") or "unknown"
            environment = labels.get("environment") or annotations.get("environment") or namespace
            branch = labels.get("branch") or annotations.get("branch") or ""
            commit = labels.get("commit") or annotations.get("commit") or ""
            
            context = self.context_manager.create_context(
                run_id=str(run_id),
                pipeline=pipeline,
                environment=environment,
                branch=branch,
                commit=commit,
                triggered_by=annotations.get("triggered-by", "system"),
                k8s_job_name=job_name,
                k8s_namespace=namespace,
            )
            
            self._notify_run_start(context)
            return context
        
        except Exception as e:
            self.logger.error(f"Error detecting run from K8s job: {e}", exc_info=True)
            return None
    
    def detect_from_log(self, log_line: str, source: str = "unknown") -> Optional[RunContext]:
        """
        Detect run start from log line pattern matching.
        
        Args:
            log_line: Log line to analyze
            source: Source identifier (pod name, service name, etc.)
            
        Returns:
            Created RunContext if detected, None otherwise
        """
        try:
            for rule in self.log_rules:
                match = re.search(rule.pattern, log_line, re.IGNORECASE)
                if match:
                    # Extract values from match groups
                    pipeline = self._extract_value(match, rule.pipeline_extractor) or "unknown"
                    environment = self._extract_value(match, rule.environment_extractor) or "unknown"
                    run_id = self._extract_value(match, rule.run_id_extractor)
                    
                    if not run_id:
                        # Generate run ID if not found
                        run_id = f"log-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    
                    # Check if we already detected this run
                    if run_id in self._detected_runs:
                        return self._detected_runs[run_id]
                    
                    context = self.context_manager.create_context(
                        run_id=str(run_id),
                        pipeline=pipeline,
                        environment=environment,
                        branch="",
                        commit="",
                        triggered_by=source,
                    )
                    
                    self._detected_runs[run_id] = context
                    self._notify_run_start(context)
                    return context
        
        except Exception as e:
            self.logger.error(f"Error detecting run from log: {e}", exc_info=True)
        
        return None
    
    def detect_run_end(self, run_id: str, success: bool = True) -> bool:
        """
        Detect run end and mark context as completed.
        
        Args:
            run_id: Run ID
            success: Whether run succeeded
            
        Returns:
            True if run was found and marked, False otherwise
        """
        context = self.context_manager.get_context(run_id)
        if not context:
            self.logger.warning(f"Run context not found for end detection: {run_id}")
            return False
        
        self.context_manager.mark_completed(run_id, success=success)
        self._notify_run_end(context)
        return True
    
    def _extract_value(self, match: re.Match, extractor: Optional[str]) -> Optional[str]:
        """Extract value from regex match using extractor pattern."""
        if not extractor:
            return None
        
        # If extractor is a group name
        if extractor in match.groupdict():
            return match.group(extractor)
        
        # If extractor is a regex pattern, try to match it
        try:
            sub_match = re.search(extractor, match.group(0))
            if sub_match:
                return sub_match.group(1) if sub_match.groups() else sub_match.group(0)
        except Exception:
            pass
        
        return None
    
    def _extract_environment_from_webhook(self, webhook_data: Dict) -> str:
        """Extract environment from webhook data."""
        # Try multiple common fields
        env = (
            webhook_data.get("environment") or
            webhook_data.get("deployment", {}).get("environment") or
            webhook_data.get("workflow_run", {}).get("environment") or
            "unknown"
        )
        return str(env)
    
    def _notify_run_start(self, context: RunContext):
        """Notify all registered callbacks of run start."""
        self.logger.info(f"Run detected: {context.run_id} ({context.pipeline} on {context.environment})")
        for callback in self.on_run_start_callbacks:
            try:
                callback(context)
            except Exception as e:
                self.logger.error(f"Error in run start callback: {e}", exc_info=True)
    
    def _notify_run_end(self, context: RunContext):
        """Notify all registered callbacks of run end."""
        self.logger.info(f"Run ended: {context.run_id}")
        for callback in self.on_run_end_callbacks:
            try:
                callback(context)
            except Exception as e:
                self.logger.error(f"Error in run end callback: {e}", exc_info=True)




