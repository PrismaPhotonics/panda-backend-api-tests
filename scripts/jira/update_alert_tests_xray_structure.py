"""
Script to update all Alert Generation Xray test cases in Jira
with proper technical and professional structure.

Tests: PZ-14933 to PZ-14963 (31 tests)
"""

import os
import sys
import re
from typing import Dict, List, Any
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.infrastructure.jira_client import JiraClient


def extract_test_info_from_code(test_file: str, test_function: str) -> Dict[str, Any]:
    """
    Extract test information from Python test file.
    
    Args:
        test_file: Path to test file
        test_function: Test function name
        
    Returns:
        Dictionary with test information
    """
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the test function
        pattern = rf'def\s+{test_function}\(.*?\):\s*"""(.*?)"""'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            return {}
        
        docstring = match.group(1)
        
        # Extract Objective
        objective_match = re.search(r'Objective:\s*(.*?)(?=\n\s*Steps:|$)', docstring, re.DOTALL)
        objective = objective_match.group(1).strip() if objective_match else ''
        
        # Extract Steps
        steps_match = re.search(r'Steps:\s*(.*?)(?=\n\s*Expected:|$)', docstring, re.DOTALL)
        steps_text = steps_match.group(1).strip() if steps_match else ''
        steps = []
        if steps_text:
            step_lines = re.findall(r'\d+\.\s*(.*)', steps_text)
            steps = [{'action': line.strip(), 'data': '', 'expected': ''} for line in step_lines]
        
        # Extract Expected Result
        expected_match = re.search(r'Expected:\s*(.*?)(?=\n|$)', docstring, re.DOTALL)
        expected_result = expected_match.group(1).strip() if expected_match else ''
        
        # Extract test data from code
        test_data = []
        if 'classId' in content:
            class_id_match = re.search(r'"classId":\s*(\d+)', content)
            if class_id_match:
                class_id = class_id_match.group(1)
                alert_type = 'SD (Spatial Distribution)' if class_id == '104' else 'SC (Single Channel)'
                test_data.append(f'Alert Type: {alert_type}')
                test_data.append(f'Class ID: {class_id}')
        
        if 'dofM' in content:
            dof_match = re.search(r'"dofM":\s*(\d+)', content)
            if dof_match:
                test_data.append(f'DOF (Distance on Fiber): {dof_match.group(1)} meters')
        
        if 'severity' in content:
            severity_match = re.search(r'"severity":\s*(\d+)', content)
            if severity_match:
                severity = severity_match.group(1)
                severity_names = {'1': 'Low', '2': 'Medium', '3': 'High'}
                test_data.append(f'Severity: {severity} ({severity_names.get(severity, "Unknown")})')
        
        return {
            'objective': objective,
            'test_steps': steps,
            'expected_result': expected_result,
            'test_data': test_data
        }
    except Exception as e:
        print(f"Error extracting test info: {e}")
        return {}


def build_jira_description(test_id: str, test_info: Dict[str, Any], test_file: str, test_function: str) -> str:
    """
    Build proper Xray description in Jira markup format.
    
    Args:
        test_id: Test ID (e.g., PZ-14933)
        test_info: Test information dictionary
        test_file: Path to test file
        test_function: Test function name
        
    Returns:
        Formatted description string in Jira markup
    """
    parts = []
    
    # Objective
    parts.append("h2. Objective")
    objective = test_info.get('objective', f'Test objective for {test_id}')
    parts.append(objective)
    parts.append("")
    
    # Test Details
    parts.append("h2. Test Details")
    parts.append(f"* *Test ID:* {test_id}")
    parts.append(f"* *Test Type:* Integration Test")
    parts.append(f"* *Category:* {test_info.get('category', 'Positive')}")
    parts.append(f"* *File:* {test_file}")
    parts.append(f"* *Function:* {{code}}{test_function}{{code}}")
    parts.append("")
    
    # Prerequisites
    parts.append("h2. Prerequisites")
    pre_conditions = test_info.get('pre_conditions', [
        "Focus Server API is available and healthy",
        "Backend system is running and accessible",
        "Valid configuration manager with API credentials"
    ])
    for condition in pre_conditions:
        parts.append(f"* {condition}")
    parts.append("")
    
    # Test Data
    test_data = test_info.get('test_data', [])
    if test_data:
        parts.append("h2. Test Data")
        for item in test_data:
            parts.append(f"* {item}")
        parts.append("")
    
    # Test Steps
    test_steps = test_info.get('test_steps', [])
    if test_steps:
        parts.append("h2. Test Steps")
        parts.append("")
        parts.append("|| # || Action || Data || Expected Result ||")
        for i, step in enumerate(test_steps, 1):
            action = step.get('action', '')
            data = step.get('data', 'N/A')
            expected = step.get('expected', 'Success')
            parts.append(f"| {i} | {action} | {data} | {expected} |")
        parts.append("")
    
    # Expected Result
    expected_result = test_info.get('expected_result', 'Test completes successfully')
    if expected_result:
        parts.append("h2. Expected Result")
        parts.append(expected_result)
        parts.append("")
    
    # Post-Conditions
    post_conditions = test_info.get('post_conditions', [
        "Alert is sent to RabbitMQ queue",
        "System remains stable and operational"
    ])
    if post_conditions:
        parts.append("h2. Post-Conditions")
        for condition in post_conditions:
            parts.append(f"* {condition}")
        parts.append("")
    
    # Automation Status
    parts.append("h2. Automation Status")
    parts.append("✅ *Automated* with Pytest")
    parts.append("")
    parts.append(f"*Test Function:* {{code}}{test_function}{{code}}")
    parts.append(f"*Test File:* {{code}}{test_file}{{code}}")
    
    return "\n".join(parts)


