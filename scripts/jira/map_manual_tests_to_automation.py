#!/usr/bin/env python3
"""
Map Manual Tests to Automation Tests
====================================

This script:
1. Finds manual tests in Jira (project = Automation or specific project)
2. Searches for corresponding automation tests in code
3. Links manual tests to automation test IDs
4. Creates configuration file for running tests from Jira

Usage:
    # Map all manual tests in Automation project
    python scripts/jira/map_manual_tests_to_automation.py --project Automation
    
    # Map specific test
    python scripts/jira/map_manual_tests_to_automation.py --test-id PZ-12345
    
    # Dry run (preview only)
    python scripts/jira/map_manual_tests_to_automation.py --project Automation --dry-run
    
    # Generate configuration file
    python scripts/jira/map_manual_tests_to_automation.py --project Automation --generate-config
"""

import argparse
import sys
import logging
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test Type custom field ID
TEST_TYPE_FIELD_ID = "customfield_10951"

# Automation Test ID custom field (if exists)
AUTOMATION_TEST_ID_FIELD = "customfield_10952"  # Update if different


class ManualTestMapper:
    """Maps manual tests in Jira to automation tests in code."""
    
    def __init__(self, jira_client: JiraClient):
        """Initialize the mapper."""
        self.jira_client = jira_client
        self.mappings: List[Dict[str, Any]] = []
        self.automation_tests_cache: Dict[str, Dict[str, Any]] = {}
        
    def find_manual_tests(self, project_key: str = None, test_id: str = None) -> List[Dict[str, Any]]:
        """
        Find manual tests in Jira.
        
        Args:
            project_key: Project key to search (e.g., "Automation", "PZ")
            test_id: Specific test ID to find
            
        Returns:
            List of manual test issues
        """
        logger.info("=" * 80)
        logger.info("Finding Manual Tests in Jira")
        logger.info("=" * 80)
        
        if test_id:
            # Get specific test
            logger.info(f"Getting specific test: {test_id}")
            try:
                issue = self.jira_client.get_issue(test_id)
                if issue:
                    test_info = self._extract_test_info(issue)
                    if test_info:
                        return [test_info]
            except Exception as e:
                logger.error(f"Error getting test {test_id}: {e}")
                return []
        else:
            # Search for manual tests
            jql_parts = [
                "issuetype = Test",
                f'"{TEST_TYPE_FIELD_ID}" = "Manual Test" OR "{TEST_TYPE_FIELD_ID}" is EMPTY'
            ]
            
            if project_key:
                jql_parts.insert(0, f"project = {project_key}")
            else:
                jql_parts.insert(0, "project = PZ")
            
            jql = " AND ".join(jql_parts)
            logger.info(f"JQL Query: {jql}")
            
            try:
                issues = self.jira_client.search_issues(jql, max_results=1000)
                logger.info(f"Found {len(issues)} potential manual tests")
                
                manual_tests = []
                for issue in issues:
                    test_info = self._extract_test_info(issue)
                    if test_info:
                        manual_tests.append(test_info)
                
                logger.info(f"Extracted {len(manual_tests)} manual tests")
                return manual_tests
                
            except Exception as e:
                logger.error(f"Error searching for manual tests: {e}")
                return []
    
    def _extract_test_info(self, issue) -> Optional[Dict[str, Any]]:
        """Extract test information from Jira issue."""
        try:
            fields = issue.fields
            
            # Get test type
            test_type = None
            if hasattr(fields, TEST_TYPE_FIELD_ID.replace("customfield_", "")):
                test_type_field = getattr(fields, TEST_TYPE_FIELD_ID.replace("customfield_", ""), None)
                if test_type_field:
                    test_type = test_type_field.value if hasattr(test_type_field, 'value') else str(test_type_field)
            
            # Check if it's a manual test
            if test_type and test_type.lower() not in ["manual test", "manual"]:
                # Check if test type is empty (might be manual)
                if test_type:
                    return None
            
            return {
                "key": issue.key,
                "summary": fields.summary,
                "description": fields.description or "",
                "test_type": test_type or "Unknown",
                "status": fields.status.name,
                "project": fields.project.key,
                "url": f"{self.jira_client.base_url}/browse/{issue.key}"
            }
        except Exception as e:
            logger.warning(f"Error extracting test info from {issue.key}: {e}")
            return None
    
    def find_automation_test(self, manual_test: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find corresponding automation test in code.
        
        Args:
            manual_test: Manual test information from Jira
            
        Returns:
            Automation test information or None
        """
        summary = manual_test.get("summary", "").lower()
        description = manual_test.get("description", "").lower()
        test_key = manual_test.get("key", "")
        
        # Search strategies
        search_terms = []
        
        # Strategy 1: Extract keywords from summary
        keywords = self._extract_keywords(summary)
        search_terms.extend(keywords)
        
        # Strategy 2: Extract keywords from description
        desc_keywords = self._extract_keywords(description)
        search_terms.extend(desc_keywords)
        
        # Strategy 3: Use test key pattern (e.g., PZ-12345)
        if test_key:
            search_terms.append(test_key.lower())
        
        logger.debug(f"Search terms for {manual_test['key']}: {search_terms}")
        
        # Search in code
        automation_test = self._search_in_code(search_terms, manual_test)
        
        return automation_test
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text."""
        if not text:
            return []
        
        # Remove common words
        stop_words = {
            "test", "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "should", "could",
            "may", "might", "must", "can", "this", "that", "these", "those"
        }
        
        # Extract words
        words = re.findall(r'\b[a-z]+\b', text.lower())
        keywords = [w for w in words if len(w) > 3 and w not in stop_words]
        
        # Remove duplicates and return
        return list(set(keywords))
    
    def _search_in_code(self, search_terms: List[str], manual_test: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Search for automation test in code."""
        tests_dir = project_root / "tests"
        
        if not tests_dir.exists():
            logger.warning(f"Tests directory not found: {tests_dir}")
            return None
        
        # Search for pytest markers with Xray ID
        test_key = manual_test.get("key", "")
        if test_key:
            # Direct search for Xray marker
            automation_test = self._find_by_xray_marker(test_key)
            if automation_test:
                return automation_test
        
        # Search by keywords in test files
        best_match = None
        best_score = 0
        
        for test_file in tests_dir.rglob("*.py"):
            if test_file.name.startswith("__"):
                continue
            
            try:
                content = test_file.read_text(encoding='utf-8', errors='ignore')
                
                # Calculate match score
                score = self._calculate_match_score(content, search_terms, manual_test)
                
                if score > best_score and score > 0.3:  # Threshold
                    best_score = score
                    best_match = {
                        "file": str(test_file.relative_to(project_root)),
                        "file_path": str(test_file),
                        "match_score": score,
                        "search_terms_matched": [t for t in search_terms if t in content.lower()]
                    }
                    
                    # Try to extract test function name
                    test_func = self._extract_test_function(content, search_terms)
                    if test_func:
                        best_match["test_function"] = test_func
                    
            except Exception as e:
                logger.debug(f"Error reading {test_file}: {e}")
                continue
        
        return best_match
    
    def _find_by_xray_marker(self, test_key: str) -> Optional[Dict[str, Any]]:
        """Find automation test by Xray marker."""
        tests_dir = project_root / "tests"
        marker_pattern = f'@pytest.mark.xray("{test_key}")'
        
        for test_file in tests_dir.rglob("*.py"):
            try:
                content = test_file.read_text(encoding='utf-8', errors='ignore')
                
                if marker_pattern in content:
                    # Extract test function
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if marker_pattern in line:
                            # Find next function definition
                            for j in range(i + 1, min(i + 10, len(lines))):
                                func_match = re.search(r'def\s+(test_\w+)', lines[j])
                                if func_match:
                                    return {
                                        "file": str(test_file.relative_to(project_root)),
                                        "file_path": str(test_file),
                                        "test_function": func_match.group(1),
                                        "match_score": 1.0,
                                        "match_method": "xray_marker"
                                    }
            except Exception as e:
                logger.debug(f"Error searching in {test_file}: {e}")
                continue
        
        return None
    
    def _calculate_match_score(self, content: str, search_terms: List[str], manual_test: Dict[str, Any]) -> float:
        """Calculate how well content matches search terms."""
        content_lower = content.lower()
        summary_lower = manual_test.get("summary", "").lower()
        
        score = 0.0
        matches = 0
        
        for term in search_terms:
            if term in content_lower:
                matches += 1
                # Higher weight if term appears in function/class names
                if f"def test_{term}" in content_lower or f"class.*{term}" in content_lower:
                    score += 0.3
                else:
                    score += 0.1
        
        # Normalize score
        if search_terms:
            score = score / len(search_terms)
        
        # Bonus for exact summary match
        if summary_lower and any(word in content_lower for word in summary_lower.split() if len(word) > 4):
            score += 0.2
        
        return min(score, 1.0)
    
    def _extract_test_function(self, content: str, search_terms: List[str]) -> Optional[str]:
        """Extract test function name from content."""
        # Look for test functions that match search terms
        pattern = r'def\s+(test_\w+)'
        functions = re.findall(pattern, content)
        
        for func in functions:
            func_lower = func.lower()
            for term in search_terms:
                if term in func_lower:
                    return func
        
        # Return first test function if found
        if functions:
            return functions[0]
        
        return None
    
    def link_manual_to_automation(
        self, 
        manual_test_key: str, 
        automation_test: Dict[str, Any],
        dry_run: bool = False
    ) -> bool:
        """
        Link manual test to automation test in Jira.
        
        Args:
            manual_test_key: Jira test key (e.g., "PZ-12345")
            automation_test: Automation test information
            dry_run: If True, don't actually update Jira
            
        Returns:
            True if successful
        """
        logger.info(f"Linking {manual_test_key} to automation test...")
        
        if dry_run:
            logger.info(f"[DRY RUN] Would link {manual_test_key} to:")
            logger.info(f"  File: {automation_test.get('file', 'N/A')}")
            logger.info(f"  Function: {automation_test.get('test_function', 'N/A')}")
            return True
        
        try:
            # Update Jira issue with automation link
            issue = self.jira_client.get_issue(manual_test_key)
            
            # Build description update with automation info
            current_desc = issue.fields.description or ""
            
            automation_section = f"""
h2. Automation Test
*Test File:* {{code}}{automation_test.get('file', 'N/A')}{{code}}
*Test Function:* {{code}}{automation_test.get('test_function', 'N/A')}{{code}}
*Match Score:* {automation_test.get('match_score', 0):.2f}

*Execution Command:*
{{code}}pytest {automation_test.get('file', '')}::{automation_test.get('test_function', '')} -v{{code}}
"""
            
            # Append automation section if not exists
            if "h2. Automation Test" not in current_desc:
                new_desc = current_desc + automation_section
            else:
                # Replace existing automation section
                new_desc = re.sub(
                    r'h2\. Automation Test.*?(?=h2\.|\Z)',
                    automation_section.strip(),
                    current_desc,
                    flags=re.DOTALL
                )
            
            # Update issue
            issue.update(description=new_desc)
            
            logger.info(f"✅ Successfully linked {manual_test_key} to automation test")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error linking {manual_test_key}: {e}")
            return False
    
    def generate_config_file(self, output_file: str = "jira_test_config.json"):
        """
        Generate configuration file for running tests from Jira.
        
        Args:
            output_file: Output file path
        """
        logger.info("=" * 80)
        logger.info("Generating Configuration File")
        logger.info("=" * 80)
        
        config = {
            "version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "mappings": self.mappings,
            "test_execution": {
                "default_command": "pytest",
                "default_flags": ["-v", "--tb=short"],
                "test_plan_format": "jira_test_plan_{test_plan_id}.json"
            }
        }
        
        output_path = project_root / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Configuration file generated: {output_path}")
        return output_path


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Map manual tests in Jira to automation tests in code"
    )
    parser.add_argument(
        "--project",
        type=str,
        help="Project key to search (e.g., 'Automation', 'PZ')"
    )
    parser.add_argument(
        "--test-id",
        type=str,
        help="Specific test ID to map (e.g., 'PZ-12345')"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without updating Jira"
    )
    parser.add_argument(
        "--generate-config",
        action="store_true",
        help="Generate configuration file for running tests"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="jira_test_config.json",
        help="Output configuration file path"
    )
    parser.add_argument(
        "--auto-link",
        action="store_true",
        help="Automatically link manual tests to automation tests"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize Jira client
        client = JiraClient()
        
        # Initialize mapper
        mapper = ManualTestMapper(client)
        
        # Find manual tests
        manual_tests = mapper.find_manual_tests(
            project_key=args.project,
            test_id=args.test_id
        )
        
        if not manual_tests:
            logger.warning("No manual tests found")
            return 1
        
        logger.info(f"\nFound {len(manual_tests)} manual tests")
        logger.info("=" * 80)
        
        # Map each manual test to automation
        mapped_count = 0
        linked_count = 0
        
        for manual_test in manual_tests:
            logger.info(f"\nProcessing: {manual_test['key']} - {manual_test['summary']}")
            
            # Find automation test
            automation_test = mapper.find_automation_test(manual_test)
            
            if automation_test:
                logger.info(f"  ✅ Found automation test:")
                logger.info(f"     File: {automation_test.get('file', 'N/A')}")
                logger.info(f"     Function: {automation_test.get('test_function', 'N/A')}")
                logger.info(f"     Match Score: {automation_test.get('match_score', 0):.2f}")
                
                # Store mapping
                mapping = {
                    "manual_test": manual_test,
                    "automation_test": automation_test,
                    "mapped_at": datetime.now().isoformat()
                }
                mapper.mappings.append(mapping)
                mapped_count += 1
                
                # Link if requested
                if args.auto_link:
                    if mapper.link_manual_to_automation(
                        manual_test['key'],
                        automation_test,
                        dry_run=args.dry_run
                    ):
                        linked_count += 1
            else:
                logger.warning(f"  ⚠️  No automation test found for {manual_test['key']}")
                mapping = {
                    "manual_test": manual_test,
                    "automation_test": None,
                    "mapped_at": datetime.now().isoformat()
                }
                mapper.mappings.append(mapping)
        
        # Generate configuration file
        if args.generate_config or args.auto_link:
            config_path = mapper.generate_config_file(args.output)
            logger.info(f"\n✅ Configuration saved to: {config_path}")
        
        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Manual tests found: {len(manual_tests)}")
        logger.info(f"Automation tests found: {mapped_count}")
        logger.info(f"Tests linked: {linked_count}")
        logger.info("=" * 80)
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

