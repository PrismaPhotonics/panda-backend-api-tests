"""
Run History Store
=================

Persists and queries historical data about runs, tests, anomalies, and infrastructure context.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import asdict
import json

from src.sentinel.core.models import (
    RunContext,
    SuiteRun,
    TestCaseRun,
    Anomaly,
    InfraSnapshot
)


class RunHistoryStore:
    """
    Stores and retrieves historical run data.
    
    Supports:
    - Persisting run metadata
    - Querying runs by filters
    - Generating baselines and trends
    - Aggregating statistics
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize history store.
        
        Args:
            config: Configuration dictionary with database settings
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Database connection (will be initialized based on config)
        self.db_connection = None
        self._init_database()
    
    def _init_database(self):
        """Initialize database connection."""
        db_type = self.config.get("database", {}).get("type", "sqlite")
        
        if db_type == "postgresql":
            self._init_postgresql()
        elif db_type == "sqlite":
            self._init_sqlite()
        else:
            self.logger.warning(f"Unknown database type: {db_type}, using in-memory storage")
            self._init_memory()
    
    def _init_postgresql(self):
        """Initialize PostgreSQL connection."""
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            db_config = self.config.get("database", {})
            self.db_connection = psycopg2.connect(
                host=db_config.get("host", "localhost"),
                port=db_config.get("port", 5432),
                database=db_config.get("database", "sentinel"),
                user=db_config.get("user", "sentinel"),
                password=db_config.get("password", "")
            )
            self.db_connection.autocommit = True
            self.logger.info("PostgreSQL connection established")
            self._create_tables()
        
        except ImportError:
            self.logger.error("psycopg2 not installed, falling back to SQLite")
            self._init_sqlite()
        except Exception as e:
            self.logger.error(f"Failed to connect to PostgreSQL: {e}")
            self.logger.warning("Falling back to SQLite")
            self._init_sqlite()
    
    def _init_sqlite(self):
        """Initialize SQLite connection."""
        try:
            import sqlite3
            
            db_config = self.config.get("database", {})
            db_path = db_config.get("path", "sentinel_history.db")
            
            self.db_connection = sqlite3.connect(db_path, check_same_thread=False)
            self.db_connection.row_factory = sqlite3.Row
            self.logger.info(f"SQLite connection established: {db_path}")
            self._create_tables()
        
        except Exception as e:
            self.logger.error(f"Failed to initialize SQLite: {e}")
            self._init_memory()
    
    def _init_memory(self):
        """Initialize in-memory storage (fallback)."""
        self._memory_store: Dict[str, Any] = {}
        self.logger.warning("Using in-memory storage (data will be lost on restart)")
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        if not self.db_connection:
            return
        
        try:
            cursor = self.db_connection.cursor()
            
            # Runs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    pipeline TEXT NOT NULL,
                    environment TEXT NOT NULL,
                    branch TEXT,
                    commit TEXT,
                    triggered_by TEXT,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    status TEXT,
                    duration_seconds REAL,
                    total_tests INTEGER,
                    passed_tests INTEGER,
                    failed_tests INTEGER,
                    skipped_tests INTEGER,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Suites table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS suites (
                    suite_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    suite_name TEXT NOT NULL,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    duration_seconds REAL,
                    total_tests INTEGER,
                    passed_tests INTEGER,
                    failed_tests INTEGER,
                    skipped_tests INTEGER,
                    FOREIGN KEY (run_id) REFERENCES runs(run_id)
                )
            """)
            
            # Tests table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tests (
                    test_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    suite_name TEXT,
                    test_name TEXT NOT NULL,
                    status TEXT,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    duration_seconds REAL,
                    tags TEXT,
                    xray_id TEXT,
                    error_message TEXT,
                    FOREIGN KEY (run_id) REFERENCES runs(run_id)
                )
            """)
            
            # Anomalies table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS anomalies (
                    anomaly_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    timestamp TIMESTAMP,
                    severity TEXT,
                    category TEXT,
                    title TEXT,
                    description TEXT,
                    affected_component TEXT,
                    metadata TEXT,
                    FOREIGN KEY (run_id) REFERENCES runs(run_id)
                )
            """)
            
            # Infrastructure snapshots table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS infra_snapshots (
                    snapshot_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    timestamp TIMESTAMP,
                    pod_count INTEGER,
                    pod_restarts INTEGER,
                    pods_crash_loop INTEGER,
                    error_count INTEGER,
                    metrics TEXT,
                    FOREIGN KEY (run_id) REFERENCES runs(run_id)
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_runs_pipeline ON runs(pipeline)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_runs_environment ON runs(environment)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_runs_start_time ON runs(start_time)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tests_run_id ON tests(run_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_anomalies_run_id ON anomalies(run_id)")
            
            self.db_connection.commit()
            self.logger.info("Database tables created successfully")
        
        except Exception as e:
            self.logger.error(f"Error creating tables: {e}", exc_info=True)
    
    def save_run(self, context: RunContext):
        """
        Save a run context to the database.
        
        Args:
            context: RunContext to save
        """
        if not self.db_connection:
            # In-memory storage
            self._memory_store[context.run_id] = asdict(context)
            return
        
        try:
            cursor = self.db_connection.cursor()
            
            # Save run
            cursor.execute("""
                INSERT OR REPLACE INTO runs (
                    run_id, pipeline, environment, branch, commit, triggered_by,
                    start_time, end_time, status, duration_seconds,
                    total_tests, passed_tests, failed_tests, skipped_tests, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                context.run_id,
                context.pipeline,
                context.environment,
                context.branch,
                context.commit,
                context.triggered_by,
                context.start_time.isoformat() if context.start_time else None,
                context.end_time.isoformat() if context.end_time else None,
                context.status.value,
                context.duration_seconds(),
                context.total_tests(),
                context.passed_tests(),
                context.failed_tests(),
                sum(1 for t in context.tests.values() if t.status.value == "skipped"),
                json.dumps({
                    "ci_run_id": context.ci_run_id,
                    "ci_workflow_id": context.ci_workflow_id,
                    "k8s_job_name": context.k8s_job_name,
                    "k8s_namespace": context.k8s_namespace,
                })
            ))
            
            # Save suites
            for suite_name, suite in context.suites.items():
                suite_id = f"{context.run_id}:{suite_name}"
                cursor.execute("""
                    INSERT OR REPLACE INTO suites (
                        suite_id, run_id, suite_name, start_time, end_time,
                        duration_seconds, total_tests, passed_tests, failed_tests, skipped_tests
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    suite_id,
                    context.run_id,
                    suite.suite_name,
                    suite.start_time.isoformat() if suite.start_time else None,
                    suite.end_time.isoformat() if suite.end_time else None,
                    suite.duration_seconds(),
                    suite.total_tests,
                    suite.passed_tests,
                    suite.failed_tests,
                    suite.skipped_tests
                ))
            
            # Save tests
            for test_id, test in context.tests.items():
                cursor.execute("""
                    INSERT OR REPLACE INTO tests (
                        test_id, run_id, suite_name, test_name, status,
                        start_time, end_time, duration_seconds, tags, xray_id, error_message
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    test_id,
                    context.run_id,
                    test.suite_name,
                    test.test_name,
                    test.status.value,
                    test.start_time.isoformat() if test.start_time else None,
                    test.end_time.isoformat() if test.end_time else None,
                    test.duration_seconds(),
                    json.dumps(list(test.tags)),
                    test.xray_id,
                    test.error_message
                ))
            
            # Save anomalies
            for anomaly in context.anomalies:
                cursor.execute("""
                    INSERT OR REPLACE INTO anomalies (
                        anomaly_id, run_id, timestamp, severity, category,
                        title, description, affected_component, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    anomaly.anomaly_id,
                    context.run_id,
                    anomaly.timestamp.isoformat(),
                    anomaly.severity.value,
                    anomaly.category.value,
                    anomaly.title,
                    anomaly.description,
                    anomaly.affected_component,
                    json.dumps(anomaly.metadata)
                ))
            
            self.db_connection.commit()
            self.logger.info(f"Saved run {context.run_id} to history")
        
        except Exception as e:
            self.logger.error(f"Error saving run: {e}", exc_info=True)
    
    def get_run(self, run_id: str) -> Optional[Dict]:
        """
        Get a run by ID.
        
        Args:
            run_id: Run ID
            
        Returns:
            Run data dictionary or None
        """
        if not self.db_connection:
            return self._memory_store.get(run_id)
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
        
        except Exception as e:
            self.logger.error(f"Error getting run: {e}", exc_info=True)
            return None
    
    def query_runs(
        self,
        pipeline: Optional[str] = None,
        environment: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """
        Query runs with filters.
        
        Args:
            pipeline: Filter by pipeline
            environment: Filter by environment
            status: Filter by status
            limit: Maximum results
            offset: Offset for pagination
            
        Returns:
            List of run dictionaries
        """
        if not self.db_connection:
            # In-memory filtering
            runs = list(self._memory_store.values())
            if pipeline:
                runs = [r for r in runs if r.get("pipeline") == pipeline]
            if environment:
                runs = [r for r in runs if r.get("environment") == environment]
            if status:
                runs = [r for r in runs if r.get("status") == status]
            return runs[offset:offset+limit]
        
        try:
            cursor = self.db_connection.cursor()
            
            conditions = []
            params = []
            
            if pipeline:
                conditions.append("pipeline = ?")
                params.append(pipeline)
            if environment:
                conditions.append("environment = ?")
                params.append(environment)
            if status:
                conditions.append("status = ?")
                params.append(status)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            query = f"""
                SELECT * FROM runs
                WHERE {where_clause}
                ORDER BY start_time DESC
                LIMIT ? OFFSET ?
            """
            
            params.extend([limit, offset])
            cursor.execute(query, params)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        
        except Exception as e:
            self.logger.error(f"Error querying runs: {e}", exc_info=True)
            return []
    
    def get_baseline(
        self,
        pipeline: str,
        environment: str,
        days: int = 30
    ) -> Optional[Dict]:
        """
        Calculate baseline statistics for a pipeline/environment.
        
        Args:
            pipeline: Pipeline name
            environment: Environment name
            days: Number of days to look back
            
        Returns:
            Baseline dictionary with statistics
        """
        if not self.db_connection:
            return None
        
        try:
            cursor = self.db_connection.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Get recent runs
            cursor.execute("""
                SELECT 
                    AVG(duration_seconds) as avg_duration,
                    AVG(total_tests) as avg_total_tests,
                    AVG(passed_tests) as avg_passed_tests,
                    AVG(failed_tests) as avg_failed_tests,
                    COUNT(*) as run_count
                FROM runs
                WHERE pipeline = ? AND environment = ? AND start_time >= ?
            """, (pipeline, environment, cutoff_date))
            
            row = cursor.fetchone()
            if row and row[4] > 0:  # run_count > 0
                return {
                    "avg_duration": row[0],
                    "avg_total_tests": row[1],
                    "avg_passed_tests": row[2],
                    "avg_failed_tests": row[3],
                    "run_count": row[4],
                    "pipeline": pipeline,
                    "environment": environment
                }
            
            return None
        
        except Exception as e:
            self.logger.error(f"Error calculating baseline: {e}", exc_info=True)
            return None