# Test mapping with file paths and function names
TEST_MAPPING = {
    # Positive Tests
    'PZ-14933': {
        'file': 'be_focus_server_tests/integration/alerts/test_alert_generation_positive.py',
        'function': 'test_successful_sd_alert_generation',
        'category': 'Positive'
    },
    'PZ-14934': {
        'file': 'be_focus_server_tests/integration/alerts/test_alert_generation_positive.py',
        'function': 'test_successful_sc_alert_generation',
        'category': 'Positive'
    },
    'PZ-14935': {
        'file': 'be_focus_server_tests/integration/alerts/test_alert_generation_positive.py',
        'function': 'test_multiple_alerts_generation',
        'category': 'Positive'
    },
    'PZ-14936': {
        'file': 'be_focus_server_tests/integration/alerts/test_alert_generation_positive.py',
        'function': 'test_different_severity_levels',
        'category': 'Positive'
    },
    'PZ-14937': {
        'file': 'be_focus_server_tests/integration/alerts/test_alert_generation_positive.py',
        'function': 'test_alert_processing_via_rabbitmq',
        'category': 'Positive'
    },
    # Negative Tests
    'PZ-14938': {
        'file': 'be_focus_server_tests/integration/alerts/test_alert_generation_negative.py',
        'function': 'test_invalid_class_id',
        'category': 'Negative'
    },
    'PZ-14939': {
        'file': 'be_focus_server_tests/integration/alerts/test_alert_generation_negative.py',
        'function': 'test_invalid_severity',
        'category': 'Negative'
    },
    'PZ-14940': {
        'file': 'be_focus_server_tests/integration/alerts/test_alert_generation_negative.py',
        'function': 'test_invalid_dof_range',
        'category': 'Negative'
    },
    'PZ-14941': {
        'file': 'be_focus_server_tests/integration/alerts/test_alert_generation_negative.py',
        'function': 'test_missing_required_fields',
        'category': 'Negative'
    },
    'PZ-14942': {
        'file': 'be_focus_server_tests/integration/alerts/test_alert_generation_negative.py',
        'function': 'test_rabbitmq_connection_failure',
        'category': 'Negative'
    },
    'PZ-14943': {
        'file': 'be_focus_server_tests/integration/alerts/test_alert_generation_negative.py',
        'function': 'test_invalid_alert_id_format',
        'category': 'Negative'
    },
    'PZ-14944': {
        'file': 'be_focus_server_tests/integration/alerts/test_alert_generation_negative.py',
        'function': 'test_duplicate_alert_ids',
        'category': 'Negative'
    },
    # Edge Cases
    'PZ-14945': {
        'file': 'be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py',
        'function': 'test_boundary_dof_values',
        'category': 'Edge Case'
    },
    'PZ-14946': {
        'file': 'be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py',
        'function': 'test_min_max_severity',
        'category': 'Edge Case'
    },
    'PZ-14947': {
        'file': 'be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py',
        'function': 'test_zero_alerts_amount',
        'category': 'Edge Case'
    },
    'PZ-14948': {
        'file': 'be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py',
        'function': 'test_very_large_alert_id',
        'category': 'Edge Case'
    },
    'PZ-14949': {
        'file': 'be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py',
        'function': 'test_concurrent_alerts_same_dof',
        'category': 'Edge Case'
    },
    'PZ-14950': {
        'file': 'be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py',
        'function': 'test_rapid_sequential_alerts',
        'category': 'Edge Case'
    },
    'PZ-14951': {
        'file': 'be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py',
        'function': 'test_alert_maximum_fields',
        'category': 'Edge Case'
    },
    'PZ-14952': {
        'file': 'be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py',
        'function': 'test_alert_minimum_fields',
        'category': 'Edge Case'
    },
    # Load Tests
    'PZ-14953': {
        'file': 'be_focus_server_tests/integration/alerts/test_alert_generation_load.py',
        'function': 'test_high_volume_load',
        'category': 'Load'
    },
    'PZ-14954': {
        'file': 'be_focus_server_tests/integration/alerts/test_alert_generation_load.py',
        'function': 'test_sustained_load',
        'category': 'Load'
    },
    'PZ-14955': {
        'file': 'be_focus_server_tests/integration/alerts/test_alert_generation_load.py',
        'function': 'test_burst_load',
        'category': 'Load'
    },
    'PZ-14956': {
        'file': 'be_focus_server_tests/integration/alerts/test_alert_generation_load.py',
        'function': 'test_mixed_alert_types_load',
        'category': 'Load'
    },
    'PZ-14957': {
        'file': 'be_focus_server_tests/integration/alerts/test_alert_generation_load.py',
        'function': 'test_rabbitmq_queue_capacity',
        'category': 'Load'
    },
    # Performance Tests
    'PZ-14958': {
        'file': 'be_focus_server_tests/integration/alerts/test_alert_generation_performance.py',
        'function': 'test_alert_response_time',
        'category': 'Performance'
    },
    'PZ-14959': {
        'file': 'be_focus_server_tests/integration/alerts/test_alert_generation_performance.py',
        'function': 'test_alert_throughput',
        'category': 'Performance'
    },
    'PZ-14960': {
        'file': 'be_focus_server_tests/integration/alerts/test_alert_generation_performance.py',
        'function': 'test_alert_latency',
        'category': 'Performance'
    },
    'PZ-14961': {
        'file': 'be_focus_server_tests/integration/alerts/test_alert_generation_performance.py',
        'function': 'test_resource_usage',
        'category': 'Performance'
    },
    'PZ-14962': {
        'file': 'be_focus_server_tests/integration/alerts/test_alert_generation_performance.py',
        'function': 'test_end_to_end_performance',
        'category': 'Performance'
    },
    'PZ-14963': {
        'file': 'be_focus_server_tests/integration/alerts/test_alert_generation_performance.py',
        'function': 'test_rabbitmq_performance',
        'category': 'Performance'
    },
}


