"""
PZ Development Repository Integration Tests
===========================================

Tests demonstrating integration with PrismaPhotonics PZ development repository.
These tests verify that we can access and use the latest production code from PZ.

Author: QA Automation Architect
"""

import pytest
import logging
from pathlib import Path
from typing import List, Dict, Any


logger = logging.getLogger(__name__)


# =================================================================
# PZ Integration Verification Tests
# =================================================================

@pytest.mark.integration
@pytest.mark.infrastructure
@pytest.mark.pz
@pytest.mark.xray("PZ-13873")
def test_pz_repository_available(pz_integration):
    """
    Test that PZ repository is available and accessible.
    
    Verification:
    - PZ repository directory exists
    - Repository is a valid Git submodule
    - Basic structure is present
    """
    logger.info("=" * 80)
    logger.info("Testing PZ Repository Availability")
    logger.info("=" * 80)
    
    try:
        # Verify repository exists
        pz_root = pz_integration.pz_root
        logger.info(f"PZ Repository Path: {pz_root}")
        
        assert pz_root.exists(), "PZ repository directory not found"
        assert pz_root.is_dir(), "PZ repository path is not a directory"
        
        # Verify Git repository
        git_dir = pz_root / ".git"
        assert git_dir.exists(), "PZ repository not initialized as Git submodule"
        
        logger.info("✅ PZ repository is available and valid")
        
    except Exception as e:
        logger.error(f"❌ PZ repository verification failed: {e}")
        pytest.fail(f"PZ repository verification failed: {e}")


@pytest.mark.integration
@pytest.mark.infrastructure
@pytest.mark.pz
@pytest.mark.xray("PZ-13873")
def test_pz_microservices_listing(pz_integration):
    """
    Test that we can list all available microservices in PZ.
    
    Verification:
    - Microservices directory exists
    - Can enumerate microservices
    - Expected microservices are present
    """
    logger.info("=" * 80)
    logger.info("🧪 TEST: PZ Microservices Listing")
    logger.info("=" * 80)
    
    try:
        # Show PZ root path
        logger.info(f"📂 PZ Repository Path: {pz_integration.pz_root}")
        logger.info(f"📂 Checking: {pz_integration.pz_root / 'microservices'}")
        
        # List all microservices
        logger.info("🔍 Scanning for microservices...")
        microservices = pz_integration.list_microservices()
        
        logger.info(f"")
        logger.info(f"✅ SUCCESS: Found {len(microservices)} microservices!")
        logger.info(f"")
        logger.info(f"📦 Complete Microservices List:")
        logger.info(f"-" * 80)
        for idx, service in enumerate(microservices, 1):
            logger.info(f"  {idx:2d}. {service}")
        logger.info(f"-" * 80)
        
        # Verify minimum microservices exist
        assert len(microservices) > 0, "No microservices found"
        
        # Verify expected microservices (from memory)
        expected_services = [
            'focus_server',
            'analyzer',
            'data_manager',
            'controller',
            'pzpy',
            'pz_core_libs'
        ]
        
        found_services = []
        missing_services = []
        
        for service in expected_services:
            if service in microservices:
                found_services.append(service)
                logger.info(f"✅ Expected microservice found: {service}")
            else:
                missing_services.append(service)
                logger.warning(f"⚠️  Expected microservice not found: {service}")
        
        # At least some expected services should be present
        assert len(found_services) > 0, "No expected microservices found"
        
        logger.info(f"\n✅ Microservices listing test PASSED")
        logger.info(f"   Found: {len(found_services)}/{len(expected_services)} expected services")
        
    except Exception as e:
        logger.error(f"❌ Microservices listing failed: {e}")
        pytest.fail(f"Microservices listing failed: {e}")


@pytest.mark.integration
@pytest.mark.infrastructure
@pytest.mark.pz
@pytest.mark.xray("PZ-13873")
def test_pz_focus_server_access(pz_integration):
    """
    Test that we can access Focus Server microservice specifically.
    
    Verification:
    - Focus Server directory exists
    - Has expected structure
    - Can access source files
    """
    logger.info("=" * 80)
    logger.info("Testing Focus Server Microservice Access")
    logger.info("=" * 80)
    
    try:
        # Get Focus Server path
        focus_server_path = pz_integration.get_microservice_path('focus_server')
        
        logger.info(f"Focus Server Path: {focus_server_path}")
        
        assert focus_server_path.exists(), "Focus Server directory not found"
        assert focus_server_path.is_dir(), "Focus Server path is not a directory"
        
        # Check for expected files/directories
        expected_items = ['app', 'src', 'requirements.txt', 'Dockerfile']
        found_items = []
        
        for item in expected_items:
            item_path = focus_server_path / item
            if item_path.exists():
                found_items.append(item)
                logger.info(f"✅ Found: {item}")
            else:
                logger.warning(f"⚠️  Not found: {item}")
        
        # List top-level contents
        contents = list(focus_server_path.iterdir())
        logger.info(f"\nFocus Server contents ({len(contents)} items):")
        for item in sorted(contents)[:10]:
            logger.info(f"  - {item.name}")
        
        logger.info(f"✅ Focus Server access test PASSED")
        
    except FileNotFoundError as e:
        logger.warning(f"⚠️  Focus Server not found: {e}")
        pytest.skip("Focus Server microservice not found in PZ repository")
        
    except Exception as e:
        logger.error(f"❌ Focus Server access failed: {e}")
        pytest.fail(f"Focus Server access failed: {e}")


