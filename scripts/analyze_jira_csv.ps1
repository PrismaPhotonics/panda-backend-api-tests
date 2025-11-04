# Read CSV file
$csv = Import-Csv "c:\Users\roy.avrahami\Downloads\Jira (20).csv"

# Load Xray list
$xrayList = Get-Content "C:\Projects\focus_server_automation\xray_tests_list.txt"

# Create hash table of Xray IDs
$xrayIds = @{}
foreach ($line in $xrayList) {
    if ($line -match '^([A-Z]+-\d+),') {
        $xrayIds[$matches[1]] = $line
    }
}

# Analysis results
$notInXray = @()
$duplicates = @{}
$visualization = @()
$roiTests = @()
$singleChannelTests = @()
$identicalSummaries = @{}

# Analyze each issue
foreach ($row in $csv) {
    $key = $row.'Issue key'
    $summary = $row.Summary
    $status = $row.Status
    
    if (-not $key) { continue }
    
    # Check if in Xray list
    if (-not $xrayIds.ContainsKey($key)) {
        $notInXray += [PSCustomObject]@{
            Key = $key
            Summary = $summary
            Status = $status
        }
    }
    
    # Find visualization tests
    if ($summary -match '(CAxis|Colormap|ROI)') {
        $visualization += [PSCustomObject]@{
            Key = $key
            Summary = $summary
            Status = $status
        }
    }
    
    # Find ROI tests
    if ($summary -match 'ROI') {
        $roiTests += [PSCustomObject]@{
            Key = $key
            Summary = $summary
        }
    }
    
    # Find SingleChannel tests
    if ($summary -match 'SingleChannel') {
        $singleChannelTests += [PSCustomObject]@{
            Key = $key
            Summary = $summary
        }
    }
    
    # Group by normalized summary (for duplicate detection)
    $normalized = ($summary -replace '[^\w\s]', '' -replace '\s+', ' ').Trim()
    if (-not $identicalSummaries.ContainsKey($normalized)) {
        $identicalSummaries[$normalized] = @()
    }
    $identicalSummaries[$normalized] += [PSCustomObject]@{
        Key = $key
        Summary = $summary
        Status = $status
    }
}

# Generate report
$report = @"
# CSV Analysis Report - Jira (20).csv
Generated: $(Get-Date)

## Summary
- Total issues in CSV: $($csv.Count)
- Issues NOT in xray_tests_list.txt: $($notInXray.Count)
- Visualization tests: $($visualization.Count)
- ROI tests: $($roiTests.Count)
- SingleChannel tests: $($singleChannelTests.Count)

"@

# Issues NOT in Xray
if ($notInXray.Count -gt 0) {
    $report += "`n## ❌ Issues NOT in xray_tests_list.txt`n`n"
    $report += "| Key | Summary | Status |`n"
    $report += "|-----|---------|--------|`n"
    foreach ($issue in $notInXray | Select-Object -First 30) {
        $report += "| $($issue.Key) | $($issue.Summary) | $($issue.Status) |`n"
    }
    if ($notInXray.Count -gt 30) {
        $report += "`n... and $($notInXray.Count - 30) more`n"
    }
}

# Visualization Tests
if ($visualization.Count -gt 0) {
    $report += "`n## 🎨 Visualization Tests (ROI, CAxis, Colormap)`n`n"
    $report += "| Key | Summary | Status |`n"
    $report += "|-----|---------|--------|`n"
    foreach ($issue in $visualization | Select-Object -First 30) {
        $report += "| $($issue.Key) | $($issue.Summary) | $($issue.Status) |`n"
    }
}

# Identical summaries (duplicates)
$duplicateGroups = $identicalSummaries.GetEnumerator() | Where-Object { $_.Value.Count -gt 1 }
if ($duplicateGroups.Count -gt 0) {
    $report += "`n## 🔄 Identical Summaries (Duplicates)`n`n"
    foreach ($group in $duplicateGroups | Select-Object -First 10) {
        $report += "`n### Summary: $($group.Key)`n"
        $report += "| Key | Summary | Status |`n"
        $report += "|-----|---------|--------|`n"
        foreach ($item in $group.Value) {
            $report += "| $($item.Key) | $($item.Summary) | $($item.Status) |`n"
        }
    }
}

# Save report
$report | Out-File "CSV_ANALYSIS_REPORT.md" -Encoding UTF8

Write-Host "✅ Report saved to CSV_ANALYSIS_REPORT.md"
Write-Host "`nSummary:"
Write-Host "- Issues NOT in Xray: $($notInXray.Count)"
Write-Host "- Visualization tests: $($visualization.Count)"
Write-Host "- ROI tests: $($roiTests.Count)"
Write-Host "- SingleChannel tests: $($singleChannelTests.Count)"
