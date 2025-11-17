# Script to fix potential serialization issues in test files
# Usage: .\scripts\fix_serialization.ps1 tests\integration\api\test_config_validation_high_priority.py

param(
    [Parameter(Mandatory=$true)]
    [string]$FilePath
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "File Serialization Fix Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $FilePath)) {
    Write-Host "ERROR: File not found: $FilePath" -ForegroundColor Red
    exit 1
}

Write-Host "Checking file: $FilePath" -ForegroundColor Yellow
$fileInfo = Get-Item $FilePath
Write-Host "  Size: $($fileInfo.Length) bytes" -ForegroundColor Gray
Write-Host "  Lines: $((Get-Content $FilePath).Count)" -ForegroundColor Gray
Write-Host ""

# Read file content
try {
    $content = Get-Content $FilePath -Raw -Encoding UTF8
    $originalContent = $content
    $issues = @()
    $fixed = $false
    
    # Check for BOM
    if ($content.StartsWith([char]0xFEFF)) {
        Write-Host "  [ISSUE] Found UTF-8 BOM" -ForegroundColor Yellow
        $content = $content.TrimStart([char]0xFEFF)
        $issues += "BOM removed"
        $fixed = $true
    }
    
    # Check for Windows line endings (CRLF)
    if ($content -match "`r`n") {
        Write-Host "  [ISSUE] Found Windows line endings (CRLF)" -ForegroundColor Yellow
        $content = $content -replace "`r`n", "`n"
        $issues += "Line endings normalized to LF"
        $fixed = $true
    }
    
    # Check for carriage return only
    if ($content -match "`r(?!`n)") {
        Write-Host "  [ISSUE] Found carriage return without newline" -ForegroundColor Yellow
        $content = $content -replace "`r(?!`n)", "`n"
        $issues += "Carriage returns normalized"
        $fixed = $true
    }
    
    # Check for invalid control characters
    $invalidChars = @()
    for ($i = 0; $i -lt $content.Length; $i++) {
        $code = [int][char]$content[$i]
        if ($code -lt 32 -and $code -notin 9, 10, 13) {
            $invalidChars += "Position $i : Code $code"
        }
    }
    
    if ($invalidChars.Count -gt 0) {
        Write-Host "  [ISSUE] Found $($invalidChars.Count) invalid control characters" -ForegroundColor Yellow
        $newContent = ""
        for ($i = 0; $i -lt $content.Length; $i++) {
            $code = [int][char]$content[$i]
            if ($code -ge 32 -or $code -in 9, 10, 13) {
                $newContent += $content[$i]
            }
        }
        $content = $newContent
        $issues += "Invalid control characters removed"
        $fixed = $true
    }
    
    # Check file size
    $sizeKB = [math]::Round($fileInfo.Length / 1024, 2)
    if ($sizeKB -gt 100) {
        Write-Host "  [INFO] File is large: $sizeKB KB" -ForegroundColor Gray
        Write-Host "         This may cause serialization issues in Cursor" -ForegroundColor Gray
    }
    
    if ($fixed) {
        Write-Host ""
        Write-Host "Creating backup..." -ForegroundColor Yellow
        $backupPath = $FilePath + ".backup"
        Copy-Item $FilePath $backupPath -Force
        Write-Host "  Backup created: $backupPath" -ForegroundColor Green
        
        Write-Host ""
        Write-Host "Fixing file..." -ForegroundColor Yellow
        # Write with UTF-8 without BOM and LF line endings
        $utf8NoBom = New-Object System.Text.UTF8Encoding $false
        [System.IO.File]::WriteAllText($FilePath, $content, $utf8NoBom)
        
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "File fixed successfully!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Issues fixed:" -ForegroundColor Cyan
        foreach ($issue in $issues) {
            Write-Host "  - $issue" -ForegroundColor White
        }
        Write-Host ""
        Write-Host "Original size: $($fileInfo.Length) bytes" -ForegroundColor Gray
        $newSize = (Get-Item $FilePath).Length
        Write-Host "New size: $newSize bytes" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Please try using Cursor again." -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "No issues found - file is clean!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "The serialization issue may be in Cursor itself." -ForegroundColor Yellow
        Write-Host "Try:" -ForegroundColor Yellow
        Write-Host "  1. Close and reopen Cursor" -ForegroundColor White
        Write-Host "  2. Close the large file ($sizeKB KB)" -ForegroundColor White
        Write-Host "  3. Restart Cursor" -ForegroundColor White
        Write-Host "  4. Try with a smaller file first" -ForegroundColor White
    }
    
} catch {
    Write-Host ""
    Write-Host "ERROR: Failed to process file" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}


