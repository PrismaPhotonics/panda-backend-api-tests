# Check coverage of all Xray tests in automation

$xrayListPath = "xray_tests_list.txt"
$reportPath = "XRAY_COVERAGE_FULL_REPORT.md"

Write-Host "Loading Xray list..." -ForegroundColor Cyan

# Load all test IDs from xray_tests_list.txt
$xrayTests = @{}
Get-Content $xrayListPath -Encoding UTF8 | ForEach-Object {
    if ($_.Trim()) {
        $parts = $_ -split ',', 2
        $testId = $parts[0].Trim()
        if ($testId -match '^PZ-\d+') {
            $xrayTests[$testId] = $true
        }
    }
}

Write-Host "Found $($xrayTests.Count) tests in xray_tests_list.txt" -ForegroundColor Green

# Scan automation tests
Write-Host "`nScanning automation tests for Xray markers..." -ForegroundColor Cyan
$automationTests = @{}

# Find all Python files with pytest markers
$testFiles = Get-ChildItem -Path tests -Filter "*.py" -Recurse -File

foreach ($file in $testFiles) {
    $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
    
    if ($content) {
        # Find all @pytest.mark.xray("PZ-XXXXX") patterns
        if ($content -match '@pytest\.mark\.xray\(["\'](PZ-\d+)["\']\)') {
            $matches = [regex]::Matches($content, '@pytest\.mark\.xray\(["\'](PZ-\d+)["\']\)')
            foreach ($match in $matches) {
                $testId = $match.Groups[1].Value
                $automationTests[$testId] = @{
                    File = $file.Name
                    Path = $file.FullName
                }
            }
        }
    }
}

Write-Host "Found $($automationTests.Count) Xray markers in automation" -ForegroundColor Green

# Find missing
$missing = @()
$covered = @()

foreach ($testId in $xrayTests.Keys) {
    if ($automationTests.ContainsKey($testId)) {
        $covered += $testId
    } else {
        $missing += $testId
    }
}

# Generate report
$report = @()
$report += "# Xray Test Coverage Report"
$report += ""
$report += "**Generated:** $(Get-Date)"
$report += ""
$report += "## Summary"
$report += ""
$report += "- Total tests in xray_tests_list.txt: **$($xrayTests.Count)**"
$report += "- Tests with automation: **$($automationTests.Count)**"
$report += "- Tests without automation: **$($missing.Count)**"
$report += "- Coverage: **$([math]::Round($automationTests.Count / $xrayTests.Count * 100, 1))%**"
$report += ""

if ($missing.Count -gt 0) {
    $report += "## ⚠️ Missing Automation Coverage ($($missing.Count) tests)"
    $report += ""
    $report += "These tests are in xray_tests_list.txt but do NOT have automation:"
    $report += ""
    $report += "| Test ID | Status |"
    $report += "|---------|--------|"
    foreach ($testId in $missing | Sort-Object) {
        $report += "| $testId | ⚠️ Missing |"
    }
    $report += ""
} else {
    $report += "## ✅ All Tests Have Automation Coverage!"
    $report += ""
}

$report += "## Covered Tests ($($covered.Count))"
$report += ""
$report += "| Test ID | Automation File |"
$report += "|---------|----------------|"
foreach ($testId in $covered | Sort-Object) {
    $fileInfo = $automationTests[$testId]
    $report += "| $testId | $($fileInfo.File) |"
}

$report | Set-Content $reportPath -Encoding UTF8

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Yellow
Write-Host "COVERAGE ANALYSIS" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Yellow
Write-Host ""
Write-Host "Total in Xray List:    $($xrayTests.Count)" -ForegroundColor White
Write-Host "With Automation:       $($automationTests.Count)" -ForegroundColor Green
Write-Host "Without Automation:    $($missing.Count)" -ForegroundColor Red
Write-Host ""
Write-Host "Coverage: $([math]::Round($automationTests.Count / $xrayTests.Count * 100, 1))%" -ForegroundColor $(if($missing.Count -eq 0){"Green"}else{"Yellow"})
Write-Host ""
Write-Host "Report saved to: $reportPath" -ForegroundColor Cyan
Write-Host ""

if ($missing.Count -gt 0) {
    Write-Host "⚠️  MISSING TESTS:" -ForegroundColor Red
    $missing | Sort-Object | ForEach-Object {
        Write-Host "  - $_" -ForegroundColor Yellow
    }
}

