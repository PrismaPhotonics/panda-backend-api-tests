# Check which tests from Jira CSV are NOT in xray_tests_list.txt

$jiraCsvPath = "c:\Users\roy.avrahami\Downloads\Jira (21).csv"
$xrayListPath = "xray_tests_list.txt"

# Load Jira CSV
Write-Host "Loading Jira CSV..."
$jiraTests = @{}
$lines = Get-Content $jiraCsvPath -Encoding UTF8

for ($i = 1; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]
    if ([string]::IsNullOrWhiteSpace($line)) { continue }
    
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
Get-Content $xrayListPath | ForEach-Object {
    $parts = $_ -split ',', 2
    if ($parts.Length -gt 0) {
        $key = $parts[0].Trim()
        if ($key -match '^PZ-\d+') {
            $xrayTests[$key] = $true
        }
    }
}

Write-Host "Found $($xrayTests.Count) tests in Xray list"

# Find missing
$missing = @()
foreach ($key in $jiraTests.Keys) {
    if (-not $xrayTests.ContainsKey($key)) {
        $missing += [PSCustomObject]@{
            IssueKey = $key
            Summary = $jiraTests[$key]
        }
    }
}

Write-Host ""
if ($missing.Count -gt 0) {
    Write-Host "❌ Tests in Jira CSV but NOT in xray_tests_list.txt: $($missing.Count)" -ForegroundColor Red
    Write-Host ""
    $missing | Format-Table -AutoSize
} else {
    Write-Host "✅ SUCCESS: All tests from Jira CSV are in xray_tests_list.txt!" -ForegroundColor Green
}

