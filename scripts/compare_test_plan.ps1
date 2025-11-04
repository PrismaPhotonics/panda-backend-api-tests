# Compare Test Plan CSV with xray_tests_list.txt and automation tests

$testPlanPath = "c:\Users\roy.avrahami\Downloads\Test plan (TS_Focus_Server_PZ-14024) by Roy Avrahami (Jira).csv"
$xrayListPath = "xray_tests_list.txt"
$outputPath = "TEST_PLAN_COMPARISON_REPORT.md"

Write-Host "Loading Test Plan CSV..."
# Read Test Plan CSV manually
$testPlanTests = @{}
$lines = Get-Content $testPlanPath -Encoding UTF8

for ($i = 1; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]
    if ([string]::IsNullOrWhiteSpace($line)) { continue }
    
    $parts = $line -split ','
    if ($parts.Length -gt 1) {
        $issueKey = $parts[1].Trim()
        if ($issueKey -match '^PZ-\d+') {
            $summary = $parts[0].Trim().Replace('"', '')
            $testPlanTests[$issueKey] = $summary
        }
    }
}

Write-Host "Found $($testPlanTests.Count) tests in Test Plan CSV"

# Load Xray list
Write-Host "Loading Xray list..."
$xrayTests = @{}
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
Write-Host "Found $($xrayTests.Count) tests in Xray list"

# Find differences
$inPlanNotInXray = $testPlanTests.Keys | Where-Object { -not $xrayTests.ContainsKey($_) }
$inXrayNotInPlan = $xrayTests.Keys | Where-Object { -not $testPlanTests.ContainsKey($_) }

# Generate report
$report = @()
$report += "# Test Plan vs Xray List Comparison Report"
$report += ""
$report += "**Generated:** $(Get-Date)"
$report += "**Test Plan:** TS_Focus_Server_PZ-14024"
$report += ""
$report += "## Statistics"
$report += ""
$report += "- Test Plan CSV: $($testPlanTests.Count) tests"
$report += "- Xray List: $($xrayTests.Count) tests"
$report += ""

# Tests in Plan but not in Xray
if ($inPlanNotInXray.Count -gt 0) {
    $report += "## Tests in Test Plan but NOT in xray_tests_list.txt"
    $report += ""
    $report += "**Total:** $($inPlanNotInXray.Count) tests"
    $report += ""
    foreach ($issueKey in $inPlanNotInXray | Sort-Object) {
        $summary = $testPlanTests[$issueKey]
        $report += "- **$issueKey**: $summary"
    }
    $report += ""
} else {
    $report += "## ✅ All Test Plan tests are in xray_tests_list.txt"
    $report += ""
}

# Tests in Xray but not in Plan
if ($inXrayNotInPlan.Count -gt 0) {
    $report += "## Tests in xray_tests_list.txt but NOT in Test Plan"
    $report += ""
    $report += "**Total:** $($inXrayNotInPlan.Count) tests"
    $report += ""
    $report += "These are older tests or tests outside this Test Plan:"
    $report += ""
    foreach ($issueKey in $inXrayNotInPlan | Sort-Object) {
        $summary = $xrayTests[$issueKey]
        $report += "- **$issueKey**: $summary"
    }
    $report += ""
}

# Common tests
$commonTests = @($testPlanTests.Keys | Where-Object { $xrayTests.ContainsKey($_) })
if ($commonTests.Count -gt 0) {
    $report += "## ✅ Common Tests (In both Test Plan and Xray)"
    $report += ""
    $report += "**Total:** $($commonTests.Count) tests"
    $report += ""
}

# Save report
$report | Set-Content $outputPath -Encoding UTF8

Write-Host ""
Write-Host "=== Results ===" 
Write-Host "Tests in Test Plan not in Xray: $($inPlanNotInXray.Count)"
Write-Host "Tests in Xray not in Test Plan: $($inXrayNotInPlan.Count)"
Write-Host "Report saved to: $outputPath"

if ($inPlanNotInXray.Count -gt 0) {
    Write-Host "`nMissing tests:" -ForegroundColor Yellow
    foreach ($key in $inPlanNotInXray | Sort-Object) {
        Write-Host "  - $key": $testPlanTests[$key]
    }
}