def main():
    """Main function to update all test cases."""
    print("=" * 80)
    print("Updating Alert Generation Xray Test Cases in Jira")
    print("=" * 80)
    
    # Initialize Jira client
    try:
        jira_client = JiraClient()
    except Exception as e:
        print(f"❌ Failed to initialize Jira client: {e}")
        return
    
    updated_count = 0
    failed_count = 0
    
    for test_id, test_info in TEST_MAPPING.items():
        try:
            print(f"\n📝 Processing {test_id}...")
            
            # Get file path
            test_file = test_info['file']
            test_function = test_info['function']
            full_path = project_root / test_file
            
            if not full_path.exists():
                print(f"⚠️  Test file not found: {test_file}")
                failed_count += 1
                continue
            
            # Extract test information from code
            code_info = extract_test_info_from_code(str(full_path), test_function)
            
            # Merge with mapping info
            test_info.update(code_info)
            
            # Build description
            description = build_jira_description(
                test_id=test_id,
                test_info=test_info,
                test_file=test_file,
                test_function=test_function
            )
            
            # Update Jira issue
            success = jira_client.update_issue_description(test_id, description)
            
            if success:
                print(f"✅ Updated {test_id}")
                updated_count += 1
            else:
                print(f"❌ Failed to update {test_id}")
                failed_count += 1
                
        except Exception as e:
            print(f"❌ Error processing {test_id}: {e}")
            failed_count += 1
    
    print("\n" + "=" * 80)
    print("Summary:")
    print(f"✅ Updated: {updated_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📊 Total: {len(TEST_MAPPING)}")
    print("=" * 80)


if __name__ == "__main__":
    main()

