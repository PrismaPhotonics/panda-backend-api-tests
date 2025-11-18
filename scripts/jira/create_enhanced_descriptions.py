"""
Create enhanced descriptions with actual values extracted from test code.
"""

import re
import ast
from pathlib import Path
from typing import Dict, Any, List

project_root = Path(__file__).parent.parent.parent

TEST_FILES = {
    'positive': project_root / 'be_focus_server_tests/integration/alerts/test_alert_generation_positive.py',
    'negative': project_root / 'be_focus_server_tests/integration/alerts/test_alert_generation_negative.py',
    'edge_cases': project_root / 'be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py',
    'load': project_root / 'be_focus_server_tests/integration/alerts/test_alert_generation_load.py',
    'performance': project_root / 'be_focus_server_tests/integration/alerts/test_alert_generation_performance.py',
}

def extract_actual_values(file_path: Path, test_function: str) -> Dict[str, Any]:
    """Extract actual test values from code."""
    content = file_path.read_text(encoding='utf-8')
    
    # Find function
    func_pattern = rf'def {test_function}\(.*?\):.*?(?=\n    @|\n    def |\Z)'
    func_match = re.search(func_pattern, content, re.DOTALL)
    
    if not func_match:
        return {}
    
    func_code = func_match.group(0)
    
    values = {}
    
    # Extract alert payload values
    payload_pattern = r'alert_payload\s*=\s*\{([^}]+)\}'
    payload_match = re.search(payload_pattern, func_code, re.DOTALL)
    if payload_match:
        payload_str = payload_match.group(1)
        # Extract key-value pairs
        for line in payload_str.split('\n'):
            if ':' in line and not line.strip().startswith('#'):
                # Match: "key": value or 'key': value
                kv_match = re.search(r'["\']?(\w+)["\']?\s*:\s*(.+?)(?:,|$)', line)
                if kv_match:
                    key = kv_match.group(1)
                    value = kv_match.group(2).strip().rstrip(',').strip()
                    # Clean value
                    value = re.sub(r'f?"([^"]+)"', r'\1', value)  # Remove f-string quotes
                    value = re.sub(r'f?\'([^\']+)\'', r'\1', value)
                    value = re.sub(r'f?"([^"]+)"', r'\1', value)
                    value = value.strip('"\'')
                    if value:
                        values[key] = value
    
    # Extract test parameters
    num_match = re.search(r'num_alerts\s*=\s*(\d+)', func_code)
    if num_match:
        values['num_alerts'] = num_match.group(1)
    
    duration_match = re.search(r'duration_seconds\s*=\s*(\d+)', func_code)
    if duration_match:
        values['duration'] = duration_match.group(1)
    
    burst_match = re.search(r'burst_size\s*=\s*(\d+)', func_code)
    if burst_match:
        values['burst_size'] = burst_match.group(1)
    
    return values

