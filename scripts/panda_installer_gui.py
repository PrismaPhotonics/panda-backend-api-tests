#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PandaApp Automated Installer with GUI
======================================

This script provides a graphical interface for automated PandaApp installation.
Supports silent installation, updates, and configuration management.

Features:
- GUI with tkinter (cross-platform)
- Automatic .NET detection and installation
- Configuration validation
- Network connectivity checks
- Progress tracking
- Logging
- CI/CD integration support

Author: QA Automation Architect
Date: 2025-10-16
Version: 1.0.0
"""

import os
import sys
import json
import shutil
import subprocess
import urllib.request
import logging
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from datetime import datetime
import ctypes

# Try to import tkinter for GUI
try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, scrolledtext
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    print("Warning: tkinter not available, running in CLI mode only")


# ============================================================================
# Configuration
# ============================================================================

CONFIG = {
    "app_name": "PandaApp",
    "app_version": "1.2.41",
    "app_install_path": r"C:\Program Files\Prisma\PandaApp",
    "app_exe_name": "PandaApp-1.2.41.exe",
    
    "dotnet_version": "9.0",
    "dotnet_download_url": "https://aka.ms/dotnet/9.0/windowsdesktop-runtime-win-x64.exe",
    "dotnet_installer_name": "windowsdesktop-runtime-9.0-win-x64.exe",
    
    "config_file_name": "usersettings.json",
    "saved_data_path": r"C:\Panda\SavedData",
    
    "default_installer_paths": [
        Path.home() / "Downloads",
        Path("C:/Temp"),
        Path("./installers"),
    ],
    
    "default_config_paths": [
        Path.home() / "Downloads",
        Path("C:/Projects/focus_server_automation/config"),
        Path("./config"),
    ],
    
    "network_endpoints": [
        {"name": "Backend", "host": "10.10.100.100", "port": 443},
        {"name": "Frontend", "host": "10.10.10.100", "port": 443},
        {"name": "FrontendApi", "host": "10.10.10.150", "port": 30443},
    ],
    
    "temp_dir": Path("C:/Temp/PandaApp-Install"),
    "log_file": Path("C:/Temp/PandaApp-Install.log"),
}


# ============================================================================
# Logging Setup
# ============================================================================

def setup_logging(log_file: Path) -> logging.Logger:
    """
    Configure logging to file and console
    
    Args:
        log_file: Path to log file
        
    Returns:
        Configured logger instance
    """
    # Ensure log directory exists
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("PandaInstaller")
    logger.setLevel(logging.DEBUG)
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - [%(levelname)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('[%(levelname)s] %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


logger = setup_logging(CONFIG["log_file"])


# ============================================================================
# System Utilities
# ============================================================================

def is_admin() -> bool:
    """
    Check if script is running with Administrator privileges
    
    Returns:
        True if running as Administrator
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def run_as_admin():
    """
    Restart script with Administrator privileges
    """
    if not is_admin():
        logger.warning("Requesting Administrator privileges...")
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit(0)


def find_file(filename_pattern: str, search_paths: List[Path]) -> Optional[Path]:
    """
    Search for a file in multiple directories
    
    Args:
        filename_pattern: File name or pattern to search for
        search_paths: List of directories to search in
        
    Returns:
        Path to file if found, None otherwise
    """
    for search_path in search_paths:
        if not search_path.exists():
            continue
        
        # Try exact match first
        file_path = search_path / filename_pattern
        if file_path.exists():
            return file_path
        
        # Try glob pattern
        files = list(search_path.glob(filename_pattern))
        if files:
            return files[0]
    
    return None


def test_network_connectivity(host: str, port: int, timeout: int = 5) -> bool:
    """
    Test TCP connectivity to a host:port
    
    Args:
        host: Hostname or IP address
        port: Port number
        timeout: Timeout in seconds
        
    Returns:
        True if connection successful
    """
    import socket
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        logger.debug(f"Network test failed for {host}:{port} - {e}")
        return False


# ============================================================================
# Installation Functions
# ============================================================================

