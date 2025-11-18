"""
Generate improved test descriptions for all Alert Generation Xray test cases.
Extracts detailed information from test code and creates comprehensive descriptions.
"""

import re
from pathlib import Path
from typing import Dict, Any

project_root = Path(__file__).parent.parent.parent

# Test file paths
TEST_FILES = {
    'positive': project_root / 'be_focus_server_tests/integration/alerts/test_alert_generation_positive.py',
    'negative': project_root / 'be_focus_server_tests/integration/alerts/test_alert_generation_negative.py',
    'edge_cases': project_root / 'be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py',
    'load': project_root / 'be_focus_server_tests/integration/alerts/test_alert_generation_load.py',
    'performance': project_root / 'be_focus_server_tests/integration/alerts/test_alert_generation_performance.py',
}

def extract_test_details(file_path: Path, test_function: str) -> Dict[str, Any]:
    """Extract detailed information from test function."""
    content = file_path.read_text(encoding='utf-8')
    
    # Find the test function
    pattern = rf'def {test_function}\(.*?\):\s*"""(.*?)"""'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        return {}
    
    docstring = match.group(1)
    
    # Extract test code
    func_start = content.find(f'def {test_function}')
    if func_start == -1:
        return {}
    
    # Find function body
    indent_level = 0
    func_end = func_start
    for i in range(func_start, len(content)):
        if content[i] == '\n':
            # Check indentation
            j = i + 1
            while j < len(content) and content[j] in ' \t':
                j += 1
            if j < len(content) and content[j] != '\n':
                next_indent = len(content[i+1:j]) - len(content[i+1:j].lstrip())
                if indent_level == 0:
                    indent_level = next_indent
                elif next_indent <= indent_level and content[j] not in ' \t\n':
                    # Found next function or class
                    func_end = i
                    break
    
    func_code = content[func_start:func_end]
    
    # Extract payload values
    payload_values = {}
    payload_match = re.search(r'alert_payload\s*=\s*\{([^}]+)\}', func_code, re.DOTALL)
    if payload_match:
        payload_str = payload_match.group(1)
        # Extract key-value pairs
        for line in payload_str.split('\n'):
            if ':' in line:
                key_match = re.search(r'["\']?(\w+)["\']?\s*:\s*(.+)', line)
                if key_match:
                    key = key_match.group(1)
                    value = key_match.group(2).strip().rstrip(',').strip('"\'')
                    payload_values[key] = value
    
    # Extract test parameters
    num_alerts_match = re.search(r'num_alerts\s*=\s*(\d+)', func_code)
    num_alerts = num_alerts_match.group(1) if num_alerts_match else None
    
    duration_match = re.search(r'duration_seconds\s*=\s*(\d+)', func_code)
    duration = duration_match.group(1) if duration_match else None
    
    # Extract assertions/requirements
    requirements = []
    assert_matches = re.findall(r'assert\s+([^,\n]+)', func_code)
    for assert_match in assert_matches:
        if 'time' in assert_match.lower() or 'rate' in assert_match.lower():
            requirements.append(assert_match.strip())
    
    return {
        'docstring': docstring,
        'payload_values': payload_values,
        'num_alerts': num_alerts,
        'duration': duration,
        'requirements': requirements
    }

