# Compare Jira CSV with Xray list and Automation tests

$jiraCsvPath = "c:\Users\roy.avrahami\Downloads\Jira (21).csv"
$xrayListPath = "xray_tests_list.txt"
$outputPath = "JIRA_VS_AUTOMATION_COMPARISON.md"

Write-Host "Loading Jira CSV..."
# Read Jira CSV manually to handle duplicate column names
$jiraTests = @{}
$lines = Get-Content $jiraCsvPath -Encoding UTF8
$headerLine = $lines[0]

for ($i = 1; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]
    if ([string]::IsNullOrWhiteSpace($line)) { continue }
    
    # Try to extract Issue key (usually 2nd field after Summary)
    # Simple split by comma - Issue key is usually at position 1
    $parts = $line -split ','
    if ($parts.Length -gt 1) {
        $issueKey = $parts[1].Trim()
        if ($issueKey -match '^PZ-\d+') {
            $summary = $parts[0].Trim().Replace('"', '')
            $jiraTests[$issueKey] = $summary
        }
    }
}

Write-Host "Found $($jiraTests.Count) tests in Jira CSV"

# Load Xray list
Write-Host "Loading Xray list..."
$xrayTests = @{}
if (Test-Path $xrayListPath) {
    Get-Content $xrayListPath | ForEach-Object {
        $parts = $_ -split ',', 2
        if ($parts.Length -gt 0) {
            $key = $parts[0].Trim()
            if ($key -match '^PZ-\d+') {
                $summary = if ($parts.Length -gt 1) { $parts[1].Trim() } else { "" }
                $xrayTests[$key] = $summary
            }
        }
    }
}
Write-Host "Found $($xrayTests.Count) tests in Xray list"

# Get automation test files
Write-Host "Scanning automation tests..."
$automationTestFiles = Get-ChildItem -Path "tests" -Filter "test_*.py" -Recurse | Select-Object -ExpandProperty FullName
Write-Host "Found $($automationTestFiles.Count) automation test files"

# Find differences
$jiraNotInXray = $jiraTests.Keys | Where-Object { -not $xrayTests.ContainsKey($_) }
$xrayNotInJira = $xrayTests.Keys | Where-Object { -not $jiraTests.ContainsKey($_) }

# Generate report
$report = @()
$report += "# Jira vs Automation Comparison Report"
$report += ""
$report += "## Statistics"
$report += ""
$report += "- Jira CSV tests: $($jiraTests.Count)"
$report += "- Xray mapped tests: $($xrayTests.Count)"
$report += "- Automation test files: $($automationTestFiles.Count)"
$report += ""

if ($jiraNotInXray.Count -gt 0) {
    $report += "## Tests in Jira but NOT in Xray (Not Yet Automated)"
    $report += ""
    foreach ($issueKey in $jiraNotInXray | Sort-Object) {
        $summary = $jiraTests[$issueKey]
        $report += "- **$issueKey**: $summary"
    }
    $report += ""
}

if ($xrayNotInJira.Count -gt 0) {
    $report += "## Tests in Xray but NOT in Jira CSV (Old/Removed)"
    $report += ""
    foreach ($issueKey in $xrayNotInJira | Sort-Object) {
        $summary = $xrayTests[$issueKey]
        $report += "- **$issueKey**: $summary"
    }
    $report += ""
}

# Common tests
$commonTests = @($jiraTests.Keys | Where-Object { $xrayTests.ContainsKey($_) })
if ($commonTests.Count -gt 0) {
    $report += "## Common Tests (In both Jira and Xray)"
    $report += ""
    $report += "Total: $($commonTests.Count) tests"
    $report += ""
}

$report | Set-Content $outputPath -Encoding UTF8

Write-Host ""
Write-Host "=== Results ===" 
Write-Host "Tests in Jira not yet automated: $($jiraNotInXray.Count)"
Write-Host "Tests in Xray but removed from Jira: $($xrayNotInJira.Count)"
Write-Host "Report saved to: $outputPath"

