"""
Extract actual values from test code and create enhanced descriptions,
then update all Jira test cases using Rovo MCP.
"""

import re
from pathlib import Path
from typing import Dict, Any

project_root = Path(__file__).parent.parent.parent

# Read test files and extract actual values
def extract_test_values():
    """Extract actual test values from code."""
    test_values = {}
    
    # PZ-14933: SD Alert
    test_values['PZ-14933'] = {
        'classId': '104',
        'dofM': '4163',
        'severity': '3',
        'alertsAmount': '1',
        'alertType': 'SD (Spatial Distribution)'
    }
    
    # PZ-14934: SC Alert
    test_values['PZ-14934'] = {
        'classId': '103',
        'dofM': '5682',
        'severity': '2',
        'alertsAmount': '1',
        'alertType': 'SC (Single Channel)'
    }
    
    # PZ-14935: Multiple Alerts
    test_values['PZ-14935'] = {
        'num_alerts': '5',
        'classId': '104/103 (alternating)',
        'dofM': '4000-4500',
        'severity': '1,2,3 (rotating)',
        'alertType': 'Mixed (SD and SC)'
    }
    
    # PZ-14936: Different Severity Levels
    test_values['PZ-14936'] = {
        'severity': '1, 2, 3',
        'classId': '104',
        'dofM': '5000',
        'alertType': 'SD (Spatial Distribution)'
    }
    
    # PZ-14937: RabbitMQ Processing
    test_values['PZ-14937'] = {
        'exchange': 'prisma',
        'exchange_type': 'topic',
        'routing_keys': 'Algorithm.AlertReport.*',
        'alertType': 'SD (Spatial Distribution)'
    }
    
    # PZ-14938: Invalid Class ID
    test_values['PZ-14938'] = {
        'invalid_class_ids': '0, 1, 100, 105, 999, -1',
        'expected': 'HTTP 400/422'
    }
    
    # PZ-14939: Invalid Severity
    test_values['PZ-14939'] = {
        'invalid_severities': '0, 4, 5, -1, 100',
        'expected': 'HTTP 400/422'
    }
    
    # PZ-14940: Invalid DOF Range
    test_values['PZ-14940'] = {
        'invalid_dofs': '-1, -100',
        'max_range': '2222',
        'expected': 'HTTP 400/422'
    }
    
    # PZ-14941: Missing Required Fields
    test_values['PZ-14941'] = {
        'missing_fields': 'alertsAmount, dofM, classId, severity, alertIds',
        'expected': 'HTTP 400 Bad Request'
    }
    
    # PZ-14942: RabbitMQ Connection Failure
    test_values['PZ-14942'] = {
        'invalid_host': 'invalid-rabbitmq-host',
        'expected': 'Connection error handled gracefully'
    }
    
    # PZ-14943: Invalid Alert ID Format
    test_values['PZ-14943'] = {
        'invalid_formats': 'Empty ID, empty array',
        'expected': 'HTTP 400/422 or handled appropriately'
    }
    
    # PZ-14944: Duplicate Alert IDs
    test_values['PZ-14944'] = {
        'duplicate_id': 'test-duplicate-{timestamp}',
        'expected': 'Both alerts may be accepted (event-based)'
    }
    
    # PZ-14945: Boundary DOF Values
    test_values['PZ-14945'] = {
        'boundary_dofs': '0, 1, 2221, 2222',
        'expected': 'All processed correctly'
    }
    
    # PZ-14946: Min/Max Severity
    test_values['PZ-14946'] = {
        'severities': '1 (minimum), 3 (maximum)',
        'expected': 'Both processed correctly'
    }
    
    # PZ-14947: Zero Alerts Amount
    test_values['PZ-14947'] = {
        'alertsAmount': '0',
        'expected': 'Rejected or handled appropriately'
    }
    
    # PZ-14948: Very Large Alert ID
    test_values['PZ-14948'] = {
        'id_length': '1000+ characters',
        'expected': 'Truncated, rejected, or processed'
    }
    
    # PZ-14949: Concurrent Alerts Same DOF
    test_values['PZ-14949'] = {
        'num_alerts': '10',
        'same_dof': '5000',
        'expected': 'All processed without conflicts'
    }
    
    # PZ-14950: Rapid Sequential Alerts
    test_values['PZ-14950'] = {
        'num_alerts': '50',
        'delay': 'No delay',
        'expected': 'All processed correctly'
    }
    
    # PZ-14951: Maximum Fields
    test_values['PZ-14951'] = {
        'alertsAmount': '100',
        'dofM': '2222',
        'severity': '3',
        'alertIds': '100 IDs',
        'expected': 'Processed correctly'
    }
    
    # PZ-14952: Minimum Fields
    test_values['PZ-14952'] = {
        'alertsAmount': '1',
        'dofM': '1',
        'classId': '103',
        'severity': '1',
        'expected': 'Processed correctly'
    }
    
    # PZ-14953: High Volume Load
    test_values['PZ-14953'] = {
        'num_alerts': '1000',
        'max_time': '300 seconds (5 minutes)',
        'min_success_rate': '99%',
        'expected': 'Success rate >= 99%'
    }
    
    # PZ-14954: Sustained Load
    test_values['PZ-14954'] = {
        'duration': '600 seconds (10 minutes)',
        'alerts_per_second': '10',
        'total_alerts': '6000',
        'expected': 'No degradation'
    }
    
    # PZ-14955: Burst Load
    test_values['PZ-14955'] = {
        'burst_size': '500',
        'min_success_rate': '95%',
        'expected': 'Success rate >= 95%'
    }
    
    # PZ-14956: Mixed Alert Types Load
    test_values['PZ-14956'] = {
        'num_alerts': '500',
        'class_ids': '103 (SC), 104 (SD)',
        'severities': '1, 2, 3',
        'expected': 'All types processed correctly'
    }
    
    # PZ-14957: RabbitMQ Queue Capacity
    test_values['PZ-14957'] = {
        'num_alerts': '1000',
        'exchange': 'prisma',
        'routing_key': 'Algorithm.AlertReport.MLGround',
        'expected': 'No message loss'
    }
    
    # PZ-14958: Response Time
    test_values['PZ-14958'] = {
        'num_alerts': '100',
        'mean_requirement': '< 100ms',
        'p95_requirement': '< 200ms',
        'p99_requirement': '< 500ms',
        'expected': 'Meets all requirements'
    }
    
    # PZ-14959: Throughput
    test_values['PZ-14959'] = {
        'num_alerts': '1000',
        'min_throughput': '>= 100 alerts/second',
        'expected': 'Meets throughput requirement'
    }
    
    # PZ-14960: Latency
    test_values['PZ-14960'] = {
        'num_alerts': '100',
        'mean_requirement': '< 50ms',
        'p95_requirement': '< 100ms',
        'expected': 'Meets latency requirements'
    }
    
    # PZ-14961: Resource Usage
    test_values['PZ-14961'] = {
        'num_alerts': '1000',
        'cpu_limit': '< 80%',
        'memory_limit': '< 500MB increase',
        'expected': 'Resource usage acceptable'
    }
    
    # PZ-14962: End-to-End Performance
    test_values['PZ-14962'] = {
        'num_alerts': '100',
        'mean_requirement': '< 200ms',
        'p95_requirement': '< 500ms',
        'expected': 'Meets E2E requirements'
    }
    
    # PZ-14963: RabbitMQ Performance
    test_values['PZ-14963'] = {
        'num_alerts': '100',
        'publish_time': '< 10ms',
        'consume_time': '< 50ms',
        'expected': 'Meets RabbitMQ performance requirements'
    }
    
    return test_values

