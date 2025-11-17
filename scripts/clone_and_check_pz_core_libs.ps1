# Script to clone pz-core-libs and check for validation code
# ============================================================

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "Cloning and Checking pz-core-libs Repository" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

$repoPath = "C:\Projects\pz-core-libs"
$repoUrl = "https://github.com/PrismaPhotonics/pz-core-libs.git"

# Step 1: Check if repository already exists
Write-Host "`n[1/4] Checking if repository exists..." -ForegroundColor Yellow

if (Test-Path $repoPath) {
    Write-Host "  Repository already exists at: $repoPath" -ForegroundColor Green
    Write-Host "  Skipping clone..." -ForegroundColor Gray
} else {
    Write-Host "  Repository not found. Cloning..." -ForegroundColor Yellow
    
    # Try HTTPS first
    Write-Host "  Attempting HTTPS clone..." -ForegroundColor Gray
    try {
        git clone $repoUrl $repoPath 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ Clone successful (HTTPS)" -ForegroundColor Green
        } else {
            Write-Host "  ❌ HTTPS clone failed. Trying SSH..." -ForegroundColor Yellow
            $repoUrl = "git@github.com:PrismaPhotonics/pz-core-libs.git"
            git clone $repoUrl $repoPath 2>&1 | Out-Null
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  ✅ Clone successful (SSH)" -ForegroundColor Green
            } else {
                Write-Host "  ❌ Clone failed. Please clone manually:" -ForegroundColor Red
                Write-Host "     git clone $repoUrl" -ForegroundColor Gray
                exit 1
            }
        }
    } catch {
        Write-Host "  ❌ Clone failed: $_" -ForegroundColor Red
        exit 1
    }
}

# Step 2: Search for validation code
Write-Host "`n[2/4] Searching for validation code..." -ForegroundColor Yellow

$searchPatterns = @(
    "Cannot proceed.*Missing required",
    "Missing required fiber metadata fields",
    "prr.*>.*0|prr.*<=.*0",
    "@.*validator.*prr|model_validator.*prr",
    "def.*validate.*prr"
)

$results = @{}

foreach ($pattern in $searchPatterns) {
    Write-Host "  Searching for: $pattern" -ForegroundColor Gray
    
    try {
        $matches = Get-ChildItem -Path $repoPath -Recurse -Include "*.py" -ErrorAction SilentlyContinue | 
            Select-String -Pattern $pattern -ErrorAction SilentlyContinue
        
        if ($matches) {
            $results[$pattern] = $matches
            Write-Host "    ✅ Found $($matches.Count) matches" -ForegroundColor Green
        } else {
            Write-Host "    ❌ No matches found" -ForegroundColor Gray
        }
    } catch {
        Write-Host "    ⚠️  Error searching: $_" -ForegroundColor Yellow
    }
}

# Step 3: Check git history
Write-Host "`n[3/4] Checking git history..." -ForegroundColor Yellow

Push-Location $repoPath

try {
    # Recent commits
    Write-Host "  Checking recent commits..." -ForegroundColor Gray
    $recentCommits = git log --all --since="3 weeks ago" --oneline 2>&1
    if ($recentCommits) {
        Write-Host "    ✅ Found $($recentCommits.Count) recent commits" -ForegroundColor Green
    }
    
    # Commits by ohad
    Write-Host "  Checking commits by ohad..." -ForegroundColor Gray
    $ohadCommits = git log --all --since="3 weeks ago" --oneline --author="ohad" -i 2>&1
    if ($ohadCommits) {
        Write-Host "    ✅ Found $($ohadCommits.Count) commits by ohad" -ForegroundColor Green
        $ohadCommits | ForEach-Object { Write-Host "      $_" -ForegroundColor Cyan }
    } else {
        Write-Host "    ❌ No commits by ohad found" -ForegroundColor Gray
    }
    
    # Commits related to validation
    Write-Host "  Checking commits related to validation..." -ForegroundColor Gray
    $validationCommits = git log --all --since="3 weeks ago" --oneline --grep="validation|prr|metadata" -i 2>&1
    if ($validationCommits) {
        Write-Host "    ✅ Found $($validationCommits.Count) commits related to validation" -ForegroundColor Green
        $validationCommits | Select-Object -First 10 | ForEach-Object { Write-Host "      $_" -ForegroundColor Cyan }
    } else {
        Write-Host "    ❌ No validation-related commits found" -ForegroundColor Gray
    }
    
    # Commits in recording_metadata files
    Write-Host "  Checking commits in recording_metadata files..." -ForegroundColor Gray
    $metadataCommits = git log --all --since="3 weeks ago" --oneline -- "*recording_metadata*" 2>&1
    if ($metadataCommits) {
        Write-Host "    ✅ Found $($metadataCommits.Count) commits in recording_metadata files" -ForegroundColor Green
        $metadataCommits | Select-Object -First 10 | ForEach-Object { Write-Host "      $_" -ForegroundColor Cyan }
    } else {
        Write-Host "    ❌ No commits in recording_metadata files found" -ForegroundColor Gray
    }
    
} catch {
    Write-Host "    ⚠️  Error checking git history: $_" -ForegroundColor Yellow
} finally {
    Pop-Location
}

# Step 4: Find RecordingMetadata class
Write-Host "`n[4/4] Finding RecordingMetadata class..." -ForegroundColor Yellow

try {
    $metadataFiles = Get-ChildItem -Path $repoPath -Recurse -Include "*.py" -ErrorAction SilentlyContinue | 
        Select-String -Pattern "class RecordingMetadata" -ErrorAction SilentlyContinue
    
    if ($metadataFiles) {
        Write-Host "  ✅ Found RecordingMetadata class in:" -ForegroundColor Green
        $metadataFiles | ForEach-Object {
            Write-Host "    $($_.Path):$($_.LineNumber)" -ForegroundColor Cyan
        }
    } else {
        Write-Host "  ❌ RecordingMetadata class not found" -ForegroundColor Red
    }
} catch {
    Write-Host "  ⚠️  Error finding RecordingMetadata: $_" -ForegroundColor Yellow
}

# Summary
Write-Host "`n" + "=" * 80 -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

Write-Host "`nRepository: $repoPath" -ForegroundColor White
Write-Host "Validation patterns found: $($results.Count)" -ForegroundColor White

if ($results.Count -gt 0) {
    Write-Host "`nResults saved to: docs/04_testing/analysis/PZ_CORE_LIBS_CHECK_RESULTS.md" -ForegroundColor Green
}

Write-Host "`n✅ Check complete!" -ForegroundColor Green

