"""
Run Context Management
======================

Manages RunContext objects and provides utilities for context operations.
"""

import logging
from datetime import datetime
from typing import Dict, Optional
from src.sentinel.core.models import RunContext, RunStatus


class RunContextManager:
    """
    Manages RunContext instances for active and completed runs.
    
    Provides thread-safe access to run contexts and maintains
    a registry of all runs.
    """
    
    def __init__(self):
        """Initialize the run context manager."""
        self.logger = logging.getLogger(__name__)
        self._contexts: Dict[str, RunContext] = {}
        self._lock = None  # Will be set to threading.Lock if needed
    
    def create_context(
        self,
        run_id: Optional[str] = None,
        pipeline: str = "",
        environment: str = "",
        branch: str = "",
        commit: str = "",
        triggered_by: str = "",
        **kwargs
    ) -> RunContext:
        """
        Create a new RunContext.
        
        Args:
            run_id: Optional run ID (generated if not provided)
            pipeline: Pipeline type (smoke, regression, etc.)
            environment: Environment name (staging, qa, etc.)
            branch: Git branch
            commit: Git commit hash
            triggered_by: User or schedule that triggered the run
            **kwargs: Additional context fields
            
        Returns:
            Created RunContext instance
        """
        context = RunContext(
            run_id=run_id or RunContext().run_id,
            pipeline=pipeline,
            environment=environment,
            branch=branch,
            commit=commit,
            triggered_by=triggered_by,
            start_time=datetime.now(),
            status=RunStatus.PENDING,
            **kwargs
        )
        
        self._contexts[context.run_id] = context
        self.logger.info(
            f"Created run context: {context.run_id} "
            f"(pipeline={pipeline}, env={environment})"
        )
        
        return context
    
    def get_context(self, run_id: str) -> Optional[RunContext]:
        """
        Get a RunContext by ID.
        
        Args:
            run_id: Run ID
            
        Returns:
            RunContext if found, None otherwise
        """
        return self._contexts.get(run_id)
    
    def update_context(self, run_id: str, **kwargs) -> bool:
        """
        Update a RunContext with new values.
        
        Args:
            run_id: Run ID
            **kwargs: Fields to update
            
        Returns:
            True if updated, False if context not found
        """
        context = self._contexts.get(run_id)
        if not context:
            self.logger.warning(f"Run context not found: {run_id}")
            return False
        
        for key, value in kwargs.items():
            if hasattr(context, key):
                setattr(context, key, value)
            else:
                self.logger.warning(f"Unknown context field: {key}")
        
        self.logger.debug(f"Updated run context: {run_id}")
        return True
    
    def mark_running(self, run_id: str) -> bool:
        """Mark a run as running."""
        return self.update_context(run_id, status=RunStatus.RUNNING)
    
    def mark_completed(self, run_id: str, success: bool = True) -> bool:
        """
        Mark a run as completed.
        
        Args:
            run_id: Run ID
            success: Whether the run succeeded
            
        Returns:
            True if updated, False if context not found
        """
        status = RunStatus.COMPLETED if success else RunStatus.FAILED
        context = self.get_context(run_id)
        if context:
            context.end_time = datetime.now()
            return self.update_context(run_id, status=status)
        return False
    
    def get_active_runs(self) -> Dict[str, RunContext]:
        """Get all currently active runs."""
        return {
            run_id: ctx
            for run_id, ctx in self._contexts.items()
            if ctx.is_active()
        }
    
    def get_all_contexts(self) -> Dict[str, RunContext]:
        """Get all run contexts."""
        return self._contexts.copy()
    
    def remove_context(self, run_id: str) -> bool:
        """
        Remove a run context (after archival).
        
        Args:
            run_id: Run ID
            
        Returns:
            True if removed, False if not found
        """
        if run_id in self._contexts:
            del self._contexts[run_id]
            self.logger.info(f"Removed run context: {run_id}")
            return True
        return False




