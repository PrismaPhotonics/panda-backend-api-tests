"""
Complete script to update all 31 Alert Generation Xray test cases in Jira
with proper technical structure based on automation test code.

Tests: PZ-14933 to PZ-14963

This script builds descriptions from test code and updates Jira issues.
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def extract_test_info(test_file: Path, test_function: str) -> Dict[str, Any]:
    """Extract test information from Python file."""
    try:
        content = test_file.read_text(encoding='utf-8')
        
        # Find function docstring
        pattern = rf'def\s+{test_function}\(.*?\):\s*"""(.*?)"""'
        match = re.search(pattern, content, re.DOTALL)
        if not match:
            return {}
        
        docstring = match.group(1)
        
        # Extract Objective
        obj_match = re.search(r'Objective:\s*(.*?)(?=\n\s*Steps:|$)', docstring, re.DOTALL)
        objective = obj_match.group(1).strip() if obj_match else ''
        
        # Extract Steps
        steps_match = re.search(r'Steps:\s*(.*?)(?=\n\s*Expected:|$)', docstring, re.DOTALL)
        steps_text = steps_match.group(1).strip() if steps_match else ''
        steps = []
        if steps_text:
            step_lines = re.findall(r'\d+\.\s*(.*)', steps_text)
            steps = [{'action': line.strip(), 'data': '', 'expected': ''} for line in step_lines]
        
        # Extract Expected
        exp_match = re.search(r'Expected:\s*(.*?)(?=\n|$)', docstring, re.DOTALL)
        expected = exp_match.group(1).strip() if exp_match else ''
        
        # Extract test data from code
        test_data = []
        if 'classId' in content:
            cid_match = re.search(r'"classId":\s*(\d+)', content)
            if cid_match:
                cid = cid_match.group(1)
                alert_type = 'SD (Spatial Distribution)' if cid == '104' else 'SC (Single Channel)'
                test_data.append(f'*Alert Type:* {alert_type}')
                test_data.append(f'*Class ID:* {cid}')
        
        if 'dofM' in content:
            dof_match = re.search(r'"dofM":\s*(\d+)', content)
            if dof_match:
                test_data.append(f'*DOF (Distance on Fiber):* {dof_match.group(1)} meters')
        
        if 'severity' in content:
            sev_match = re.search(r'"severity":\s*(\d+)', content)
            if sev_match:
                sev = sev_match.group(1)
                sev_names = {'1': 'Low', '2': 'Medium', '3': 'High'}
                test_data.append(f'*Severity:* {sev} ({sev_names.get(sev, "Unknown")})')
        
        return {
            'objective': objective,
            'steps': steps,
            'expected': expected,
            'test_data': test_data
        }
    except Exception as e:
        print(f"Error extracting from {test_file}: {e}")
        return {}


def build_description(test_id: str, test_info: Dict[str, Any], file_path: str, function: str, category: str) -> str:
    """Build Jira markup description."""
    parts = []
    
    # Objective
    parts.append("h2. Objective")
    parts.append(test_info.get('objective', f'Test objective for {test_id}'))
    parts.append("")
    
    # Test Details
    parts.append("h2. Test Details")
    parts.append(f"* *Test ID:* {test_id}")
    parts.append("* *Test Type:* Integration Test")
    parts.append(f"* *Category:* {category}")
    parts.append(f"* *File:* {file_path}")
    parts.append(f"* *Function:* {{code}}{function}{{code}}")
    parts.append("")
    
    # Prerequisites
    parts.append("h2. Prerequisites")
    parts.append("* Focus Server API is available and healthy")
    parts.append("* Backend system is running and accessible")
    parts.append("* Valid configuration manager with API credentials")
    parts.append("")
    
    # Test Data
    test_data = test_info.get('test_data', [])
    if test_data:
        parts.append("h2. Test Data")
        for item in test_data:
            parts.append(item)
        parts.append("")
    
    # Test Steps
    steps = test_info.get('steps', [])
    if steps:
        parts.append("h2. Test Steps")
        parts.append("")
        parts.append("|| # || Action || Data || Expected Result ||")
        for i, step in enumerate(steps, 1):
            action = step.get('action', '')
            data = step.get('data', 'N/A')
            expected = step.get('expected', 'Success')
            parts.append(f"| {i} | {action} | {data} | {expected} |")
        parts.append("")
    
    # Expected Result
    expected = test_info.get('expected', 'Test completes successfully')
    if expected:
        parts.append("h2. Expected Result")
        parts.append(expected)
        parts.append("")
    
    # Post-Conditions
    parts.append("h2. Post-Conditions")
    parts.append("* Alert is sent to RabbitMQ queue")
    parts.append("* System remains stable and operational")
    parts.append("")
    
    # Automation Status
    parts.append("h2. Automation Status")
    parts.append("✅ *Automated* with Pytest")
    parts.append("")
    parts.append(f"*Test Function:* {{code}}{function}{{code}}")
    parts.append(f"*Test File:* {{code}}{file_path}{{code}}")
    
    return "\n".join(parts)


# Test mapping
TESTS = {
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
    """Generate descriptions for all tests."""
    print("=" * 80)
    print("Generating descriptions for all Alert Generation tests")
    print("=" * 80)
    
    descriptions = {}
    
    for test_id, test_config in TESTS.items():
        file_path = project_root / test_config['file']
        function = test_config['function']
        category = test_config['category']
        
        print(f"\nProcessing {test_id}...")
        
        if not file_path.exists():
            print(f"WARNING: File not found: {test_config['file']}")
            continue
        
        # Extract test info
        test_info = extract_test_info(file_path, function)
        
        # Build description
        description = build_description(test_id, test_info, test_config['file'], function, category)
        descriptions[test_id] = description
        
        print(f"OK: Generated description for {test_id} ({len(description)} chars)")
    
    # Save to file
    output_file = project_root / 'scripts/jira/alert_tests_descriptions.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        for test_id, desc in descriptions.items():
            f.write(f"\n{'='*80}\n")
            f.write(f"TEST: {test_id}\n")
            f.write(f"{'='*80}\n\n")
            f.write(desc)
            f.write("\n\n")
    
    print(f"\nOK: Saved all descriptions to: {output_file}")
    print(f"Total tests: {len(descriptions)}")


if __name__ == "__main__":
    main()