def build_improved_description(test_id: str, category: str, test_function: str, 
                               file_path: Path, test_details: Dict[str, Any]) -> str:
    """Build improved description with better formatting."""
    
    # Category mapping
    category_names = {
        'positive': 'Positive',
        'negative': 'Negative',
        'edge_cases': 'Edge Case',
        'load': 'Load',
        'performance': 'Performance'
    }
    
    category_name = category_names.get(category, category.title())
    
    # Extract docstring sections
    docstring = test_details.get('docstring', '')
    objective = ''
    steps = []
    expected = ''
    
    if 'Objective:' in docstring:
        obj_match = re.search(r'Objective:\s*(.*?)(?:\n\s*Steps:|$)', docstring, re.DOTALL)
        if obj_match:
            objective = obj_match.group(1).strip()
    
    if 'Steps:' in docstring:
        steps_match = re.search(r'Steps:\s*(.*?)(?:\n\s*Expected:|$)', docstring, re.DOTALL)
        if steps_match:
            steps_text = steps_match.group(1)
            # Extract numbered steps
            step_matches = re.findall(r'\d+\.\s*(.+?)(?=\d+\.|$)', steps_text, re.DOTALL)
            steps = [s.strip() for s in step_matches]
    
    if 'Expected:' in docstring:
        exp_match = re.search(r'Expected:\s*(.*?)$', docstring, re.DOTALL)
        if exp_match:
            expected = exp_match.group(1).strip()
    
    # Get payload values
    payload = test_details.get('payload_values', {})
    
    # Build description
    desc_parts = []
    
    # Header
    desc_parts.append(f"h2. Objective")
    desc_parts.append(objective if objective else f"Verify alert generation functionality for {category_name.lower()} scenarios.")
    desc_parts.append("")
    
    # Test Details Section
    desc_parts.append("h2. Test Details")
    desc_parts.append(f"* *Test ID:* {test_id}")
    desc_parts.append(f"* *Test Type:* Integration Test")
    desc_parts.append(f"* *Category:* {category_name}")
    desc_parts.append(f"* *Test File:* {{code}}{file_path.relative_to(project_root)}{{code}}")
    desc_parts.append(f"* *Test Function:* {{code}}{test_function}{{code}}")
    desc_parts.append("")
    
    # Prerequisites
    desc_parts.append("h2. Prerequisites")
    desc_parts.append("* Focus Server API is available and healthy")
    desc_parts.append("* Backend system is running and accessible")
    desc_parts.append("* Valid configuration manager with API credentials")
    desc_parts.append("* RabbitMQ is accessible (for RabbitMQ-related tests)")
    desc_parts.append("")
    
    # Test Data
    desc_parts.append("h2. Test Data")
    if payload:
        if 'classId' in payload or 'class_id' in payload:
            class_id = payload.get('classId') or payload.get('class_id', '104')
            class_name = 'SD (Spatial Distribution)' if str(class_id) == '104' else 'SC (Single Channel)'
            desc_parts.append(f"* *Alert Type:* {class_name}")
            desc_parts.append(f"* *Class ID:* {class_id}")
        if 'dofM' in payload or 'dof_m' in payload:
            dof = payload.get('dofM') or payload.get('dof_m', '5000')
            desc_parts.append(f"* *DOF (Distance on Fiber):* {dof} meters")
        if 'severity' in payload:
            severity = payload.get('severity', '3')
            severity_name = {'1': 'Low', '2': 'Medium', '3': 'High'}.get(str(severity), 'High')
            desc_parts.append(f"* *Severity:* {severity} ({severity_name})")
        if 'alertsAmount' in payload:
            desc_parts.append(f"* *Alerts Amount:* {payload.get('alertsAmount', '1')}")
    else:
        desc_parts.append("* *Alert Type:* SD (Spatial Distribution)")
        desc_parts.append("* *Class ID:* 104")
        desc_parts.append("* *DOF (Distance on Fiber):* 5000 meters")
        desc_parts.append("* *Severity:* 3 (High)")
    desc_parts.append("")
    
    # Test Steps
    desc_parts.append("h2. Test Steps")
    desc_parts.append("")
    desc_parts.append("|| # || Action || Test Data || Expected Result ||")
    
    if steps:
        for i, step in enumerate(steps, 1):
            # Extract data from step if mentioned
            data = ""
            if 'classId' in step or 'class_id' in step:
                data = "classId=104 (SD) or 103 (SC)"
            elif 'severity' in step.lower():
                data = "severity=1,2,3"
            elif 'DOF' in step or 'dof' in step:
                data = "dofM=0-2222"
            
            desc_parts.append(f"| {i} | {step} | {data} | Success / No errors |")
    else:
        desc_parts.append("| 1 | Create alert payload with test data | See Test Data section | Payload created |")
        desc_parts.append("| 2 | Send alert via HTTP API | POST to push-to-rabbit endpoint | HTTP 200/201 |")
        desc_parts.append("| 3 | Verify response | Check status code and response body | Valid response |")
    
    desc_parts.append("")
    
    # Expected Result
    desc_parts.append("h2. Expected Result")
    if expected:
        desc_parts.append(expected)
    else:
        desc_parts.append(f"Alert is successfully generated and processed according to {category_name.lower()} scenario requirements.")
    
    # Add specific requirements if available
    requirements = test_details.get('requirements', [])
    if requirements:
        desc_parts.append("")
        desc_parts.append("*Requirements:*")
        for req in requirements[:3]:  # Limit to 3 requirements
            desc_parts.append(f"* {req}")
    
    desc_parts.append("")
    
    # Post-Conditions
    desc_parts.append("h2. Post-Conditions")
    desc_parts.append("* Alert is sent to RabbitMQ queue (if applicable)")
    desc_parts.append("* System remains stable and operational")
    desc_parts.append("* No resource leaks or performance degradation")
    desc_parts.append("")
    
    # Automation Status
    desc_parts.append("h2. Automation Status")
    desc_parts.append("✅ *Automated* with Pytest")
    desc_parts.append("")
    desc_parts.append(f"*Test Function:* {{code}}{test_function}{{code}}")
    desc_parts.append(f"*Test File:* {{code}}{file_path.relative_to(project_root)}{{code}}")
    desc_parts.append("")
    desc_parts.append(f"*Execution Command:*")
    file_rel_path = str(file_path.relative_to(project_root)).replace('\\', '/')
    desc_parts.append(f"{{code}}pytest {file_rel_path}::{test_function} -v{{code}}")
    
    return "\n".join(desc_parts)

