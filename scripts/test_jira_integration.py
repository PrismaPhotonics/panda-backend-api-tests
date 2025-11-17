"""
Test Jira Integration
=====================

This script tests the Jira bug deduplication and reporting mechanism.

Usage:
    python scripts/test_jira_integration.py
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Remove scripts/ from path to avoid conflict with jira library
# scripts/jira/ directory conflicts with the installed jira package
scripts_path = str(project_root / "scripts")
if scripts_path in sys.path:
    sys.path.remove(scripts_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_imports():
    """Test that all modules can be imported."""
    logger.info("Testing imports...")
    
    # First check if jira library is installed
    try:
        import importlib.util
        spec = importlib.util.find_spec("jira")
        if spec is None:
            logger.warning("⚠️  Jira library not installed - some tests will be skipped")
            logger.info("   Install with: pip install jira")
            return False
        # Check if it's from site-packages (not scripts/jira/)
        if spec.origin and 'site-packages' not in spec.origin and 'scripts' in spec.origin:
            logger.warning("⚠️  Jira library conflict detected - scripts/jira/ is being imported instead of installed package")
            logger.info("   This is a known issue. The code should still work when jira is installed.")
            return False
    except Exception as e:
        logger.warning(f"⚠️  Could not check jira library installation: {e}")
    
    try:
        from external.jira.bug_deduplication import BugDeduplicationService
        logger.info("✅ BugDeduplicationService imported successfully")
    except ImportError as e:
        if "Jira library not installed" in str(e):
            logger.warning(f"⚠️  Jira library not installed: {e}")
            logger.info("   Install with: pip install jira")
            return False
        logger.error(f"❌ Failed to import BugDeduplicationService: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to import BugDeduplicationService: {e}")
        return False
    
    try:
        from external.jira.bug_creator import BugCreatorService
        logger.info("✅ BugCreatorService imported successfully")
    except Exception as e:
        logger.error(f"❌ Failed to import BugCreatorService: {e}")
        return False
    
    try:
        from src.reporting.test_report_generator import TestReportGenerator, TestFailure
        logger.info("✅ TestReportGenerator imported successfully")
    except Exception as e:
        logger.error(f"❌ Failed to import TestReportGenerator: {e}")
        return False
    
    try:
        from src.reporting.pytest_integration import pytest_addoption, pytest_configure
        logger.info("✅ pytest_integration imported successfully")
    except Exception as e:
        logger.error(f"❌ Failed to import pytest_integration: {e}")
        return False
    
    return True


def test_service_initialization():
    """Test that services can be initialized."""
    logger.info("Testing service initialization...")
    
    try:
        from external.jira.bug_deduplication import BugDeduplicationService
        service = BugDeduplicationService()
        logger.info("✅ BugDeduplicationService initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize BugDeduplicationService: {e}")
        return False
    
    try:
        from external.jira.bug_creator import BugCreatorService
        service = BugCreatorService()
        logger.info("✅ BugCreatorService initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize BugCreatorService: {e}")
        return False
    
    try:
        from src.reporting.test_report_generator import TestReportGenerator
        generator = TestReportGenerator()
        logger.info("✅ TestReportGenerator initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize TestReportGenerator: {e}")
        return False
    
    return True


def test_report_generator():
    """Test report generator functionality."""
    logger.info("Testing report generator...")
    
    try:
        from src.reporting.test_report_generator import TestReportGenerator, TestFailure
        from datetime import datetime
        
        generator = TestReportGenerator()
        
        # Add some test results
        generator.add_passed("test_example.py::test_something")
        generator.add_skipped("test_example.py::test_skipped")
        
        generator.add_failure(
            test_name="test_example.py::test_failure",
            error_message="AssertionError: Expected 1, got 2",
            error_type="AssertionError"
        )
        
        logger.info(f"✅ Report generator: {len(generator.passed)} passed, "
                   f"{len(generator.failures)} failed, {len(generator.skipped)} skipped")
        
        # Test report generation (without Jira mapping)
        report = generator.generate_report()
        logger.info(f"✅ Report generated: {len(report)} keys")
        
        return True
    except Exception as e:
        logger.error(f"❌ Failed to test report generator: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pytest_integration():
    """Test pytest integration hooks."""
    logger.info("Testing pytest integration...")
    
    try:
        from src.reporting.pytest_integration import pytest_addoption
        
        # Create a mock parser
        class MockParser:
            def addoption(self, *args, **kwargs):
                pass
        
        parser = MockParser()
        pytest_addoption(parser)
        logger.info("✅ pytest_addoption hook works")
        
        return True
    except Exception as e:
        logger.error(f"❌ Failed to test pytest integration: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    logger.info("=" * 60)
    logger.info("Testing Jira Integration")
    logger.info("=" * 60)
    
    results = []
    
    # Test imports
    results.append(("Imports", test_imports()))
    
    # Test service initialization
    results.append(("Service Initialization", test_service_initialization()))
    
    # Test report generator
    results.append(("Report Generator", test_report_generator()))
    
    # Test pytest integration
    results.append(("Pytest Integration", test_pytest_integration()))
    
    # Summary
    logger.info("=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{name}: {status}")
        if not result:
            all_passed = False
    
    logger.info("=" * 60)
    if all_passed:
        logger.info("✅ All tests passed!")
        return 0
    else:
        logger.error("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())