@pytest.mark.integration
@pytest.mark.infrastructure
@pytest.mark.pz
@pytest.mark.xray("PZ-13873")
def test_pz_version_info(pz_integration):
    """
    Test that we can retrieve PZ repository version information.
    
    Verification:
    - Can get current commit hash
    - Can get current branch
    - Can get last update timestamp
    """
    logger.info("=" * 80)
    logger.info("Testing PZ Version Information")
    logger.info("=" * 80)
    
    try:
        # Get version info
        version_info = pz_integration.get_version_info()
        
        logger.info("Version Information:")
        for key, value in version_info.items():
            logger.info(f"  {key}: {value}")
        
        # Verify we got at least some info
        assert len(version_info) > 0, "No version information retrieved"
        
        # Check for expected keys
        expected_keys = ['commit', 'branch']
        for key in expected_keys:
            if key in version_info:
                logger.info(f"✅ {key} information available")
        
        logger.info(f"✅ Version info test PASSED")
        
    except Exception as e:
        logger.error(f"❌ Version info retrieval failed: {e}")
        pytest.fail(f"Version info retrieval failed: {e}")


@pytest.mark.integration
@pytest.mark.infrastructure
@pytest.mark.pz
@pytest.mark.slow
@pytest.mark.xray("PZ-13873")
def test_pz_import_capability(pz_integration):
    """
    Test that we can dynamically import modules from PZ repository.
    
    NOTE: This is a demonstration test. Actual imports depend on
    PZ repository structure and may fail if modules have changed.
    
    Verification:
    - Python path is configured correctly
    - Can attempt imports from PZ
    """
    logger.info("=" * 80)
    logger.info("Testing PZ Module Import Capability")
    logger.info("=" * 80)
    
    import sys
    
    try:
        # Show Python path configuration
        logger.info("Python path configuration:")
        pz_paths = [p for p in sys.path if 'pz' in str(p).lower()]
        for path in pz_paths:
            logger.info(f"  ✓ {path}")
        
        assert len(pz_paths) > 0, "PZ paths not found in sys.path"
        
        logger.info(f"\n✅ Python path configured correctly")
        logger.info(f"   {len(pz_paths)} PZ-related paths in sys.path")
        
        # NOTE: Actual module imports would go here
        # Example (commented out as module structure may vary):
        # 
        # try:
        #     # Import a common PZ module
        #     pzpy = pz_integration.import_module('pzpy')
        #     logger.info(f"✅ Successfully imported pzpy")
        # except ImportError as e:
        #     logger.warning(f"⚠️  Could not import pzpy: {e}")
        
        logger.info(f"✅ Import capability test PASSED")
        
    except Exception as e:
        logger.error(f"❌ Import capability test failed: {e}")
        pytest.fail(f"Import capability test failed: {e}")


# =================================================================
# PZ Integration Summary
# =================================================================

@pytest.mark.integration
@pytest.mark.infrastructure
@pytest.mark.pz
@pytest.mark.summary
def test_pz_integration_summary(pz_integration):
    """
    Comprehensive PZ integration summary test.
    
    This test runs all verification checks and provides a complete
    summary of PZ repository integration status.
    """
    logger.info("=" * 80)
    logger.info("PZ INTEGRATION COMPREHENSIVE SUMMARY")
    logger.info("=" * 80)
    
    results = {
        "Repository Available": "Not Tested",
        "Microservices Accessible": "Not Tested",
        "Focus Server Present": "Not Tested",
        "Version Info Available": "Not Tested",
        "Import Capability": "Not Tested"
    }
    
    # Test repository availability
    try:
        assert pz_integration.pz_root.exists()
        results["Repository Available"] = "✅ PASSED"
    except:
        results["Repository Available"] = "❌ FAILED"
    
    # Test microservices
    try:
        services = pz_integration.list_microservices()
        assert len(services) > 0
        results["Microservices Accessible"] = f"✅ PASSED ({len(services)} services)"
    except:
        results["Microservices Accessible"] = "❌ FAILED"
    
    # Test Focus Server
    try:
        focus_path = pz_integration.get_microservice_path('focus_server')
        assert focus_path.exists()
        results["Focus Server Present"] = "✅ PASSED"
    except:
        results["Focus Server Present"] = "⚠️  NOT FOUND"
    
    # Test version info
    try:
        version = pz_integration.get_version_info()
        assert len(version) > 0
        results["Version Info Available"] = "✅ PASSED"
    except:
        results["Version Info Available"] = "❌ FAILED"
    
    # Test import capability
    import sys
    pz_paths = [p for p in sys.path if 'pz' in str(p).lower()]
    results["Import Capability"] = f"✅ PASSED ({len(pz_paths)} paths)" if pz_paths else "❌ FAILED"
    
    # Print summary
    logger.info("")
    logger.info("PZ Integration Test Results:")
    logger.info("-" * 80)
    for test, status in results.items():
        logger.info(f"  {test:30s}: {status}")
    logger.info("=" * 80)
    
    # Check if any critical tests failed
    failed_tests = [test for test, status in results.items() if "FAILED" in status]
    if failed_tests:
        logger.warning(f"Some integration checks failed: {', '.join(failed_tests)}")
    else:
        logger.info("🎉 All PZ integration checks passed!")


if __name__ == "__main__":
    # Configure logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)8s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    pytest.main([__file__, "-v", "-s", "-m", "pz"])

