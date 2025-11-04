# Check which Xray tests have automation

$xrayListPath = "xray_tests_list.txt"

# Load Xray list
$xrayTests = @{}
Get-Content $xrayListPath | ForEach-Object {
    $parts = $_ -split ',', 2
    if ($parts.Length -gt 0 -and $parts[0] -match '^PZ-\d+') {
        $xrayTests[$parts[0].Trim()] = $true
    }
}

Write-Host "Loaded $($xrayTests.Count) tests from xray_tests_list.txt"
Write-Host ""

# Scan automation tests
$automationTests = @{}
$testFiles = Get-ChildItem -Path tests -Filter "test_*.py" -Recurse

foreach ($testFile in $testFiles) {
    $content = Get-Content $testFile.FullName -Raw
    $matches = [regex]::Matches($content, '@pytest\.mark\.xray\(["\'](PZ-\d+)["\']\)')
    
    foreach ($match in $matches) {
        $testId = $match.Groups[1].Value
        $automationTests[$testId] = $true
    }
}

Write-Host "Found $($automationTests.Count) Xray tests in automation"
Write-Host ""

# Find missing
$missing = @()
foreach ($testId in $xrayTests.Keys) {
    if (-not $automationTests.ContainsKey($testId)) {
        $missing += $testId
    }
}

Write-Host "=" * 80
Write-Host "COVERAGE ANALYSIS"
Write-Host "=" * 80
Write-Host ""
Write-Host "Tests in Xray List: $($xrayTests.Count)"
Write-Host "Tests with Automation: $($automationTests.Count)"
Write-Host "Tests without Automation: $($missing.Count)"
Write-Host ""

if ($missing.Count -gt 0) {
    Write-Host "⚠️  TESTS WITHOUT AUTOMATION:" -ForegroundColor Yellow
    Write-Host ("-" * 80)
    foreach ($testId in $missing | Sort-Object) {
        Write-Host "  - $testId" -ForegroundColor Red
    }
} else {
    Write-Host "✅ ALL TESTS HAVE AUTOMATION!" -ForegroundColor Green
}

Write-Host ""

