#!/usr/bin/env python3
"""
Production-grade configuration validator and cleaner for usersettings.json.

This script performs comprehensive validation, cleaning, and normalization
of the usersettings.json configuration file used by the Focus Server client.

Features:
- JSON syntax validation and trailing comma removal
- Semantic validation (IP addresses, URLs, ranges, constraints)
- Configuration conflict detection (_TimeStatus vs TimeStatus)
- Produces clean production-ready config + detailed diff
- Environment-specific variants (prod, staging, dev)

Author: QA Automation Architect
Date: 2025-10-16
"""

import json
import difflib
import re
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
from urllib.parse import urlparse


class ConfigValidator:
    """Validates and cleans Focus Server user settings configuration."""

    def __init__(self, raw_json: str):
        """
        Initialize validator with raw JSON string.
        
        Args:
            raw_json: Raw JSON configuration string (may contain errors)
        """
        self.raw_json = raw_json
        self.issues: List[str] = []
        self.warnings: List[str] = []
        self.cleaned_data: Dict[str, Any] = {}

    def remove_trailing_commas(self, text: str) -> str:
        """
        Remove trailing commas that break JSON spec.
        
        Args:
            text: Raw JSON string with potential trailing commas
            
        Returns:
            JSON string with trailing commas removed
        """
        # Remove trailing commas before closing braces/brackets
        patterns = [
            (r',(\s*})', r'\1'),  # , before }
            (r',(\s*\])', r'\1'),  # , before ]
        ]
        
        result = text
        for pattern, replacement in patterns:
            result = re.sub(pattern, replacement, result)
        
        return result

    def parse_json(self) -> bool:
        """
        Parse and load JSON with error recovery.
        
        Returns:
            True if parsing succeeded, False otherwise
        """
        try:
            # First attempt: direct parse
            self.cleaned_data = json.loads(self.raw_json)
            return True
        except json.JSONDecodeError as e:
            self.issues.append(f"Initial JSON parse failed: {e}")
            
            # Second attempt: remove trailing commas
            try:
                cleaned = self.remove_trailing_commas(self.raw_json)
                self.cleaned_data = json.loads(cleaned)
                self.warnings.append("Removed trailing commas to fix JSON syntax")
                return True
            except json.JSONDecodeError as e2:
                self.issues.append(f"JSON parse failed even after cleaning: {e2}")
                return False

    def validate_url(self, url: str, field_name: str) -> bool:
        """
        Validate URL format and reachability structure.
        
        Args:
            url: URL string to validate
            field_name: Name of configuration field (for error reporting)
            
        Returns:
            True if URL is valid
        """
        try:
            parsed = urlparse(url)
            if not parsed.scheme in ['http', 'https']:
                self.issues.append(f"{field_name}: Invalid scheme '{parsed.scheme}' (must be http/https)")
                return False
            if not parsed.netloc:
                self.issues.append(f"{field_name}: Missing network location")
                return False
            return True
        except Exception as e:
            self.issues.append(f"{field_name}: URL validation error - {e}")
            return False

    def validate_ip_consistency(self) -> None:
        """Check for IP address consistency across endpoints."""
        comm = self.cleaned_data.get("Communication", {})
        
        backend = comm.get("Backend", "")
        frontend = comm.get("Frontend", "")
        frontend_api = comm.get("FrontendApi", "")
        
        # Extract IPs
        ips = []
        for url, name in [(backend, "Backend"), (frontend, "Frontend"), (frontend_api, "FrontendApi")]:
            match = re.search(r'(\d+\.\d+\.\d+\.\d+)', url)
            if match:
                ips.append((name, match.group(1)))
        
        if len(set(ip for _, ip in ips)) > 1:
            self.warnings.append(
                f"Multiple different IPs detected: {', '.join(f'{n}={ip}' for n, ip in ips)}. "
                "Verify this is intentional (e.g., load balancer setup)."
            )

    def validate_constraints(self) -> None:
        """Validate numerical constraints and ranges."""
        constraints = self.cleaned_data.get("Constraints", {})
        
        freq_min = constraints.get("FrequencyMin", 0)
        freq_max = constraints.get("FrequencyMax", 0)
        
        if freq_min >= freq_max:
            self.issues.append(
                f"FrequencyMin ({freq_min}) must be < FrequencyMax ({freq_max})"
            )
        
        defaults = self.cleaned_data.get("Defaults", {})
        start_freq = defaults.get("StartFrequency_hz", 0)
        end_freq = defaults.get("EndFrequency_hz", 0)
        
        if start_freq < freq_min or start_freq > freq_max:
            self.warnings.append(
                f"StartFrequency_hz ({start_freq}) outside Constraints range [{freq_min}, {freq_max}]"
            )
        
        if end_freq < freq_min or end_freq > freq_max:
            self.warnings.append(
                f"EndFrequency_hz ({end_freq}) outside Constraints range [{freq_min}, {freq_max}]"
            )

    def validate_time_status_conflict(self) -> bool:
        """
        Detect and resolve _TimeStatus vs TimeStatus conflict.
        
        Returns:
            True if conflict was found and resolved
        """
        defaults = self.cleaned_data.get("Defaults", {})
        
        if "_TimeStatus" in defaults and "TimeStatus" in defaults:
            private_val = defaults["_TimeStatus"]
            public_val = defaults["TimeStatus"]
            
            if private_val != public_val:
                self.warnings.append(
                    f"CONFLICT: _TimeStatus='{private_val}' vs TimeStatus='{public_val}'. "
                    f"Keeping TimeStatus (public API) and removing _TimeStatus."
                )
                del defaults["_TimeStatus"]
                return True
        
        return False

    def clean_template_types(self) -> None:
        """Remove empty strings from TemplateTypes array."""
        template_types = self.cleaned_data.get("TemplateTypes", [])
        
        if "" in template_types:
            self.warnings.append("Removing empty string from TemplateTypes")
            self.cleaned_data["TemplateTypes"] = [t for t in template_types if t]

    def validate_paths(self) -> None:
        """Validate file system paths."""
        saved_data = self.cleaned_data.get("SavedData", {})
        folder = saved_data.get("Folder", "")
        
        if folder:
            # Basic path validation (Windows-style in this case)
            if not re.match(r'^[A-Za-z]:\\', folder):
                self.warnings.append(
                    f"SavedData.Folder '{folder}' doesn't look like a valid Windows path"
                )

    def validate_performance_settings(self) -> None:
        """Check for potential performance issues."""
        num_live = self.cleaned_data.get("NumLiveScreens", 0)
        max_windows = self.cleaned_data.get("Constraints", {}).get("MaxWindows", 0)
        refresh_rate = self.cleaned_data.get("RefreshRate", 0)
        
        if num_live >= 20:
            self.warnings.append(
                f"NumLiveScreens={num_live} is high. Consider reducing for better performance."
            )
        
        if refresh_rate >= 30:
            self.warnings.append(
                f"RefreshRate={refresh_rate} is very high. May cause CPU load."
            )

    def run_full_validation(self) -> bool:
        """
        Execute complete validation pipeline.
        
        Returns:
            True if validation passed (no critical issues)
        """
        # Step 1: Parse JSON
        if not self.parse_json():
            return False
        
        # Step 2: Validate URLs
        comm = self.cleaned_data.get("Communication", {})
        self.validate_url(comm.get("Backend", ""), "Communication.Backend")
        self.validate_url(comm.get("Frontend", ""), "Communication.Frontend")
        self.validate_url(comm.get("FrontendApi", ""), "Communication.FrontendApi")
        
        # Step 3: Semantic validations
        self.validate_ip_consistency()
        self.validate_constraints()
        self.validate_time_status_conflict()
        self.clean_template_types()
        self.validate_paths()
        self.validate_performance_settings()
        
        return len(self.issues) == 0

    def get_clean_json(self, indent: int = 2) -> str:
        """
        Get cleaned, formatted JSON string.
        
        Args:
            indent: Number of spaces for indentation
            
        Returns:
            Pretty-printed JSON string
        """
        return json.dumps(self.cleaned_data, indent=indent, ensure_ascii=False)

    def generate_diff(self, original_lines: List[str], cleaned_lines: List[str]) -> str:
        """
        Generate unified diff between original and cleaned versions.
        
        Args:
            original_lines: Original config lines
            cleaned_lines: Cleaned config lines
            
        Returns:
            Unified diff string
        """
        return "\n".join(difflib.unified_diff(
            original_lines,
            cleaned_lines,
            fromfile="usersettings.json (original)",
            tofile="usersettings.json (cleaned)",
            lineterm=""
        ))

    def print_report(self) -> None:
        """Print validation report to console."""
        print("=" * 80)
        print("FOCUS SERVER USERSETTINGS.JSON VALIDATION REPORT")
        print("=" * 80)
        
        if self.issues:
            print("\n[ERROR] CRITICAL ISSUES FOUND:")
            for i, issue in enumerate(self.issues, 1):
                print(f"  {i}. {issue}")
        else:
            print("\n[OK] No critical issues found")
        
        if self.warnings:
            print("\n[WARNING] WARNINGS:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
        else:
            print("\n[OK] No warnings")
        
        print("\n" + "=" * 80)


def create_environment_variants(base_config: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Create environment-specific configuration variants.
    
    Args:
        base_config: Base cleaned configuration
        
    Returns:
        Dictionary with 'production', 'staging', 'development' configs
    """
    import copy
    
    configs = {}
    
    # Production (base)
    configs['production'] = copy.deepcopy(base_config)
    configs['production']['Communication']['Backend'] = "https://10.10.100.100/focus-server/"
    configs['production']['Communication']['Frontend'] = "https://10.10.10.100/liveView"
    configs['production']['Communication']['FrontendApi'] = "https://10.10.10.150:30443/prisma/api/internal/sites/prisma-210-1000"
    configs['production']['EnableDebugTools'] = False
    
    # Staging
    configs['staging'] = copy.deepcopy(base_config)
    configs['staging']['Communication']['Backend'] = "https://10.10.10.200/focus-server/"
    configs['staging']['Communication']['Frontend'] = "https://10.10.10.200/liveView"
    configs['staging']['Communication']['FrontendApi'] = "https://10.10.10.200:30443/prisma/api/internal/sites/prisma-210-1000-staging"
    configs['staging']['Communication']['SiteId'] = "prisma-210-1000-staging"
    configs['staging']['EnableDebugTools'] = True
    
    # Development
    configs['development'] = copy.deepcopy(base_config)
    configs['development']['Communication']['Backend'] = "http://localhost:5000/focus-server/"
    configs['development']['Communication']['Frontend'] = "http://localhost:3000/liveView"
    configs['development']['Communication']['FrontendApi'] = "http://localhost:8080/prisma/api/internal/sites/prisma-210-1000-dev"
    configs['development']['Communication']['SiteId'] = "prisma-210-1000-dev"
    configs['development']['EnableDebugTools'] = True
    configs['development']['Logger']['LogGrpcMessages'] = True
    configs['development']['Logger']['LogGrpcValidation'] = True
    configs['development']['NumLiveScreens'] = 5
    configs['development']['RefreshRate'] = 10
    
    return configs


def main():
    """Main execution flow."""
    # Read the current cleaned file
    input_file = Path(r"c:\Users\roy.avrahami\Downloads\usersettings.cleaned.json")
    
    if not input_file.exists():
        print(f"[ERROR] Input file not found: {input_file}")
        sys.exit(1)
    
    print(f"[INFO] Reading configuration from: {input_file}")
    raw_content = input_file.read_text(encoding='utf-8')
    
    # Validate and clean
    validator = ConfigValidator(raw_content)
    success = validator.run_full_validation()
    
    # Print report
    validator.print_report()
    
    if not success:
        print("\n[ERROR] Validation failed with critical issues. Please fix before proceeding.")
        sys.exit(1)
    
    # Get cleaned JSON
    cleaned_json = validator.get_clean_json(indent=2)
    
    # Save cleaned version to project
    output_dir = Path(r"c:\Projects\focus_server_automation\config")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "usersettings.production.json"
    output_file.write_text(cleaned_json, encoding='utf-8')
    print(f"\n[SUCCESS] Saved production config to: {output_file}")
    
    # Generate diff
    diff = validator.generate_diff(
        raw_content.splitlines(),
        cleaned_json.splitlines()
    )
    
    diff_file = output_dir / "usersettings.changes.diff"
    diff_file.write_text(diff, encoding='utf-8')
    print(f"[SUCCESS] Saved diff to: {diff_file}")
    
    # Create environment variants
    print("\n[INFO] Generating environment-specific variants...")
    variants = create_environment_variants(validator.cleaned_data)
    
    for env_name, env_config in variants.items():
        env_file = output_dir / f"usersettings.{env_name}.json"
        env_file.write_text(
            json.dumps(env_config, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        print(f"[SUCCESS] Created {env_name} config: {env_file}")
    
    print("\n" + "=" * 80)
    print("[SUCCESS] ALL TASKS COMPLETED SUCCESSFULLY")
    print("=" * 80)


if __name__ == "__main__":
    main()

