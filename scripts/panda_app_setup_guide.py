#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Panda Application Setup and Configuration Helper
=================================================

This script helps diagnose and fix Panda Application installation issues,
and properly configure the usersettings.json file.

Author: QA Automation Architect
Date: 2025-10-16
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import Optional, List, Tuple
from datetime import datetime

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')


class PandaSetupHelper:
    """Helper class to diagnose and configure Panda Application"""
    
    # Common installation paths
    COMMON_INSTALL_PATHS = [
        r"C:\Program Files\Prisma\Panda",
        r"C:\Program Files (x86)\Prisma\Panda",
        r"C:\Panda",
        r"C:\Program Files\Panda",
        os.path.expanduser(r"~\AppData\Local\Panda"),
        os.path.expanduser(r"~\AppData\Roaming\Panda"),
    ]
    
    # Expected executable names
    EXPECTED_EXES = ["Panda.exe", "PandaApp.exe", "FocusClient.exe"]
    
    def __init__(self):
        self.installation_path: Optional[Path] = None
        self.exe_path: Optional[Path] = None
        self.config_path: Optional[Path] = None
        self.issues: List[str] = []
        self.warnings: List[str] = []
        
    def check_installation(self) -> bool:
        """
        Check if Panda application is installed and locate its path
        
        Returns:
            True if installation found, False otherwise
        """
        print("🔍 Scanning for Panda installation...")
        
        # Check common paths
        for path_str in self.COMMON_INSTALL_PATHS:
            path = Path(path_str)
            if path.exists():
                # Look for executable
                for exe_name in self.EXPECTED_EXES:
                    exe_path = path / exe_name
                    if exe_path.exists():
                        self.installation_path = path
                        self.exe_path = exe_path
                        print(f"✅ Found installation at: {self.installation_path}")
                        print(f"✅ Executable: {self.exe_path}")
                        return True
        
        # Installation not found
        self.issues.append("Panda application not found in common installation paths")
        print("❌ Panda application not found")
        return False
    
    def locate_config_file(self) -> bool:
        """
        Locate existing usersettings.json file
        
        Returns:
            True if config file found, False otherwise
        """
        if not self.installation_path:
            return False
            
        print("\n🔍 Scanning for usersettings.json...")
        
        # Check in installation directory
        config_path = self.installation_path / "usersettings.json"
        if config_path.exists():
            self.config_path = config_path
            print(f"✅ Found config at: {self.config_path}")
            return True
        
        # Check in AppData
        appdata_config = Path(os.path.expanduser(r"~\AppData\Roaming\Panda\usersettings.json"))
        if appdata_config.exists():
            self.config_path = appdata_config
            print(f"✅ Found config at: {self.config_path}")
            return True
        
        # Config file not found - this is OK, we'll create it
        print("⚠️  No existing usersettings.json found (will be created)")
        self.config_path = self.installation_path / "usersettings.json"
        return False
    
    def validate_config_json(self, config_path: Path) -> Tuple[bool, Optional[dict]]:
        """
        Validate that a JSON config file is valid
        
        Args:
            config_path: Path to the config file
            
        Returns:
            Tuple of (is_valid, config_dict)
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Validate required fields
            required_sections = ["Communication", "SavedData", "Defaults"]
            missing = [s for s in required_sections if s not in config]
            
            if missing:
                self.warnings.append(f"Config missing sections: {missing}")
                return False, config
            
            # Validate Communication section
            comm = config.get("Communication", {})
            required_comm = ["Backend", "Frontend", "SiteId"]
            missing_comm = [f for f in required_comm if f not in comm]
            
            if missing_comm:
                self.warnings.append(f"Communication section missing: {missing_comm}")
                return False, config
            
            print("✅ Config JSON is valid")
            return True, config
            
        except json.JSONDecodeError as e:
            self.issues.append(f"Invalid JSON in config: {e}")
            print(f"❌ Invalid JSON: {e}")
            return False, None
        except Exception as e:
            self.issues.append(f"Error reading config: {e}")
            print(f"❌ Error reading config: {e}")
            return False, None
    
    def backup_existing_config(self) -> bool:
        """
        Backup existing config file before replacement
        
        Returns:
            True if backup successful or no backup needed
        """
        if not self.config_path or not self.config_path.exists():
            print("ℹ️  No existing config to backup")
            return True
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.config_path.with_suffix(f".json.backup_{timestamp}")
        
        try:
            shutil.copy2(self.config_path, backup_path)
            print(f"✅ Backed up existing config to: {backup_path}")
            return True
        except Exception as e:
            self.warnings.append(f"Could not backup config: {e}")
            print(f"⚠️  Could not backup config: {e}")
            return False
    
    def install_clean_config(self, source_config: Path) -> bool:
        """
        Install the cleaned usersettings.json
        
        Args:
            source_config: Path to the cleaned config file
            
        Returns:
            True if installation successful
        """
        if not self.config_path:
            self.issues.append("Target config path not determined")
            return False
        
        if not source_config.exists():
            self.issues.append(f"Source config not found: {source_config}")
            return False
        
        # Validate source config
        valid, _ = self.validate_config_json(source_config)
        if not valid:
            self.issues.append("Source config is invalid")
            return False
        
        # Backup existing
        self.backup_existing_config()
        
        # Copy new config
        try:
            # Ensure target directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(source_config, self.config_path)
            print(f"✅ Installed clean config to: {self.config_path}")
            return True
        except Exception as e:
            self.issues.append(f"Failed to install config: {e}")
            print(f"❌ Failed to install config: {e}")
            return False
    
    def verify_network_endpoints(self, config_path: Path) -> List[Tuple[str, bool, str]]:
        """
        Verify that network endpoints in config are reachable
        
        Args:
            config_path: Path to config file
            
        Returns:
            List of (endpoint_name, is_reachable, message)
        """
        _, config = self.validate_config_json(config_path)
        if not config:
            return []
        
        results = []
        comm = config.get("Communication", {})
        
        endpoints = {
            "Backend": comm.get("Backend"),
            "Frontend": comm.get("Frontend"),
            "FrontendApi": comm.get("FrontendApi"),
        }
        
        print("\n🌐 Checking network connectivity...")
        
        for name, url in endpoints.items():
            if not url:
                results.append((name, False, "Not configured"))
                continue
            
            # Extract hostname from URL
            try:
                from urllib.parse import urlparse
                parsed = urlparse(url)
                host = parsed.hostname
                port = parsed.port or (443 if parsed.scheme == "https" else 80)
                
                # Try to connect (using Test-NetConnection on Windows)
                cmd = f'powershell -Command "Test-NetConnection -ComputerName {host} -Port {port} -WarningAction SilentlyContinue"'
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                
                # Check if connection succeeded
                if "TcpTestSucceeded : True" in result.stdout:
                    print(f"  ✅ {name}: {url} - Reachable")
                    results.append((name, True, "Reachable"))
                else:
                    print(f"  ❌ {name}: {url} - Not reachable")
                    results.append((name, False, "Not reachable"))
                    self.warnings.append(f"{name} endpoint not reachable: {url}")
                    
            except subprocess.TimeoutExpired:
                print(f"  ⏱️  {name}: {url} - Timeout")
                results.append((name, False, "Timeout"))
                self.warnings.append(f"{name} endpoint timeout: {url}")
            except Exception as e:
                print(f"  ⚠️  {name}: {url} - Error: {e}")
                results.append((name, False, str(e)))
        
        return results
    
    def check_saved_data_folder(self, config_path: Path) -> bool:
        """
        Check if SavedData folder exists and is writable
        
        Args:
            config_path: Path to config file
            
        Returns:
            True if folder is ready
        """
        _, config = self.validate_config_json(config_path)
        if not config:
            return False
        
        saved_data = config.get("SavedData", {})
        folder = saved_data.get("Folder")
        
        if not folder:
            self.warnings.append("SavedData.Folder not configured")
            return False
        
        folder_path = Path(folder)
        
        print(f"\n📁 Checking SavedData folder: {folder_path}")
        
        # Check if exists
        if not folder_path.exists():
            try:
                folder_path.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created SavedData folder: {folder_path}")
            except Exception as e:
                self.issues.append(f"Cannot create SavedData folder: {e}")
                print(f"❌ Cannot create SavedData folder: {e}")
                return False
        else:
            print(f"✅ SavedData folder exists")
        
        # Check if writable
        test_file = folder_path / ".write_test"
        try:
            test_file.write_text("test")
            test_file.unlink()
            print(f"✅ SavedData folder is writable")
            return True
        except Exception as e:
            self.issues.append(f"SavedData folder not writable: {e}")
            print(f"❌ SavedData folder not writable: {e}")
            return False
    
    def try_launch_app(self) -> Tuple[bool, str]:
        """
        Attempt to launch the Panda application
        
        Returns:
            Tuple of (success, message)
        """
        if not self.exe_path:
            return False, "No executable found"
        
        print(f"\n🚀 Attempting to launch: {self.exe_path}")
        
        try:
            # Launch as detached process
            subprocess.Popen(
                [str(self.exe_path)],
                cwd=str(self.installation_path),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
            )
            
            print("✅ Application launched successfully")
            print("   Check if window appears. If not, check logs for errors.")
            return True, "Launched"
            
        except Exception as e:
            msg = f"Failed to launch: {e}"
            self.issues.append(msg)
            print(f"❌ {msg}")
            return False, str(e)
    
    def generate_report(self) -> str:
        """
        Generate diagnostic report
        
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 70)
        report.append("Panda Application Setup & Diagnostic Report")
        report.append("=" * 70)
        report.append("")
        
        # Installation info
        report.append("📦 Installation")
        if self.installation_path:
            report.append(f"  ✅ Path: {self.installation_path}")
            report.append(f"  ✅ Executable: {self.exe_path}")
        else:
            report.append("  ❌ Not found")
        report.append("")
        
        # Config info
        report.append("⚙️  Configuration")
        if self.config_path:
            report.append(f"  ✅ Config: {self.config_path}")
        else:
            report.append("  ❌ No config file")
        report.append("")
        
        # Issues
        if self.issues:
            report.append("❌ Critical Issues:")
            for issue in self.issues:
                report.append(f"  • {issue}")
            report.append("")
        
        # Warnings
        if self.warnings:
            report.append("⚠️  Warnings:")
            for warning in self.warnings:
                report.append(f"  • {warning}")
            report.append("")
        
        if not self.issues and not self.warnings:
            report.append("✅ No issues detected!")
        
        report.append("=" * 70)
        
        return "\n".join(report)


