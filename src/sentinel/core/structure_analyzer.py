"""
Structure Analyzer
==================

Validates that automation run structure matches expected requirements
and compares against historical baselines.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Set
from collections import defaultdict

from src.sentinel.core.models import (
    RunContext,
    StructureRule,
    StructureViolation,
    SuiteRun,
    TestCaseRun,
    TestStatus,
    AnomalySeverity,
    AnomalyCategory
)


class StructureAnalyzer:
    """
    Analyzes and validates test run structure.
    
    Validates:
    - Required suites are present
    - Forbidden suites are absent
    - Test counts are within expected ranges
    - Required tags are present
    - Structure matches historical baseline
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize structure analyzer.
        
        Args:
            config: Configuration dictionary with structure rules
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Load structure rules from config
        self.structure_rules: Dict[str, StructureRule] = self._load_structure_rules()
        
        # Historical baselines (loaded from history store)
        self.baselines: Dict[str, Dict] = {}
    
    def _load_structure_rules(self) -> Dict[str, StructureRule]:
        """Load structure rules from configuration."""
        rules = {}
        
        config_rules = self.config.get("pipeline_structure_rules", {})
        for pipeline, rule_config in config_rules.items():
            rule = StructureRule(
                pipeline=pipeline,
                required_suites=rule_config.get("required_suites", []),
                forbidden_suites=rule_config.get("forbidden_suites", []),
                required_tags=rule_config.get("required_tags", []),
                expected_test_count={
                    "min": rule_config.get("expected_test_count", {}).get("min", 0),
                    "max": rule_config.get("expected_test_count", {}).get("max", 10000),
                },
                required_test_ids=rule_config.get("required_test_ids", [])
            )
            rules[pipeline] = rule
        
        # Default rules if none configured
        if not rules:
            rules = {
                "regression-nightly": StructureRule(
                    pipeline="regression-nightly",
                    required_suites=["smoke", "sanity", "regression"],
                    forbidden_suites=["load"],
                    required_tags=["@critical"],
                    expected_test_count={"min": 200, "max": 400}
                ),
                "smoke": StructureRule(
                    pipeline="smoke",
                    required_suites=["smoke"],
                    expected_test_count={"min": 20, "max": 80}
                ),
            }
        
        return rules
    
    def analyze_run_structure(self, context: RunContext) -> List[StructureViolation]:
        """
        Analyze run structure and detect violations.
        
        Args:
            context: RunContext to analyze
            
        Returns:
            List of StructureViolation objects
        """
        violations = []
        
        # Get structure rule for this pipeline
        rule = self.structure_rules.get(context.pipeline)
        if not rule:
            self.logger.warning(f"No structure rule found for pipeline: {context.pipeline}")
            return violations
        
        # Check required suites
        violations.extend(self._check_required_suites(context, rule))
        
        # Check forbidden suites
        violations.extend(self._check_forbidden_suites(context, rule))
        
        # Check test counts
        violations.extend(self._check_test_counts(context, rule))
        
        # Check required tags
        violations.extend(self._check_required_tags(context, rule))
        
        # Check required test IDs
        violations.extend(self._check_required_test_ids(context, rule))
        
        # Compare with baseline
        violations.extend(self._compare_with_baseline(context))
        
        return violations
    
    def _check_required_suites(
        self,
        context: RunContext,
        rule: StructureRule
    ) -> List[StructureViolation]:
        """Check that all required suites are present."""
        violations = []
        
        actual_suites = set(context.suites.keys())
        required_suites = set(rule.required_suites)
        missing_suites = required_suites - actual_suites
        
        for suite in missing_suites:
            violation = StructureViolation(
                violation_type="MISSING_SUITE",
                rule=rule,
                actual_value=list(actual_suites),
                expected_value=list(required_suites),
                description=f"Required suite '{suite}' is missing from run {context.run_id}",
                timestamp=datetime.now()
            )
            violations.append(violation)
            self.logger.warning(
                f"Structure violation: Missing required suite '{suite}' "
                f"in pipeline {context.pipeline}"
            )
        
        return violations
    
    def _check_forbidden_suites(
        self,
        context: RunContext,
        rule: StructureRule
    ) -> List[StructureViolation]:
        """Check that forbidden suites are not present."""
        violations = []
        
        actual_suites = set(context.suites.keys())
        forbidden_suites = set(rule.forbidden_suites)
        present_forbidden = forbidden_suites & actual_suites
        
        for suite in present_forbidden:
            violation = StructureViolation(
                violation_type="FORBIDDEN_SUITE",
                rule=rule,
                actual_value=list(actual_suites),
                expected_value=list(forbidden_suites),
                description=f"Forbidden suite '{suite}' is present in run {context.run_id}",
                timestamp=datetime.now()
            )
            violations.append(violation)
            self.logger.warning(
                f"Structure violation: Forbidden suite '{suite}' "
                f"found in pipeline {context.pipeline}"
            )
        
        return violations
    
    def _check_test_counts(
        self,
        context: RunContext,
        rule: StructureRule
    ) -> List[StructureViolation]:
        """Check that test counts are within expected ranges."""
        violations = []
        
        total_tests = context.total_tests()
        min_tests = rule.expected_test_count.get("min", 0)
        max_tests = rule.expected_test_count.get("max", 10000)
        
        if total_tests < min_tests:
            violation = StructureViolation(
                violation_type="TEST_COUNT_BELOW_MIN",
                rule=rule,
                actual_value=total_tests,
                expected_value=min_tests,
                description=(
                    f"Test count {total_tests} is below minimum {min_tests} "
                    f"for pipeline {context.pipeline}"
                ),
                timestamp=datetime.now()
            )
            violations.append(violation)
            self.logger.warning(
                f"Structure violation: Test count {total_tests} < minimum {min_tests}"
            )
        
        if total_tests > max_tests:
            violation = StructureViolation(
                violation_type="TEST_COUNT_ABOVE_MAX",
                rule=rule,
                actual_value=total_tests,
                expected_value=max_tests,
                description=(
                    f"Test count {total_tests} is above maximum {max_tests} "
                    f"for pipeline {context.pipeline}"
                ),
                timestamp=datetime.now()
            )
            violations.append(violation)
            self.logger.warning(
                f"Structure violation: Test count {total_tests} > maximum {max_tests}"
            )
        
        return violations
    
    def _check_required_tags(
        self,
        context: RunContext,
        rule: StructureRule
    ) -> List[StructureViolation]:
        """Check that tests with required tags are present."""
        violations = []
        
        if not rule.required_tags:
            return violations
        
        # Collect all tags from tests
        all_tags = set()
        for test in context.tests.values():
            all_tags.update(test.tags)
        
        required_tags = set(rule.required_tags)
        missing_tags = required_tags - all_tags
        
        for tag in missing_tags:
            violation = StructureViolation(
                violation_type="MISSING_REQUIRED_TAG",
                rule=rule,
                actual_value=list(all_tags),
                expected_value=list(required_tags),
                description=(
                    f"Required tag '{tag}' not found in any test "
                    f"for pipeline {context.pipeline}"
                ),
                timestamp=datetime.now()
            )
            violations.append(violation)
            self.logger.warning(
                f"Structure violation: Required tag '{tag}' missing"
            )
        
        return violations
    
    def _check_required_test_ids(
        self,
        context: RunContext,
        rule: StructureRule
    ) -> List[StructureViolation]:
        """Check that required test IDs are present."""
        violations = []
        
        if not rule.required_test_ids:
            return violations
        
        actual_test_ids = set(context.tests.keys())
        required_test_ids = set(rule.required_test_ids)
        missing_test_ids = required_test_ids - actual_test_ids
        
        for test_id in missing_test_ids:
            violation = StructureViolation(
                violation_type="MISSING_REQUIRED_TEST",
                rule=rule,
                actual_value=list(actual_test_ids),
                expected_value=list(required_test_ids),
                description=(
                    f"Required test ID '{test_id}' not found "
                    f"in pipeline {context.pipeline}"
                ),
                timestamp=datetime.now()
            )
            violations.append(violation)
            self.logger.warning(
                f"Structure violation: Required test ID '{test_id}' missing"
            )
        
        return violations
    
    def _compare_with_baseline(self, context: RunContext) -> List[StructureViolation]:
        """Compare run structure with historical baseline."""
        violations = []
        
        baseline_key = f"{context.pipeline}:{context.environment}"
        baseline = self.baselines.get(baseline_key)
        
        if not baseline:
            self.logger.debug(f"No baseline found for {baseline_key}")
            return violations
        
        # Compare suite counts
        baseline_suites = baseline.get("suites", {})
        actual_suites = {name: len(suite.test_ids) for name, suite in context.suites.items()}
        
        for suite_name, expected_count in baseline_suites.items():
            actual_count = actual_suites.get(suite_name, 0)
            if actual_count == 0 and expected_count > 0:
                violation = StructureViolation(
                    violation_type="BASELINE_SUITE_MISSING",
                    rule=StructureRule(pipeline=context.pipeline),
                    actual_value=actual_count,
                    expected_value=expected_count,
                    description=(
                        f"Suite '{suite_name}' missing compared to baseline "
                        f"(expected {expected_count} tests)"
                    ),
                    timestamp=datetime.now()
                )
                violations.append(violation)
        
        # Compare total test count (allow ±10% deviation)
        baseline_total = baseline.get("total_tests", 0)
        if baseline_total > 0:
            actual_total = context.total_tests()
            deviation_percent = abs(actual_total - baseline_total) / baseline_total * 100
            
            if deviation_percent > 10:
                violation = StructureViolation(
                    violation_type="BASELINE_TEST_COUNT_DEVIATION",
                    rule=StructureRule(pipeline=context.pipeline),
                    actual_value=actual_total,
                    expected_value=baseline_total,
                    description=(
                        f"Test count deviates {deviation_percent:.1f}% from baseline "
                        f"({actual_total} vs {baseline_total})"
                    ),
                    timestamp=datetime.now()
                )
                violations.append(violation)
        
        return violations
    
    def update_baseline(self, context: RunContext):
        """
        Update baseline from a completed run.
        
        Args:
            context: Completed RunContext
        """
        baseline_key = f"{context.pipeline}:{context.environment}"
        
        baseline = {
            "total_tests": context.total_tests(),
            "suites": {
                name: len(suite.test_ids)
                for name, suite in context.suites.items()
            },
            "avg_duration": context.duration_seconds(),
            "last_updated": datetime.now().isoformat()
        }
        
        self.baselines[baseline_key] = baseline
        self.logger.info(f"Updated baseline for {baseline_key}")
    
    def load_baseline_from_history(self, history_store):
        """
        Load baselines from history store.
        
        Args:
            history_store: RunHistoryStore instance
        """
        # This will be called by the main service to load baselines
        # Implementation depends on history store interface
        pass




