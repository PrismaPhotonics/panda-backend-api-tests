# PowerShell script to run financial analysis
$ErrorActionPreference = "Stop"

Write-Host "=" * 80
Write-Host "מתחיל אנליזה פיננסית מעמיקה..."
Write-Host "=" * 80
Write-Host ""

# Try to find Python
$pythonPaths = @(
    "python",
    "python3",
    "py",
    "C:\Python*\python.exe",
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\*\python.exe"
)

$pythonCmd = $null
foreach ($path in $pythonPaths) {
    try {
        $result = Get-Command $path -ErrorAction SilentlyContinue
        if ($result) {
            $pythonCmd = $result.Source
            Write-Host "נמצא Python: $pythonCmd"
            break
        }
    } catch {
        continue
    }
}

if (-not $pythonCmd) {
    Write-Host "שגיאה: לא נמצא Python!"
    Write-Host "אנא התקן Python מ: https://www.python.org/downloads/"
    Write-Host ""
    Write-Host "או הרץ ידנית:"
    Write-Host "  pip install pandas openpyxl xlrd"
    Write-Host '  python scripts\analyze_credit_card_expenses.py --data-dir "כרטיסי אשראי רועי" --income 37000 --mortgage 10000 --debt -83000'
    exit 1
}

# Change to script directory
Set-Location $PSScriptRoot

# Run the analysis
Write-Host "מריץ ניתוח..."
Write-Host ""

try {
    & $pythonCmd scripts\run_analysis.py
    Write-Host ""
    Write-Host "=" * 80
    Write-Host "הניתוח הושלם בהצלחה!"
    Write-Host "קרא את הקובץ: comprehensive_financial_analysis.txt"
    Write-Host "=" * 80
} catch {
    Write-Host "שגיאה בהרצת הסקריפט: $_"
    Write-Host ""
    Write-Host "נסה להריץ ידנית:"
    Write-Host '  python scripts\analyze_credit_card_expenses.py --data-dir "כרטיסי אשראי רועי" --income 37000 --mortgage 10000 --debt -83000'
    exit 1
}

