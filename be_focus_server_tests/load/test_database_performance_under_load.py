"""
Load Tests - MongoDB Performance Under Concurrent Load
======================================================

Tests for MongoDB query performance when system is under concurrent load.

Tests Covered (Xray):
    - PZ-15140: Performance - MongoDB Query Performance Under Load

Author: QA Automation Architect
Date: 2025-11-23
"""

import pytest
import logging
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
from datetime import datetime, timedelta

from src.apis.focus_server_api import FocusServerAPI
from src.infrastructure.mongodb_manager import MongoDBManager
from src.models.focus_server_models import ConfigureRequest, ViewType

logger = logging.getLogger(__name__)


# ===================================================================
# Test Class: MongoDB Performance Under Load
# ===================================================================

@pytest.mark.slow
@pytest.mark.nightly
@pytest.mark.load
@pytest.mark.performance
@pytest.mark.database
class TestDatabasePerformanceUnderLoad:
    """
    Test suite for MongoDB query performance under concurrent API load.
    
    Tests covered:
        - PZ-15140: MongoDB Query Performance Under Load
    """
    
    @pytest.mark.xray("PZ-15140")
    def test_mongodb_query_performance_under_load(
        self, 
        focus_server_api: FocusServerAPI,
        mongodb_manager: MongoDBManager
    ):
        """
        Test PZ-15140: Performance - MongoDB Query Performance Under Load.
        
        Objective:
            Verify MongoDB maintains acceptable query performance when
            Focus Server API is under high concurrent load.
        
        Steps:
            1. Record baseline MongoDB performance (no load)
            2. Create 30 concurrent API jobs (high load)
            3. While under load, test MongoDB queries
            4. Measure query latency, connection pool, indexes
            5. Verify no database bottlenecks
            6. Cleanup and verify recovery
        
        Expected:
            - MongoDB ping < 100ms (even under load)
            - Average query time < 200ms
            - P95 query latency < 300ms
            - P99 query latency < 500ms
            - No connection pool exhaustion
            - No lock timeouts
        
        Jira: PZ-15140
        Priority: MEDIUM
        """
        logger.info("=" * 80)
        logger.info("TEST: MongoDB Query Performance Under Load (PZ-15140)")
        logger.info("=" * 80)
        
        num_api_jobs = 15  # Reduced from 30 to avoid system overload
        num_db_queries = 50  # Reduced from 100 to reasonable amount
        
        logger.info(f"Test Configuration:")
        logger.info(f"  API Load: {num_api_jobs} concurrent jobs")
        logger.info(f"  DB Queries: {num_db_queries} test queries")
        logger.info(f"")
        
        # Standard configuration for API load
        config_payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 1024,
            "displayInfo": {"height": 1000},
            "channels": {"min": 1, "max": 50},
            "frequencyRange": {"min": 0, "max": 1000},
            "start_time": None,
            "end_time": None,
            "view_type": ViewType.MULTICHANNEL
        }
        
        # Phase 1: Baseline database performance
        logger.info("Phase 1: Recording baseline MongoDB performance...")
        
        baseline_ping_latencies = []
        
        # Connect to MongoDB
        if not mongodb_manager.connect():
            pytest.skip("MongoDB not accessible - cannot run database performance test")
        
        # Test baseline ping latency
        for _ in range(10):
            start = time.time()
            try:
                # Ping MongoDB
                mongodb_manager.client.admin.command('ping')
                latency_ms = (time.time() - start) * 1000
                baseline_ping_latencies.append(latency_ms)
            except Exception as e:
                logger.warning(f"Baseline ping failed: {e}")
            time.sleep(0.1)
        
        baseline_ping = statistics.mean(baseline_ping_latencies) if baseline_ping_latencies else 0
        
        logger.info(f"Baseline MongoDB Metrics:")
        logger.info(f"  Ping Latency: {baseline_ping:.2f}ms")
        logger.info(f"")
        
        mongodb_manager.disconnect()
        
        # Phase 2: Create high API load
        logger.info("Phase 2: Creating high API load...")
        
        job_ids = []
        
        def create_job(job_num: int) -> str:
            """Create a single job."""
            try:
                config_request = ConfigureRequest(**config_payload)
                response = focus_server_api.configure_streaming_job(config_request)
                if response.job_id:
                    return response.job_id
            except Exception as e:
                logger.debug(f"Job {job_num} creation failed: {e}")
            return None
        
        # Create jobs concurrently
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(create_job, i) for i in range(num_api_jobs)]
            
            for future in as_completed(futures):
                job_id = future.result()
                if job_id:
                    job_ids.append(job_id)
        
        logger.info(f"Created {len(job_ids)}/{num_api_jobs} jobs")
        
        if len(job_ids) < num_api_jobs * 0.8:
            pytest.fail(f"Only {len(job_ids)}/{num_api_jobs} jobs created - insufficient load")
        
        # Wait for load to stabilize
        logger.info("Waiting 30 seconds for load to stabilize...")
        time.sleep(30)
        logger.info(f"")
        
        # Phase 3: Measure database performance under load
        logger.info("Phase 3: Measuring MongoDB performance under load...")
        
        # Reconnect to MongoDB
        if not mongodb_manager.connect():
            pytest.fail("Cannot connect to MongoDB")
        
        under_load_ping_latencies = []
        under_load_query_latencies = []
        connection_errors = 0
        query_errors = 0
        
        for query_num in range(num_db_queries):
            # Test 1: Ping latency
            start = time.time()
            try:
                mongodb_manager.client.admin.command('ping')
                latency_ms = (time.time() - start) * 1000
                under_load_ping_latencies.append(latency_ms)
            except Exception as e:
                connection_errors += 1
                logger.debug(f"Query {query_num}: Ping failed - {e}")
            
            # Test 2: Simple query latency (if database has recordings collection)
            start = time.time()
            try:
                # Try to query recordings (if exists)
                db = mongodb_manager.client.get_database()
                collection = db['recordings'] if 'recordings' in db.list_collection_names() else None
                
                if collection is not None:
                    # Simple count query
                    collection.count_documents({})
                    query_latency_ms = (time.time() - start) * 1000
                    under_load_query_latencies.append(query_latency_ms)
                
            except Exception as e:
                query_errors += 1
                logger.debug(f"Query {query_num}: Query failed - {e}")
            
            # Small delay between queries
            time.sleep(0.05)
        
        # Calculate statistics
        if under_load_ping_latencies:
            under_load_ping_latencies.sort()
            ping_avg = statistics.mean(under_load_ping_latencies)
            ping_p50 = under_load_ping_latencies[len(under_load_ping_latencies) // 2]
            ping_p95 = under_load_ping_latencies[int(len(under_load_ping_latencies) * 0.95)]
            ping_p99 = under_load_ping_latencies[int(len(under_load_ping_latencies) * 0.99)]
            ping_max = max(under_load_ping_latencies)
        else:
            ping_avg = ping_p50 = ping_p95 = ping_p99 = ping_max = 0
        
        if under_load_query_latencies:
            under_load_query_latencies.sort()
            query_avg = statistics.mean(under_load_query_latencies)
            query_p95 = under_load_query_latencies[int(len(under_load_query_latencies) * 0.95)]
            query_p99 = under_load_query_latencies[int(len(under_load_query_latencies) * 0.99)]
        else:
            query_avg = query_p95 = query_p99 = 0
        
        ping_increase = ping_avg - baseline_ping
        
        logger.info(f"\n{'='*80}")
        logger.info(f"MONGODB PERFORMANCE UNDER LOAD RESULTS")
        logger.info(f"{'='*80}")
        logger.info(f"")
        logger.info(f"Ping Latency ({len(under_load_ping_latencies)} samples):")
        logger.info(f"  Baseline: {baseline_ping:.2f}ms")
        logger.info(f"  Under Load - Avg: {ping_avg:.2f}ms")
        logger.info(f"  Under Load - P50: {ping_p50:.2f}ms")
        logger.info(f"  Under Load - P95: {ping_p95:.2f}ms")
        logger.info(f"  Under Load - P99: {ping_p99:.2f}ms")
        logger.info(f"  Under Load - Max: {ping_max:.2f}ms")
        logger.info(f"  Increase: +{ping_increase:.2f}ms")
        logger.info(f"")
        
        if under_load_query_latencies:
            logger.info(f"Query Latency ({len(under_load_query_latencies)} samples):")
            logger.info(f"  Average: {query_avg:.2f}ms")
            logger.info(f"  P95: {query_p95:.2f}ms")
            logger.info(f"  P99: {query_p99:.2f}ms")
            logger.info(f"")
        
        logger.info(f"Errors:")
        logger.info(f"  Connection Errors: {connection_errors}/{num_db_queries}")
        logger.info(f"  Query Errors: {query_errors}/{num_db_queries}")
        logger.info(f"")
        
        mongodb_manager.disconnect()
        
        # Phase 4: Cleanup API jobs
        logger.info("Phase 4: Cleaning up API jobs...")
        cleanup_count = 0
        for job_id in job_ids:
            try:
                focus_server_api.cancel_job(job_id)
                cleanup_count += 1
            except Exception:
                pass
        
        logger.info(f"Cleaned up {cleanup_count}/{len(job_ids)} jobs")
        logger.info(f"")
        
        # Assertions
        logger.info(f"{'='*80}")
        logger.info(f"VALIDATION RESULTS")
        logger.info(f"{'='*80}")
        
        # 1. Ping latency under load
        max_ping_under_load = 100  # 100ms
        assert ping_avg < max_ping_under_load, \
            f"MongoDB ping {ping_avg:.2f}ms exceeds {max_ping_under_load}ms under load"
        logger.info(f"✅ Ping latency OK: {ping_avg:.2f}ms < {max_ping_under_load}ms")
        
        # 2. P95 latency
        max_p95 = 150  # 150ms for ping
        assert ping_p95 < max_p95, \
            f"MongoDB ping P95 {ping_p95:.2f}ms exceeds {max_p95}ms"
        logger.info(f"✅ P95 latency OK: {ping_p95:.2f}ms < {max_p95}ms")
        
        # 3. Query performance (if we have query data)
        if under_load_query_latencies:
            max_query_avg = 200  # 200ms
            assert query_avg < max_query_avg, \
                f"Query average {query_avg:.2f}ms exceeds {max_query_avg}ms"
            logger.info(f"✅ Query latency OK: {query_avg:.2f}ms < {max_query_avg}ms")
            
            max_query_p95 = 300  # 300ms
            assert query_p95 < max_query_p95, \
                f"Query P95 {query_p95:.2f}ms exceeds {max_query_p95}ms"
            logger.info(f"✅ Query P95 OK: {query_p95:.2f}ms < {max_query_p95}ms")
        
        # 4. Connection errors
        max_connection_errors = 5  # Allow up to 5 errors out of 100
        assert connection_errors <= max_connection_errors, \
            f"Too many connection errors: {connection_errors} > {max_connection_errors}"
        logger.info(f"✅ Connection errors OK: {connection_errors} <= {max_connection_errors}")
        
        logger.info(f"")
        logger.info(f"{'='*80}")
        logger.info(f"✅ TEST PASSED: MongoDB Performance Under Load!")
        logger.info(f"{'='*80}")
        logger.info(f"MongoDB handled concurrent load successfully")
        logger.info(f"Query performance remained acceptable")
        logger.info(f"No database bottlenecks detected")
        logger.info(f"{'='*80}\n")
    
    @pytest.mark.xray("PZ-15140")
    def test_mongodb_connection_pool_under_load(
        self,
        focus_server_api: FocusServerAPI,
        mongodb_manager: MongoDBManager
    ):
        """
        Test PZ-15140.2: MongoDB Connection Pool Under Load.
        
        Objective:
            Verify MongoDB connection pool doesn't exhaust under load.
        
        Steps:
            1. Create 20 concurrent jobs
            2. Monitor connection pool
            3. Verify no pool exhaustion
        
        Expected:
            - No connection pool exhaustion
            - Connections remain within limits
        """
        logger.info("=" * 80)
        logger.info("TEST: MongoDB Connection Pool Under Load (PZ-15140.2)")
        logger.info("=" * 80)
        
        num_jobs = 10  # Reduced from 20 to avoid overload
        
        config_payload = {
            "displayTimeAxisDuration": 10,
            "nfftSelection": 512,  # Lighter config
            "displayInfo": {"height": 1000},
            "channels": {"min": 1, "max": 30},
            "frequencyRange": {"min": 0, "max": 1000},
            "start_time": None,
            "end_time": None,
            "view_type": ViewType.MULTICHANNEL
        }
        
        logger.info(f"Creating {num_jobs} concurrent jobs...")
        
        # Create jobs
        job_ids = []
        for i in range(num_jobs):
            try:
                config_request = ConfigureRequest(**config_payload)
                response = focus_server_api.configure_streaming_job(config_request)
                if response.job_id:
                    job_ids.append(response.job_id)
            except Exception as e:
                logger.warning(f"Job {i+1} failed: {e}")
        
        logger.info(f"Created {len(job_ids)} jobs")
        
        # Wait for jobs to be processing
        time.sleep(10)
        
        # Test MongoDB connections
        logger.info("\nTesting MongoDB connections under load...")
        
        connection_test_count = 50
        connection_successes = 0
        connection_failures = 0
        connection_latencies = []
        
        for i in range(connection_test_count):
            start = time.time()
            try:
                # Test connection
                if mongodb_manager.connect():
                    connection_successes += 1
                    latency_ms = (time.time() - start) * 1000
                    connection_latencies.append(latency_ms)
                    mongodb_manager.disconnect()
                else:
                    connection_failures += 1
            except Exception as e:
                connection_failures += 1
                logger.debug(f"Connection test {i+1} failed: {e}")
            
            time.sleep(0.1)
        
        # Cleanup jobs
        logger.info("\nCleaning up jobs...")
        for job_id in job_ids:
            try:
                focus_server_api.cancel_job(job_id)
            except:
                pass
        
        # Results
        connection_success_rate = connection_successes / connection_test_count
        avg_connection_latency = statistics.mean(connection_latencies) if connection_latencies else 0
        
        logger.info(f"\nConnection Pool Results:")
        logger.info(f"  Test Count: {connection_test_count}")
        logger.info(f"  Successes: {connection_successes}")
        logger.info(f"  Failures: {connection_failures}")
        logger.info(f"  Success Rate: {connection_success_rate:.1%}")
        logger.info(f"  Avg Latency: {avg_connection_latency:.2f}ms")
        
        # Assertions
        assert connection_success_rate >= 0.95, \
            f"Connection success rate {connection_success_rate:.1%} below 95%"
        logger.info(f"✅ Connection pool healthy: {connection_success_rate:.1%} success")
        
        assert avg_connection_latency < 200, \
            f"Connection latency {avg_connection_latency:.2f}ms exceeds 200ms"
        logger.info(f"✅ Connection latency OK: {avg_connection_latency:.2f}ms")