def main():
    """Main execution flow"""
    
    print("=" * 70)
    print("Panda Application Setup Helper")
    print("=" * 70)
    print()
    
    helper = PandaSetupHelper()
    
    # Step 1: Check if installed
    if not helper.check_installation():
        print("\n" + "=" * 70)
        print("⚠️  INSTALLATION REQUIRED")
        print("=" * 70)
        print()
        print("The Panda application is not installed or not found.")
        print()
        print("Please install it first:")
        print(f'  1. Run the installer: PandaAppInstaller-1.2.41.exe')
        print(f'  2. Follow installation wizard')
        print(f'  3. Note the installation path')
        print(f'  4. Run this script again')
        print()
        return 1
    
    # Step 2: Locate or prepare config
    helper.locate_config_file()
    
    # Step 3: Ask user for cleaned config location
    print("\n" + "=" * 70)
    print("📋 Configuration Setup")
    print("=" * 70)
    
    # Default to the Downloads folder location
    default_source = Path(os.path.expanduser(r"~\Downloads\usersettings.cleaned.json"))
    
    if default_source.exists():
        print(f"\n✅ Found cleaned config: {default_source}")
        response = input("\nUse this config? (Y/n): ").strip().lower()
        
        if response in ['', 'y', 'yes']:
            source_config = default_source
        else:
            source_path = input("Enter path to usersettings.cleaned.json: ").strip()
            source_config = Path(source_path)
    else:
        print(f"\n⚠️  Cleaned config not found at: {default_source}")
        source_path = input("Enter path to usersettings.cleaned.json: ").strip()
        source_config = Path(source_path)
    
    # Step 4: Install cleaned config
    if not helper.install_clean_config(source_config):
        print("\n❌ Failed to install configuration")
        print(helper.generate_report())
        return 1
    
    # Step 5: Verify network endpoints
    helper.verify_network_endpoints(helper.config_path)
    
    # Step 6: Check SavedData folder
    helper.check_saved_data_folder(helper.config_path)
    
    # Step 7: Generate report
    print("\n")
    print(helper.generate_report())
    
    # Step 8: Offer to launch app
    if helper.issues:
        print("\n⚠️  There are critical issues. Please fix them before launching.")
        return 1
    
    print("\n" + "=" * 70)
    response = input("Launch Panda application now? (Y/n): ").strip().lower()
    
    if response in ['', 'y', 'yes']:
        helper.try_launch_app()
    
    print("\n✅ Setup complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