def build_enhanced_description(test_id: str, category: str, test_function: str,
                               file_path: Path, docstring: str, values: Dict[str, Any]) -> str:
    """Build enhanced description with actual values."""
    
    category_names = {
        'positive': 'Positive',
        'negative': 'Negative',
        'edge_cases': 'Edge Case',
        'load': 'Load',
        'performance': 'Performance'
    }
    
    category_name = category_names.get(category, category.title())
    file_rel = str(file_path.relative_to(project_root)).replace('\\', '/')
    
    # Extract from docstring
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
            step_matches = re.findall(r'\d+\.\s*(.+?)(?=\d+\.|$)', steps_text, re.DOTALL)
            steps = [s.strip() for s in step_matches]
    
    if 'Expected:' in docstring:
        exp_match = re.search(r'Expected:\s*(.*?)$', docstring, re.DOTALL)
        if exp_match:
            expected = exp_match.group(1).strip()
    
    # Build description
    parts = []
    
    # Objective
    parts.append("h2. Objective")
    parts.append(objective if objective else f"Verify alert generation for {category_name.lower()} scenarios.")
    parts.append("")
    
    # Test Details
    parts.append("h2. Test Details")
    parts.append(f"* *Test ID:* {test_id}")
    parts.append(f"* *Test Type:* Integration Test")
    parts.append(f"* *Category:* {category_name}")
    parts.append(f"* *Test File:* {{code}}{file_rel}{{code}}")
    parts.append(f"* *Test Function:* {{code}}{test_function}{{code}}")
    parts.append("")
    
    # Prerequisites
    parts.append("h2. Prerequisites")
    parts.append("* Focus Server API is available and healthy")
    parts.append("* Backend system is running and accessible")
    parts.append("* Valid configuration manager with API credentials")
    if 'rabbitmq' in test_function.lower() or category in ['load', 'performance']:
        parts.append("* RabbitMQ is accessible and configured")
    parts.append("")
    
    # Test Data with actual values
    parts.append("h2. Test Data")
    
    # Extract actual values
    class_id = values.get('classId') or values.get('class_id', '104')
    dof = values.get('dofM') or values.get('dof_m', '5000')
    severity = values.get('severity', '3')
    alerts_amount = values.get('alertsAmount', '1')
    
    if class_id == '104':
        alert_type = 'SD (Spatial Distribution)'
    elif class_id == '103':
        alert_type = 'SC (Single Channel)'
    else:
        alert_type = 'SD (Spatial Distribution)'
    
    severity_names = {'1': 'Low', '2': 'Medium', '3': 'High'}
    severity_name = severity_names.get(str(severity), 'High')
    
    parts.append(f"* *Alert Type:* {alert_type}")
    parts.append(f"* *Class ID:* {class_id}")
    parts.append(f"* *DOF (Distance on Fiber):* {dof} meters")
    parts.append(f"* *Severity:* {severity} ({severity_name})")
    parts.append(f"* *Alerts Amount:* {alerts_amount}")
    
    # Add test-specific parameters
    if values.get('num_alerts'):
        parts.append(f"* *Number of Alerts:* {values['num_alerts']}")
    if values.get('duration'):
        parts.append(f"* *Test Duration:* {values['duration']} seconds ({int(values['duration'])/60:.1f} minutes)")
    if values.get('burst_size'):
        parts.append(f"* *Burst Size:* {values['burst_size']} alerts")
    
    parts.append("")
    
    # Test Steps with actual data
    parts.append("h2. Test Steps")
    parts.append("")
    parts.append("|| # || Action || Test Data || Expected Result ||")
    
    if steps:
        for i, step in enumerate(steps, 1):
            # Extract data from step
            data = ""
            if 'classId' in step.lower() or 'class_id' in step.lower():
                data = f"classId={class_id}"
            elif 'severity' in step.lower():
                data = f"severity={severity}"
            elif 'DOF' in step or 'dof' in step.lower():
                data = f"dofM={dof}"
            elif 'multiple' in step.lower() or 'alerts' in step.lower():
                if values.get('num_alerts'):
                    data = f"{values['num_alerts']} alerts"
            
            # Determine expected result based on category
            if category == 'negative':
                expected_result = "HTTP 400/422 or error response"
            elif category == 'edge_case':
                expected_result = "Alert processed correctly"
            elif category == 'load':
                expected_result = f"Success rate >= 99%"
            elif category == 'performance':
                expected_result = "Meets performance requirements"
            else:
                expected_result = "HTTP 200/201, alert sent successfully"
            
            parts.append(f"| {i} | {step} | {data} | {expected_result} |")
    else:
        # Default steps
        parts.append(f"| 1 | Create alert payload | classId={class_id}, dofM={dof}, severity={severity} | Payload created |")
        parts.append("| 2 | Send alert via HTTP API | POST to push-to-rabbit endpoint | HTTP 200/201 |")
        parts.append("| 3 | Verify response | Check status code and response body | Valid response |")
    
    parts.append("")
    
    # Expected Result
    parts.append("h2. Expected Result")
    if expected:
        parts.append(expected)
    else:
        if category == 'negative':
            parts.append("Alert is rejected with appropriate error message (HTTP 400/422).")
        elif category == 'load':
            parts.append("System handles load successfully with >= 99% success rate.")
        elif category == 'performance':
            parts.append("Performance metrics meet specified requirements.")
        else:
            parts.append(f"Alert is successfully generated and processed.")
    
    # Add specific requirements
    if category == 'load' and values.get('num_alerts'):
        parts.append(f"* Successfully process {values['num_alerts']} alerts")
        parts.append("* No system degradation or failures")
    elif category == 'performance':
        if 'response_time' in test_function:
            parts.append("* Mean response time < 100ms")
            parts.append("* P95 response time < 200ms")
            parts.append("* P99 response time < 500ms")
        elif 'throughput' in test_function:
            parts.append("* Throughput >= 100 alerts/second")
        elif 'latency' in test_function:
            parts.append("* Mean latency < 50ms")
            parts.append("* P95 latency < 100ms")
        elif 'resource' in test_function:
            parts.append("* CPU usage < 80%")
            parts.append("* Memory increase < 500MB")
    
    parts.append("")
    
    # Post-Conditions
    parts.append("h2. Post-Conditions")
    parts.append("* Alert is sent to RabbitMQ queue (if applicable)")
    parts.append("* System remains stable and operational")
    parts.append("* No resource leaks or performance degradation")
    if category in ['load', 'performance']:
        parts.append("* System metrics within acceptable ranges")
    parts.append("")
    
    # Automation Status
    parts.append("h2. Automation Status")
    parts.append("✅ *Automated* with Pytest")
    parts.append("")
    parts.append(f"*Test Function:* {{code}}{test_function}{{code}}")
    parts.append(f"*Test File:* {{code}}{file_rel}{{code}}")
    parts.append("")
    parts.append("*Execution Command:*")
    
    # Build execution command
    class_name = None
    if 'TestAlertGeneration' in content:
        class_match = re.search(r'class\s+(\w+).*?def\s+' + test_function, content)
        if class_match:
            class_name = class_match.group(1)
    
    if class_name:
        cmd = f"pytest {file_rel}::{class_name}::{test_function} -v"
    else:
        cmd = f"pytest {file_rel}::{test_function} -v"
    
    parts.append(f"{{code}}{cmd}{{code}}")
    
    return "\n".join(parts)

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
    """Generate enhanced descriptions."""
    enhanced_descriptions = {}
    
    for test_id, test_config in TESTS.items():
        file_key = test_config['file']
        function = test_config['function']
        file_path = TEST_FILES[file_key]
        
        if not file_path.exists():
            print(f"WARNING: File not found: {file_path}")
            continue
        
        content = file_path.read_text(encoding='utf-8')
        
        # Extract docstring
        docstring = ''
        func_pattern = rf'def {function}\(.*?\):\s*"""(.*?)"""'
        doc_match = re.search(func_pattern, content, re.DOTALL)
        if doc_match:
            docstring = doc_match.group(1)
        
        # Extract actual values
        values = extract_actual_values(file_path, function)
        
        # Build enhanced description
        description = build_enhanced_description(
            test_id, file_key, function, file_path, docstring, values
        )
        
        enhanced_descriptions[test_id] = description
        print(f"Generated enhanced description for {test_id}")
    
    # Save to file
    output_file = project_root / 'scripts/jira/enhanced_test_descriptions.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        for test_id, desc in sorted(enhanced_descriptions.items()):
            f.write(f"\n{'='*80}\n")
            f.write(f"TEST: {test_id}\n")
            f.write(f"{'='*80}\n\n")
            f.write(desc)
            f.write("\n\n")
    
    print(f"\nSaved {len(enhanced_descriptions)} enhanced descriptions to {output_file}")
    return enhanced_descriptions

if __name__ == "__main__":
    main()

