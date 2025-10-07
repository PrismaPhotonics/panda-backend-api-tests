"""
PZ Development Repository Integration
======================================

This module provides seamless integration with the PrismaPhotonics PZ development
repository, enabling automated tests to access the latest production code.

Features:
- Automatic PYTHONPATH configuration
- Dynamic import helpers
- Version synchronization utilities
- Microservices access layer

Author: QA Automation Architect
"""

import sys
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging


logger = logging.getLogger(__name__)


class PZIntegration:
    """
    Main integration class for accessing PZ development code.
    
    This class provides utilities for importing and using code from the PZ
    repository submodule.
    
    Time Complexity: O(1) for most operations
    Space Complexity: O(1)
    """
    
    def __init__(self, pz_root: Optional[Path] = None):
        """
        Initialize PZ integration.
        
        Args:
            pz_root: Optional path to PZ repository root.
                    If not provided, will auto-detect from project structure.
        """
        self.pz_root = pz_root or self._detect_pz_root()
        self._setup_python_path()
        
    def _detect_pz_root(self) -> Path:
        """
        Auto-detect PZ repository root from project structure.
        
        Returns:
            Path to PZ repository root
            
        Raises:
            FileNotFoundError: If PZ repository not found
        """
        # Try to find PZ repository relative to this file
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent
        pz_path = project_root / "external" / "pz"
        
        if not pz_path.exists():
            raise FileNotFoundError(
                f"PZ repository not found at {pz_path}. "
                "Please run 'git submodule update --init --recursive'"
            )
        
        logger.info(f"✅ PZ repository detected at: {pz_path}")
        return pz_path
    
    def _setup_python_path(self) -> None:
        """
        Add PZ repository to Python path for imports.
        
        This method adds the PZ microservices directory to sys.path,
        enabling direct imports of PZ modules.
        """
        pz_str = str(self.pz_root)
        microservices_path = self.pz_root / "microservices"
        microservices_str = str(microservices_path)
        
        # Add both root and microservices to path
        for path in [pz_str, microservices_str]:
            if path not in sys.path:
                sys.path.insert(0, path)
                logger.debug(f"Added to PYTHONPATH: {path}")
    
    def get_microservice_path(self, service_name: str) -> Path:
        """
        Get path to a specific microservice.
        
        Args:
            service_name: Name of the microservice (e.g., 'focus_server')
            
        Returns:
            Path to the microservice directory
            
        Raises:
            FileNotFoundError: If microservice not found
        """
        service_path = self.pz_root / "microservices" / service_name
        
        if not service_path.exists():
            raise FileNotFoundError(
                f"Microservice '{service_name}' not found at {service_path}"
            )
        
        return service_path
    
    def list_microservices(self) -> List[str]:
        """
        List all available microservices in PZ repository.
        
        Returns:
            List of microservice names
        """
        microservices_dir = self.pz_root / "microservices"
        
        if not microservices_dir.exists():
            return []
        
        # Return directories that look like microservices
        services = [
            d.name for d in microservices_dir.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        ]
        
        return sorted(services)
    
    def import_module(self, module_path: str) -> Any:
        """
        Dynamically import a module from PZ repository.
        
        Args:
            module_path: Module path (e.g., 'focus_server.api.endpoints')
            
        Returns:
            Imported module
            
        Raises:
            ImportError: If module cannot be imported
        """
        try:
            import importlib
            module = importlib.import_module(module_path)
            logger.info(f"✅ Successfully imported: {module_path}")
            return module
        except ImportError as e:
            logger.error(f"❌ Failed to import {module_path}: {e}")
            raise
    
    def get_version_info(self) -> Dict[str, str]:
        """
        Get PZ repository version information.
        
        Returns:
            Dictionary with version info (commit hash, branch, etc.)
        """
        import subprocess
        
        info = {}
        
        try:
            # Get current commit hash
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.pz_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                info["commit"] = result.stdout.strip()[:8]
            
            # Get current branch
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.pz_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                info["branch"] = result.stdout.strip()
            
            # Get last commit date
            result = subprocess.run(
                ["git", "log", "-1", "--format=%ci"],
                cwd=self.pz_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                info["last_update"] = result.stdout.strip()
                
        except Exception as e:
            logger.warning(f"Failed to get version info: {e}")
        
        return info
    
    def sync_latest(self) -> bool:
        """
        Sync PZ repository to latest version from remote.
        
        Returns:
            True if sync successful, False otherwise
        """
        import subprocess
        
        try:
            logger.info("🔄 Syncing PZ repository to latest version...")
            
            # Git submodule update
            result = subprocess.run(
                ["git", "submodule", "update", "--remote", "--merge", "external/pz"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info("✅ PZ repository synced successfully")
                return True
            else:
                logger.error(f"❌ Sync failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Sync failed with exception: {e}")
            return False


# Singleton instance for convenience
_pz_integration = None


def get_pz_integration() -> PZIntegration:
    """
    Get singleton instance of PZIntegration.
    
    Returns:
        PZIntegration instance
    """
    global _pz_integration
    
    if _pz_integration is None:
        _pz_integration = PZIntegration()
    
    return _pz_integration


# Convenience functions
def get_microservice_path(service_name: str) -> Path:
    """Get path to a microservice. Convenience wrapper."""
    return get_pz_integration().get_microservice_path(service_name)


def list_microservices() -> List[str]:
    """List all microservices. Convenience wrapper."""
    return get_pz_integration().list_microservices()


def import_pz_module(module_path: str) -> Any:
    """Import module from PZ. Convenience wrapper."""
    return get_pz_integration().import_module(module_path)


def sync_pz() -> bool:
    """Sync PZ to latest. Convenience wrapper."""
    return get_pz_integration().sync_latest()


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)8s] %(name)s: %(message)s'
    )
    
    # Initialize integration
    pz = PZIntegration()
    
    # Show version info
    print("\n" + "=" * 80)
    print("PZ Repository Integration")
    print("=" * 80)
    
    version_info = pz.get_version_info()
    if version_info:
        print(f"\n📌 Version Information:")
        for key, value in version_info.items():
            print(f"  {key}: {value}")
    
    # List microservices
    print(f"\n📦 Available Microservices ({len(pz.list_microservices())}):")
    for service in pz.list_microservices()[:10]:
        print(f"  - {service}")
    
    if len(pz.list_microservices()) > 10:
        print(f"  ... and {len(pz.list_microservices()) - 10} more")
    
    print("\n" + "=" * 80)