# Test mappings
TESTS = {
    'PZ-14933': {'file': 'positive', 'function': 'test_successful_sd_alert_generation'},
    'PZ-14934': {'file': 'positive', 'function': 'test_successful_sc_alert_generation'},
    'PZ-14935': {'file': 'positive', 'function': 'test_multiple_alerts_generation'},
    'PZ-14936': {'file': 'positive', 'function': 'test_different_severity_levels'},
    'PZ-14937': {'file': 'positive', 'function': 'test_alert_processing_via_rabbitmq'},
    'PZ-14938': {'file': 'negative', 'function': 'test_invalid_class_id'},
    'PZ-14939': {'file': 'negative', 'function': 'test_invalid_severity'},
    'PZ-14940': {'file': 'negative', 'function': 'test_invalid_dof_range'},
    'PZ-14941': {'file': 'negative', 'function': 'test_missing_required_fields'},
    'PZ-14942': {'file': 'negative', 'function': 'test_rabbitmq_connection_failure'},
    'PZ-14943': {'file': 'negative', 'function': 'test_invalid_alert_id_format'},
    'PZ-14944': {'file': 'negative', 'function': 'test_duplicate_alert_ids'},
    'PZ-14945': {'file': 'edge_cases', 'function': 'test_boundary_dof_values'},
    'PZ-14946': {'file': 'edge_cases', 'function': 'test_min_max_severity'},
    'PZ-14947': {'file': 'edge_cases', 'function': 'test_zero_alerts_amount'},
    'PZ-14948': {'file': 'edge_cases', 'function': 'test_very_large_alert_id'},
    'PZ-14949': {'file': 'edge_cases', 'function': 'test_concurrent_alerts_same_dof'},
    'PZ-14950': {'file': 'edge_cases', 'function': 'test_rapid_sequential_alerts'},
    'PZ-14951': {'file': 'edge_cases', 'function': 'test_alert_maximum_fields'},
    'PZ-14952': {'file': 'edge_cases', 'function': 'test_alert_minimum_fields'},
    'PZ-14953': {'file': 'load', 'function': 'test_high_volume_load'},
    'PZ-14954': {'file': 'load', 'function': 'test_sustained_load'},
    'PZ-14955': {'file': 'load', 'function': 'test_burst_load'},
    'PZ-14956': {'file': 'load', 'function': 'test_mixed_alert_types_load'},
    'PZ-14957': {'file': 'load', 'function': 'test_rabbitmq_queue_capacity'},
    'PZ-14958': {'file': 'performance', 'function': 'test_alert_response_time'},
    'PZ-14959': {'file': 'performance', 'function': 'test_alert_throughput'},
    'PZ-14960': {'file': 'performance', 'function': 'test_alert_latency'},
    'PZ-14961': {'file': 'performance', 'function': 'test_resource_usage'},
    'PZ-14962': {'file': 'performance', 'function': 'test_end_to_end_performance'},
    'PZ-14963': {'file': 'performance', 'function': 'test_rabbitmq_performance'},
}

def main():
    """Generate improved descriptions for all tests."""
    descriptions = {}
    
    for test_id, test_config in TESTS.items():
        file_key = test_config['file']
        function = test_config['function']
        file_path = TEST_FILES[file_key]
        
        if not file_path.exists():
            print(f"WARNING: File not found: {file_path}")
            continue
        
        # Extract test details
        test_details = extract_test_details(file_path, function)
        
        # Build improved description
        description = build_improved_description(
            test_id, file_key, function, file_path, test_details
        )
        
        descriptions[test_id] = description
        print(f"Generated description for {test_id}")
    
    # Save to file
    output_file = project_root / 'scripts/jira/improved_test_descriptions.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        for test_id, desc in sorted(descriptions.items()):
            f.write(f"\n{'='*80}\n")
            f.write(f"TEST: {test_id}\n")
            f.write(f"{'='*80}\n\n")
            f.write(desc)
            f.write("\n\n")
    
    print(f"\nSaved {len(descriptions)} improved descriptions to {output_file}")
    return descriptions

if __name__ == "__main__":
    main()

