# Quick Job Capacity Check - PowerShell Script
# ============================================
# סקריפט מהיר לבדיקת קיבולת jobs במערכת Focus Server
#
# שימוש:
#   .\run_capacity_check.ps1 -Environment staging -Quick
#   .\run_capacity_check.ps1 -Environment production -Comprehensive
#
# תאריך: 26 אוקטובר 2025

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('development', 'staging', 'production', 'new_production')]
    [string]$Environment = 'staging',
    
    [Parameter(Mandatory=$false)]
    [switch]$Quick,
    
    [Parameter(Mandatory=$false)]
    [switch]$Comprehensive,
    
    [Parameter(Mandatory=$false)]
    [int]$MaxJobs = 0,
    
    [Parameter(Mandatory=$false)]
    [string]$OutputFile = "capacity_check_results.json",
    
    [Parameter(Mandatory=$false)]
    [switch]$NoSave,
    
    [Parameter(Mandatory=$false)]
    [switch]$Help
)

# ===================================================================
# Help Message
# ===================================================================

if ($Help) {
    Write-Host @"

╔════════════════════════════════════════════════════════════════╗
║       Focus Server - Job Capacity Check (PowerShell)          ║
╚════════════════════════════════════════════════════════════════╝

שימוש:
  .\run_capacity_check.ps1 [אופציות]

אופציות:
  -Environment <env>     סביבה לבדיקה (development/staging/production/new_production)
                        ברירת מחדל: staging
  
  -Quick                 בדיקה מהירה (1, 5, 10 jobs) - ~30 שניות
  
  -Comprehensive         בדיקה מקיפה (עד 100 jobs) - ~5-10 דקות
                        ⚠️ עלול להעמיס על המערכת!
  
  -MaxJobs <num>         מספר jobs מקסימלי מותאם אישית
  
  -OutputFile <file>     שם קובץ פלט
                        ברירת מחדל: capacity_check_results.json
  
  -NoSave                אל תשמור תוצאות לקובץ
  
  -Help                  הצג הודעה זו

דוגמאות:

  # בדיקה מהירה של staging
  .\run_capacity_check.ps1 -Environment staging -Quick

  # בדיקה סטנדרטית של production
  .\run_capacity_check.ps1 -Environment production

  # בדיקה מקיפה עם שמירת תוצאות
  .\run_capacity_check.ps1 -Environment staging -Comprehensive -OutputFile staging_test.json

  # בדיקה מותאמת אישית עד 25 jobs
  .\run_capacity_check.ps1 -Environment production -MaxJobs 25

"@
    exit 0
}

# ===================================================================
# Functions
# ===================================================================

function Write-Banner {
    param([string]$Text)
    
    Write-Host ""
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host $Text.PadLeft(($Text.Length + 80) / 2) -ForegroundColor Cyan
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️ $Message" -ForegroundColor Yellow
}

function Write-Error-Message {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Check-Prerequisites {
    Write-Host "בדיקת דרישות מוקדמות..." -ForegroundColor Yellow
    
    # Check Python
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Message "Python לא מותקן!"
        Write-Host "התקן Python 3.8+ מ: https://www.python.org/"
        exit 1
    }
    Write-Success "Python: $pythonVersion"
    
    # Check if in correct directory
    if (-not (Test-Path "scripts/quick_job_capacity_check.py")) {
        Write-Error-Message "הרץ את הסקריפט מהתיקייה הראשית של הפרויקט!"
        exit 1
    }
    Write-Success "תיקיית עבודה תקינה"
    
    # Check dependencies
    $requirementsFile = "requirements.txt"
    if (Test-Path $requirementsFile) {
        Write-Host "בדיקת תלויות..." -ForegroundColor Yellow
        # Note: We're not installing automatically, just checking
        Write-Success "requirements.txt קיים"
    }
    
    Write-Host ""
}

# ===================================================================
# Main Script
# ===================================================================

Write-Banner "🔍 Focus Server - Job Capacity Check"

Write-Host "סביבה: $Environment" -ForegroundColor Cyan
Write-Host "תאריך: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Check-Prerequisites

# Build Python command
$pythonCmd = "python scripts/quick_job_capacity_check.py"
$pythonCmd += " --environment $Environment"

if ($Quick) {
    $pythonCmd += " --quick"
    Write-Host "סוג בדיקה: מהירה (1, 5, 10 jobs)" -ForegroundColor Cyan
    Write-Host "זמן משוער: ~30 שניות" -ForegroundColor Cyan
}
elseif ($Comprehensive) {
    $pythonCmd += " --comprehensive"
    Write-Host "סוג בדיקה: מקיפה (עד 100 jobs)" -ForegroundColor Cyan
    Write-Host "זמן משוער: ~5-10 דקות" -ForegroundColor Cyan
    Write-Warning "בדיקה זו עלולה להעמיס על המערכת!"
}
elseif ($MaxJobs -gt 0) {
    $pythonCmd += " --max-jobs $MaxJobs"
    Write-Host "סוג בדיקה: מותאמת אישית (עד $MaxJobs jobs)" -ForegroundColor Cyan
}
else {
    Write-Host "סוג בדיקה: סטנדרטית (1, 5, 10, 20, 30 jobs)" -ForegroundColor Cyan
    Write-Host "זמן משוער: ~2-3 דקות" -ForegroundColor Cyan
}

if (-not $NoSave) {
    $pythonCmd += " --output $OutputFile"
    Write-Host "קובץ פלט: $OutputFile" -ForegroundColor Cyan
}
else {
    $pythonCmd += " --no-save"
}

Write-Host ""
Write-Host "מתחיל בדיקה..." -ForegroundColor Yellow
Write-Host ""

# Run Python script
try {
    Invoke-Expression $pythonCmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Success "הבדיקה הושלמה בהצלחה!"
        
        if (-not $NoSave -and (Test-Path $OutputFile)) {
            Write-Host ""
            Write-Host "תוצאות נשמרו ב: $OutputFile" -ForegroundColor Cyan
            
            # Show file size
            $fileSize = (Get-Item $OutputFile).Length
            Write-Host "גודל קובץ: $fileSize bytes" -ForegroundColor Gray
            
            # Offer to open file
            Write-Host ""
            $response = Read-Host "האם לפתוח את קובץ התוצאות? (y/n)"
            if ($response -eq 'y' -or $response -eq 'Y') {
                Start-Process $OutputFile
            }
        }
    }
    else {
        Write-Error-Message "הבדיקה נכשלה עם קוד שגיאה: $LASTEXITCODE"
        exit $LASTEXITCODE
    }
}
catch {
    Write-Error-Message "שגיאה בהרצת הבדיקה: $_"
    exit 1
}

Write-Host ""
Write-Banner "✅ בדיקת קיבולת הושלמה"

# ===================================================================
# Additional Options
# ===================================================================

Write-Host ""
Write-Host "אופציות נוספות:" -ForegroundColor Yellow
Write-Host "  1. הרץ בדיקת pytest מלאה:"
Write-Host "     pytest be_focus_server_tests/load/test_job_capacity_limits.py -v -m load" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. הרץ רק baseline test:"
Write-Host "     pytest be_focus_server_tests/load/test_job_capacity_limits.py -v -m baseline" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. צפה בלוגים:"
Write-Host "     Get-Content logs\quick_capacity_check_*.log -Tail 50" -ForegroundColor Gray
Write-Host ""

# Exit successfully
exit 0