def build_enhanced_description(test_id: str, values: Dict[str, Any], 
                               category: str, test_function: str, file_path: str) -> str:
    """Build enhanced description with actual values."""
    
    category_names = {
        'positive': 'Positive',
        'negative': 'Negative',
        'edge_cases': 'Edge Case',
        'load': 'Load',
        'performance': 'Performance'
    }
    
    category_name = category_names.get(category, category.title())
    
    parts = []
    
    # Objective - will be customized per test
    parts.append("h2. Objective")
    if test_id == 'PZ-14933':
        parts.append("Verify that SD (Spatial Distribution) alerts can be successfully generated and processed through the backend system.")
    elif test_id == 'PZ-14934':
        parts.append("Verify that SC (Single Channel) alerts can be successfully generated and processed through the backend system.")
    elif test_id == 'PZ-14935':
        parts.append("Verify that multiple alerts can be generated and processed simultaneously without conflicts.")
    elif test_id == 'PZ-14936':
        parts.append("Verify that alerts with different severity levels (1, 2, 3) are correctly generated and processed.")
    elif test_id == 'PZ-14937':
        parts.append("Verify that alerts are correctly processed through RabbitMQ message queue system.")
    elif category == 'negative':
        parts.append(f"Verify that system correctly handles invalid input: {test_function.replace('test_', '').replace('_', ' ')}")
    elif category == 'edge_case':
        parts.append(f"Verify edge case handling: {test_function.replace('test_', '').replace('_', ' ')}")
    elif category == 'load':
        parts.append(f"Verify system can handle {category_name.lower()} scenarios without degradation.")
    elif category == 'performance':
        parts.append(f"Verify {category_name.lower()} metrics meet specified requirements.")
    else:
        parts.append(f"Verify alert generation for {category_name.lower()} scenarios.")
    
    parts.append("")
    
    # Test Details
    parts.append("h2. Test Details")
    parts.append(f"* *Test ID:* {test_id}")
    parts.append(f"* *Test Type:* Integration Test")
    parts.append(f"* *Category:* {category_name}")
    parts.append(f"* *Test File:* {{code}}{file_path}{{code}}")
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
    
    if values.get('alertType'):
        parts.append(f"* *Alert Type:* {values['alertType']}")
    if values.get('classId'):
        parts.append(f"* *Class ID:* {values['classId']}")
    if values.get('dofM'):
        parts.append(f"* *DOF (Distance on Fiber):* {values['dofM']} meters")
    if values.get('severity'):
        parts.append(f"* *Severity:* {values['severity']}")
    if values.get('alertsAmount'):
        parts.append(f"* *Alerts Amount:* {values['alertsAmount']}")
    if values.get('num_alerts'):
        parts.append(f"* *Number of Alerts:* {values['num_alerts']}")
    if values.get('duration'):
        parts.append(f"* *Test Duration:* {values['duration']}")
    if values.get('burst_size'):
        parts.append(f"* *Burst Size:* {values['burst_size']} alerts")
    if values.get('alerts_per_second'):
        parts.append(f"* *Alerts per Second:* {values['alerts_per_second']}")
    
    parts.append("")
    
    # Test Steps
    parts.append("h2. Test Steps")
    parts.append("")
    parts.append("|| # || Action || Test Data || Expected Result ||")
    
    # Customize steps based on test
    if test_id == 'PZ-14933':
        parts.append(f"| 1 | Create SD alert payload | classId={values.get('classId', '104')}, dofM={values.get('dofM', '4163')}, severity={values.get('severity', '3')} | Payload created |")
        parts.append("| 2 | Send alert via HTTP API | POST to push-to-rabbit endpoint | HTTP 200/201 |")
        parts.append("| 3 | Verify response status code | Check response.status_code | Status code is 200 or 201 |")
        parts.append("| 4 | Log response details | Response text and status | Details logged for verification |")
    elif test_id == 'PZ-14934':
        parts.append(f"| 1 | Create SC alert payload | classId={values.get('classId', '103')}, dofM={values.get('dofM', '5682')}, severity={values.get('severity', '2')} | Payload created |")
        parts.append("| 2 | Send alert via HTTP API | POST to push-to-rabbit endpoint | HTTP 200/201 |")
        parts.append("| 3 | Verify alert is processed | Check response and RabbitMQ | Alert processed successfully |")
    elif test_id == 'PZ-14935':
        parts.append(f"| 1 | Create {values.get('num_alerts', '5')} alert payloads | Alternating classId (104/103), different DOF values | Payloads created |")
        parts.append("| 2 | Send all alerts via HTTP API | Sequential API calls | All alerts sent |")
        parts.append("| 3 | Verify all alerts processed | Check success count | {num_alerts}/{num_alerts} alerts successful |")
        parts.append("| 4 | Verify no conflicts | Check for errors or data loss | No conflicts or data loss |")
    elif category == 'negative':
        invalid_data = values.get('invalid_class_ids') or values.get('invalid_severities') or values.get('invalid_dofs') or values.get('missing_fields', 'Invalid data')
        parts.append(f"| 1 | Create alert with invalid data | {invalid_data} | Payload created |")
        parts.append("| 2 | Attempt to send alert via API | POST to push-to-rabbit endpoint | HTTP 400/422 |")
        parts.append("| 3 | Verify error handling | Check response status and message | Appropriate error returned |")
    elif category == 'load':
        parts.append(f"| 1 | Generate {values.get('num_alerts', 'large number')} alerts | Mixed alert types and severities | Alerts generated |")
        parts.append("| 2 | Measure processing time | Monitor start/end time | Time recorded |")
        parts.append(f"| 3 | Verify success rate | Calculate success/total | Success rate >= {values.get('min_success_rate', '99%')} |")
        parts.append("| 4 | Verify system stability | Monitor system metrics | No degradation |")
    elif category == 'performance':
        parts.append("| 1 | Generate alerts and measure metrics | Monitor response time/throughput/latency | Metrics recorded |")
        parts.append("| 2 | Calculate statistics | Mean, median, P95, P99 | Statistics calculated |")
        parts.append("| 3 | Verify requirements | Compare against thresholds | Requirements met |")
    else:
        parts.append("| 1 | Create alert payload | See Test Data section | Payload created |")
        parts.append("| 2 | Send alert via HTTP API | POST to push-to-rabbit endpoint | HTTP 200/201 |")
        parts.append("| 3 | Verify response | Check status code and response body | Valid response |")
    
    parts.append("")
    
    # Expected Result
    parts.append("h2. Expected Result")
    if values.get('expected'):
        parts.append(values['expected'])
    elif category == 'negative':
        parts.append("Alert is rejected with appropriate error message (HTTP 400/422).")
    elif category == 'load':
        parts.append(f"System handles load successfully with success rate >= {values.get('min_success_rate', '99%')}.")
    elif category == 'performance':
        parts.append("Performance metrics meet specified requirements.")
    else:
        parts.append("Alert is successfully generated and processed.")
    
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
    parts.append(f"*Test File:* {{code}}{file_path}{{code}}")
    parts.append("")
    parts.append("*Execution Command:*")
    
    # Build command
    if 'TestAlertGeneration' in file_path:
        class_name = 'TestAlertGeneration' + category_name.replace(' ', '')
        cmd = f"pytest {file_path}::{class_name}::{test_function} -v"
    else:
        cmd = f"pytest {file_path}::{test_function} -v"
    
    parts.append(f"{{code}}{cmd}{{code}}")
    
    return "\n".join(parts)