class PandaInstaller:
    """
    Main installer class for PandaApp
    """
    
    def __init__(self, silent_mode: bool = False, auto_update: bool = False):
        """
        Initialize installer
        
        Args:
            silent_mode: Run without user prompts
            auto_update: Automatically check for updates
        """
        self.silent_mode = silent_mode
        self.auto_update = auto_update
        self.config = CONFIG
        self.installer_path: Optional[Path] = None
        self.config_path: Optional[Path] = None
        
    def check_dotnet_installed(self) -> bool:
        """
        Check if required .NET version is installed
        
        Returns:
            True if .NET is installed
        """
        try:
            result = subprocess.run(
                ["dotnet", "--list-runtimes"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return False
            
            required_version = self.config["dotnet_version"]
            return f"Microsoft.WindowsDesktop.App {required_version}" in result.stdout
        except Exception as e:
            logger.debug(f"Failed to check .NET version: {e}")
            return False
    
    def install_dotnet(self) -> bool:
        """
        Download and install .NET Desktop Runtime
        
        Returns:
            True if installation successful
        """
        logger.info(f"Installing .NET {self.config['dotnet_version']} Desktop Runtime...")
        
        if self.check_dotnet_installed():
            logger.info(f".NET {self.config['dotnet_version']} already installed")
            return True
        
        # Create temp directory
        temp_dir = self.config["temp_dir"]
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        installer_path = temp_dir / self.config["dotnet_installer_name"]
        
        try:
            # Download installer
            logger.info("Downloading .NET installer...")
            urllib.request.urlretrieve(
                self.config["dotnet_download_url"],
                installer_path
            )
            
            file_size_mb = installer_path.stat().st_size / (1024 * 1024)
            logger.info(f"Downloaded: {file_size_mb:.2f} MB")
            
            # Run installer
            logger.info("Running .NET installer (this may take 30-60 seconds)...")
            result = subprocess.run(
                [str(installer_path), "/install", "/quiet", "/norestart"],
                capture_output=True,
                timeout=300
            )
            
            # Clean up
            installer_path.unlink(missing_ok=True)
            
            if result.returncode in [0, 1638]:  # 0=success, 1638=already installed
                logger.info(".NET installed successfully")
                return True
            else:
                logger.error(f".NET installation failed with exit code: {result.returncode}")
                return False
        
        except Exception as e:
            logger.error(f"Failed to install .NET: {e}")
            return False
    
    def find_installer(self) -> bool:
        """
        Locate PandaApp installer
        
        Returns:
            True if installer found
        """
        if self.installer_path and self.installer_path.exists():
            return True
        
        logger.info("Searching for PandaApp installer...")
        installer_pattern = "PandaAppInstaller*.exe"
        
        self.installer_path = find_file(
            installer_pattern,
            self.config["default_installer_paths"]
        )
        
        if self.installer_path:
            logger.info(f"Found installer: {self.installer_path}")
            return True
        else:
            logger.error("Installer not found in default locations")
            return False
    
    def install_application(self) -> bool:
        """
        Install PandaApp from installer
        
        Returns:
            True if installation successful
        """
        if not self.installer_path or not self.installer_path.exists():
            logger.error("Installer path not set or file not found")
            return False
        
        logger.info(f"Installing PandaApp from: {self.installer_path}")
        
        try:
            # Run installer
            if self.silent_mode:
                # Try silent mode
                result = subprocess.run(
                    [str(self.installer_path), "/S"],
                    capture_output=True,
                    timeout=300
                )
            else:
                # Interactive mode
                result = subprocess.run(
                    [str(self.installer_path)],
                    timeout=300
                )
            
            # Wait for installation to complete
            import time
            time.sleep(2)
            
            # Check if installed
            app_path = Path(self.config["app_install_path"])
            if app_path.exists():
                logger.info("PandaApp installed successfully")
                return True
            else:
                logger.warning("Installation completed but application not found at expected location")
                return False
        
        except Exception as e:
            logger.error(f"Failed to install PandaApp: {e}")
            return False
    
    def find_config(self) -> bool:
        """
        Locate configuration file
        
        Returns:
            True if config found
        """
        if self.config_path and self.config_path.exists():
            return True
        
        logger.info("Searching for configuration file...")
        config_pattern = "usersettings*.json"
        
        self.config_path = find_file(
            config_pattern,
            self.config["default_config_paths"]
        )
        
        if self.config_path:
            logger.info(f"Found config: {self.config_path}")
            return True
        else:
            logger.warning("Configuration file not found")
            return False
    
    def install_configuration(self) -> bool:
        """
        Install configuration file
        
        Returns:
            True if installation successful
        """
        if not self.config_path or not self.config_path.exists():
            logger.warning("Configuration file not available - skipping")
            return False
        
        target_path = Path(self.config["app_install_path"]) / self.config["config_file_name"]
        
        logger.info("Installing configuration file...")
        
        try:
            # Validate JSON
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            logger.info("Configuration file validated (valid JSON)")
            
            # Backup existing
            if target_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = target_path.parent / f"{target_path.name}.backup_{timestamp}"
                shutil.copy2(target_path, backup_path)
                logger.info(f"Backed up existing config to: {backup_path}")
            
            # Copy new config
            shutil.copy2(self.config_path, target_path)
            logger.info("Configuration installed successfully")
            return True
        
        except Exception as e:
            logger.error(f"Failed to install configuration: {e}")
            return False
    
    def initialize_directories(self) -> bool:
        """
        Create required directories
        
        Returns:
            True if successful
        """
        logger.info("Initializing directories...")
        
        try:
            saved_data_path = Path(self.config["saved_data_path"])
            saved_data_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created/verified SavedData directory: {saved_data_path}")
            
            # Test write permissions
            test_file = saved_data_path / ".write_test"
            test_file.write_text("test")
            test_file.unlink()
            logger.info("SavedData directory is writable")
            
            return True
        except Exception as e:
            logger.error(f"Failed to initialize directories: {e}")
            return False
    
    def check_network(self) -> Dict[str, bool]:
        """
        Check network connectivity to required endpoints
        
        Returns:
            Dictionary of endpoint: connectivity status
        """
        logger.info("Checking network connectivity...")
        results = {}
        
        for endpoint in self.config["network_endpoints"]:
            name = endpoint["name"]
            host = endpoint["host"]
            port = endpoint["port"]
            
            is_reachable = test_network_connectivity(host, port)
            results[name] = is_reachable
            
            if is_reachable:
                logger.info(f"✓ {name} ({host}:{port}) - Reachable")
            else:
                logger.warning(f"✗ {name} ({host}:{port}) - Not reachable")
        
        return results
    
    def launch_application(self) -> bool:
        """
        Launch PandaApp
        
        Returns:
            True if launched successfully
        """
        app_path = Path(self.config["app_install_path"])
        exe_path = app_path / self.config["app_exe_name"]
        
        if not exe_path.exists():
            logger.error(f"Executable not found: {exe_path}")
            return False
        
        try:
            logger.info("Launching PandaApp...")
            subprocess.Popen(
                [str(exe_path)],
                cwd=str(app_path),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
            )
            
            logger.info("PandaApp launched successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to launch PandaApp: {e}")
            return False
    
    def run_installation(self) -> bool:
        """
        Execute full installation workflow
        
        Returns:
            True if installation successful
        """
        logger.info("=" * 80)
        logger.info("PandaApp Automated Installation")
        logger.info("=" * 80)
        logger.info(f"Installation started at {datetime.now()}")
        logger.info(f"Log file: {self.config['log_file']}")
        
        # Step 1: Check admin
        if not is_admin():
            logger.error("Administrator privileges required")
            return False
        
        # Step 2: Install .NET
        if not self.install_dotnet():
            logger.error("Failed to install .NET Runtime")
            return False
        
        # Step 3: Find installer
        if not self.find_installer():
            logger.error("PandaApp installer not found")
            return False
        
        # Step 4: Install application
        if not self.install_application():
            logger.error("Failed to install PandaApp")
            return False
        
        # Step 5: Install configuration
        if self.find_config():
            self.install_configuration()
        
        # Step 6: Initialize directories
        self.initialize_directories()
        
        # Step 7: Check network
        self.check_network()
        
        logger.info("=" * 80)
        logger.info("Installation completed successfully!")
        logger.info("=" * 80)
        
        return True


# ============================================================================
# GUI Application (if tkinter available)
# ============================================================================

if GUI_AVAILABLE:
    class InstallerGUI:
        """
        GUI for PandaApp installer
        """
        
        def __init__(self, root: tk.Tk):
            self.root = root
            self.root.title("PandaApp Automated Installer")
            self.root.geometry("800x600")
            self.root.resizable(True, True)
            
            self.installer = PandaInstaller(silent_mode=False)
            self.setup_ui()
        
        def setup_ui(self):
            """Setup GUI components"""
            # Header
            header_frame = ttk.Frame(self.root, padding="10")
            header_frame.pack(fill="x")
            
            title_label = ttk.Label(
                header_frame,
                text="PandaApp Automated Installer",
                font=("Arial", 16, "bold")
            )
            title_label.pack()
            
            version_label = ttk.Label(header_frame, text="Version 1.0.0")
            version_label.pack()
            
            # File selection frame
            file_frame = ttk.LabelFrame(self.root, text="Files", padding="10")
            file_frame.pack(fill="x", padx=10, pady=5)
            
            # Installer path
            ttk.Label(file_frame, text="Installer:").grid(row=0, column=0, sticky="w", pady=2)
            self.installer_var = tk.StringVar()
            ttk.Entry(file_frame, textvariable=self.installer_var, width=60).grid(row=0, column=1, padx=5)
            ttk.Button(file_frame, text="Browse...", command=self.browse_installer).grid(row=0, column=2)
            
            # Config path
            ttk.Label(file_frame, text="Config:").grid(row=1, column=0, sticky="w", pady=2)
            self.config_var = tk.StringVar()
            ttk.Entry(file_frame, textvariable=self.config_var, width=60).grid(row=1, column=1, padx=5)
            ttk.Button(file_frame, text="Browse...", command=self.browse_config).grid(row=1, column=2)
            
            # Options frame
            options_frame = ttk.LabelFrame(self.root, text="Options", padding="10")
            options_frame.pack(fill="x", padx=10, pady=5)
            
            self.auto_find_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(options_frame, text="Auto-find files", variable=self.auto_find_var).pack(anchor="w")
            
            self.launch_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(options_frame, text="Launch after installation", variable=self.launch_var).pack(anchor="w")
            
            # Progress frame
            progress_frame = ttk.LabelFrame(self.root, text="Progress", padding="10")
            progress_frame.pack(fill="both", expand=True, padx=10, pady=5)
            
            self.log_text = scrolledtext.ScrolledText(progress_frame, height=15, wrap=tk.WORD)
            self.log_text.pack(fill="both", expand=True)
            
            self.progress_var = tk.DoubleVar()
            self.progress_bar = ttk.Progressbar(
                progress_frame,
                variable=self.progress_var,
                maximum=100,
                mode="determinate"
            )
            self.progress_bar.pack(fill="x", pady=5)
            
            # Buttons frame
            button_frame = ttk.Frame(self.root, padding="10")
            button_frame.pack(fill="x")
            
            self.install_button = ttk.Button(
                button_frame,
                text="Install",
                command=self.start_installation,
                width=20
            )
            self.install_button.pack(side="left", padx=5)
            
            ttk.Button(
                button_frame,
                text="Exit",
                command=self.root.quit,
                width=20
            ).pack(side="right", padx=5)
            
            # Redirect logger to GUI
            self.setup_logging_handler()
        
        def browse_installer(self):
            """Browse for installer file"""
            filename = filedialog.askopenfilename(
                title="Select PandaApp Installer",
                filetypes=[("Executable", "*.exe"), ("All files", "*.*")]
            )
            if filename:
                self.installer_var.set(filename)
        
        def browse_config(self):
            """Browse for config file"""
            filename = filedialog.askopenfilename(
                title="Select Configuration File",
                filetypes=[("JSON", "*.json"), ("All files", "*.*")]
            )
            if filename:
                self.config_var.set(filename)
        
        def setup_logging_handler(self):
            """Redirect logging to GUI text widget"""
            class GUIHandler(logging.Handler):
                def __init__(self, text_widget):
                    super().__init__()
                    self.text_widget = text_widget
                
                def emit(self, record):
                    msg = self.format(record)
                    self.text_widget.insert(tk.END, msg + "\n")
                    self.text_widget.see(tk.END)
                    self.text_widget.update()
            
            gui_handler = GUIHandler(self.log_text)
            gui_handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
            logger.addHandler(gui_handler)
        
        def start_installation(self):
            """Start installation process"""
            self.install_button.config(state="disabled")
            
            try:
                # Set paths
                if self.installer_var.get():
                    self.installer.installer_path = Path(self.installer_var.get())
                
                if self.config_var.get():
                    self.installer.config_path = Path(self.config_var.get())
                
                # Run installation
                success = self.installer.run_installation()
                
                if success:
                    if self.launch_var.get():
                        self.installer.launch_application()
                    
                    messagebox.showinfo("Success", "Installation completed successfully!")
                else:
                    messagebox.showerror("Error", "Installation failed. Check log for details.")
            
            except Exception as e:
                logger.error(f"Installation error: {e}")
                messagebox.showerror("Error", f"Installation failed: {e}")
            
            finally:
                self.install_button.config(state="normal")


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PandaApp Automated Installer")
    parser.add_argument("--gui", action="store_true", help="Launch GUI (default if available)")
    parser.add_argument("--cli", action="store_true", help="Force CLI mode")
    parser.add_argument("--silent", action="store_true", help="Silent installation")
    parser.add_argument("--installer", type=str, help="Path to installer")
    parser.add_argument("--config", type=str, help="Path to config file")
    parser.add_argument("--auto-update", action="store_true", help="Auto-update enabled")
    parser.add_argument("--admin", action="store_true", help="Request admin privileges")
    
    args = parser.parse_args()
    
    # Request admin if needed
    if args.admin and not is_admin():
        run_as_admin()
        return
    
    # Determine mode
    if args.cli or not GUI_AVAILABLE or args.silent:
        # CLI mode
        installer = PandaInstaller(
            silent_mode=args.silent,
            auto_update=args.auto_update
        )
        
        if args.installer:
            installer.installer_path = Path(args.installer)
        
        if args.config:
            installer.config_path = Path(args.config)
        
        success = installer.run_installation()
        sys.exit(0 if success else 1)
    else:
        # GUI mode
        root = tk.Tk()
        app = InstallerGUI(root)
        root.mainloop()


if __name__ == "__main__":
    main()