# Test mappings with categories
TESTS = {
    'PZ-14933': {'file': 'positive', 'function': 'test_successful_sd_alert_generation', 'path': 'be_focus_server_tests/integration/alerts/test_alert_generation_positive.py'},
    'PZ-14934': {'file': 'positive', 'function': 'test_successful_sc_alert_generation', 'path': 'be_focus_server_tests/integration/alerts/test_alert_generation_positive.py'},
    'PZ-14935': {'file': 'positive', 'function': 'test_multiple_alerts_generation', 'path': 'be_focus_server_tests/integration/alerts/test_alert_generation_positive.py'},
    'PZ-14936': {'file': 'positive', 'function': 'test_different_severity_levels', 'path': 'be_focus_server_tests/integration/alerts/test_alert_generation_positive.py'},
    'PZ-14937': {'file': 'positive', 'function': 'test_alert_processing_via_rabbitmq', 'path': 'be_focus_server_tests/integration/alerts/test_alert_generation_positive.py'},
    'PZ-14938': {'file': 'negative', 'function': 'test_invalid_class_id', 'path': 'be_focus_server_tests/integration/alerts/test_alert_generation_negative.py'},
    'PZ-14939': {'file': 'negative', 'function': 'test_invalid_severity', 'path': 'be_focus_server_tests/integration/alerts/test_alert_generation_negative.py'},
    'PZ-14940': {'file': 'negative', 'function': 'test_invalid_dof_range', 'path': 'be_focus_server_tests/integration/alerts/test_alert_generation_negative.py'},
    'PZ-14941': {'file': 'negative', 'function': 'test_missing_required_fields', 'path': 'be_focus_server_tests/integration/alerts/test_alert_generation_negative.py'},
    'PZ-14942': {'file': 'negative', 'function': 'test_rabbitmq_connection_failure', 'path': 'be_focus_server_tests/integration/alerts/test_alert_generation_negative.py'},
    'PZ-14943': {'file': 'negative', 'function': 'test_invalid_alert_id_format', 'path': 'be_focus_server_tests/integration/alerts/test_alert_generation_negative.py'},
    'PZ-14944': {'file': 'negative', 'function': 'test_duplicate_alert_ids', 'path': 'be_focus_server_tests/integration/alerts/test_alert_generation_negative.py'},
    'PZ-14945': {'file': 'edge_cases', 'function': 'test_boundary_dof_values', 'path': 'be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py'},
    'PZ-14946': {'file': 'edge_cases', 'function': 'test_min_max_severity', 'path': 'be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py'},
    'PZ-14947': {'file': 'edge_cases', 'function': 'test_zero_alerts_amount', 'path': 'be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py'},
    'PZ-14948': {'file': 'edge_cases', 'function': 'test_very_large_alert_id', 'path': 'be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py'},
    'PZ-14949': {'file': 'edge_cases', 'function': 'test_concurrent_alerts_same_dof', 'path': 'be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py'},
    'PZ-14950': {'file': 'edge_cases', 'function': 'test_rapid_sequential_alerts', 'path': 'be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py'},
    'PZ-14951': {'file': 'edge_cases', 'function': 'test_alert_maximum_fields', 'path': 'be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py'},
    'PZ-14952': {'file': 'edge_cases', 'function': 'test_alert_minimum_fields', 'path': 'be_focus_server_tests/integration/alerts/test_alert_generation_edge_cases.py'},
    'PZ-14953': {'file': 'load', 'function': 'test_high_volume_load', 'path': 'be_focus_server_tests/integration/alerts/test_alert_generation_load.py'},
    'PZ-14954': {'file': 'load', 'function': 'test_sustained_load', 'path': 'be_focus_server_tests/integration/alerts/test_alert_generation_load.py'},
    'PZ-14955': {'file': 'load', 'function': 'test_burst_load', 'path': 'be_focus_server_tests/integration/alerts/test_alert_generation_load.py'},
    'PZ-14956': {'file': 'load', 'function': 'test_mixed_alert_types_load', 'path': 'be_focus_server_tests/integration/alerts/test_alert_generation_load.py'},
    'PZ-14957': {'file': 'load', 'function': 'test_rabbitmq_queue_capacity', 'path': 'be_focus_server_tests/integration/alerts/test_alert_generation_load.py'},
    'PZ-14958': {'file': 'performance', 'function': 'test_alert_response_time', 'path': 'be_focus_server_tests/integration/alerts/test_alert_generation_performance.py'},
    'PZ-14959': {'file': 'performance', 'function': 'test_alert_throughput', 'path': 'be_focus_server_tests/integration/alerts/test_alert_generation_performance.py'},
    'PZ-14960': {'file': 'performance', 'function': 'test_alert_latency', 'path': 'be_focus_server_tests/integration/alerts/test_alert_generation_performance.py'},
    'PZ-14961': {'file': 'performance', 'function': 'test_resource_usage', 'path': 'be_focus_server_tests/integration/alerts/test_alert_generation_performance.py'},
    'PZ-14962': {'file': 'performance', 'function': 'test_end_to_end_performance', 'path': 'be_focus_server_tests/integration/alerts/test_alert_generation_performance.py'},
    'PZ-14963': {'file': 'performance', 'function': 'test_rabbitmq_performance', 'path': 'be_focus_server_tests/integration/alerts/test_alert_generation_performance.py'},
}

def main():
    """Generate enhanced descriptions."""
    test_values = extract_test_values()
    enhanced_descriptions = {}
    
    for test_id, test_config in TESTS.items():
        category = test_config['file']
        function = test_config['function']
        file_path = test_config['path']
        values = test_values.get(test_id, {})
        
        description = build_enhanced_description(
            test_id, values, category, function, file_path
        )
        
        enhanced_descriptions[test_id] = description
        print(f"Generated enhanced description for {test_id}")
    
    # Save to file
    output_file = project_root / 'scripts/jira/enhanced_descriptions_final.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        for test_id, desc in sorted(enhanced_descriptions.items()):
            f.write(f"\n{'='*80}\n")
            f.write(f"TEST: {test_id}\n")
            f.write(f"{'='*80}\n\n")
            f.write(desc)
            f.write("\n\n")
    
    print(f"\nSaved {len(enhanced_descriptions)} enhanced descriptions")
    return enhanced_descriptions

if __name__ == "__main__":
    main()

