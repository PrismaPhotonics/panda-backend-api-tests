# ============================================================================
# Clean Stale Recording - Production Environment
# ============================================================================
# This script marks or deletes stale recordings (old recordings without end_time)
# ============================================================================

param(
    [Parameter(Mandatory=$false)]
    [switch]$Delete = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$DryRun = $false,
    
    [Parameter(Mandatory=$false)]
    [string]$UUID = "65777a6b-7e0d-4876-add0-7d136792ce64"
)

$ErrorActionPreference = "Stop"

Write-Host "`n════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Clean Stale Recording - Production Environment" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# MongoDB connection details
$MONGODB_HOST = "10.10.100.108"
$MONGODB_PORT = "27017"
$MONGODB_USER = "prisma"
$MONGODB_PASS = "prisma"
$MONGODB_DB = "prisma"
$GUID = "d57c8adb-ea00-4666-83cb-0248ae9d602f"
$STALE_UUID = $UUID

$MONGODB_URI = "mongodb://${MONGODB_USER}:${MONGODB_PASS}@${MONGODB_HOST}:${MONGODB_PORT}/${MONGODB_DB}?authSource=${MONGODB_DB}"

Write-Host "📋 Details:" -ForegroundColor Yellow
Write-Host "   Host: $MONGODB_HOST:$MONGODB_PORT" -ForegroundColor White
Write-Host "   Database: $MONGODB_DB" -ForegroundColor White
Write-Host "   Collection: $GUID" -ForegroundColor White
Write-Host "   Stale UUID: $STALE_UUID" -ForegroundColor White
Write-Host "   Action: $(if ($Delete) { 'DELETE' } else { 'MARK AS DELETED' })" -ForegroundColor $(if ($Delete) { 'Red' } else { 'Yellow' })
Write-Host ""

if ($DryRun) {
    Write-Host "🔍 DRY RUN MODE - No changes will be made" -ForegroundColor Yellow
    Write-Host ""
}

# Check if mongosh is available
Write-Host "Step 1: Checking MongoDB shell..." -ForegroundColor Cyan
try {
    $mongoshVersion = mongosh --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "mongosh not found"
    }
    Write-Host "[OK] mongosh is available" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] mongosh is not installed or not in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install MongoDB Shell (mongosh)" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Create JavaScript script
if ($Delete) {
    $action = "DELETE"
    $jsScript = @"
// Delete stale recording
use $MONGODB_DB

var collection = db.getCollection("$GUID");
var staleUUID = "$STALE_UUID";

print("════════════════════════════════════════════════════════════");
print("Deleting Stale Recording");
print("════════════════════════════════════════════════════════════");
print("");

// Check if recording exists
var recording = collection.findOne({ uuid: staleUUID });

if (!recording) {
    print("⚠️  Recording not found with UUID: " + staleUUID);
    print("   No action needed.");
    quit(0);
}

print("📋 Recording found:");
print("   UUID: " + recording.uuid);
print("   Start time: " + recording.start_time);
print("   End time: " + (recording.end_time || "null (missing)"));
print("   Deleted: " + recording.deleted);
print("");

// Delete the recording
var result = collection.deleteOne({ uuid: staleUUID });

if (result.deletedCount === 1) {
    print("✅ Recording deleted successfully!");
} else {
    print("❌ Failed to delete recording");
    quit(1);
}
print("");
"@
} else {
    $action = "MARK AS DELETED"
    $jsScript = @"
// Mark stale recording as deleted (CAREFUL: Check if it might be LIVE first!)
use $MONGODB_DB

var collection = db.getCollection("$GUID");
var staleUUID = "$STALE_UUID";

print("════════════════════════════════════════════════════════════");
print("Analyzing Recording - Stale vs LIVE Check");
print("════════════════════════════════════════════════════════════");
print("");

// Check if recording exists
var recording = collection.findOne({ uuid: staleUUID });

if (!recording) {
    print("⚠️  Recording not found with UUID: " + staleUUID);
    print("   No action needed.");
    quit(0);
}

print("📋 Recording found:");
print("   UUID: " + recording.uuid);
print("   Start time: " + recording.start_time);
print("   End time: " + (recording.end_time || "null (missing)"));
print("   Deleted: " + recording.deleted);
print("");

// CAREFUL CHECK: Calculate age
var now = new Date();
var startTime = recording.start_time;
var ageHours = (now - startTime) / (1000 * 60 * 60);

print("📊 Age Analysis:");
print("   Age: " + ageHours.toFixed(1) + " hours");
print("   Threshold: 24 hours");
print("");

// Check if it might be LIVE (recent, <24h)
if (ageHours < 24) {
    print("⚠️  WARNING: Recording is less than 24 hours old!");
    print("   This might be a LIVE recording (still in progress).");
    print("   It's too risky to mark as deleted - might be active!");
    print("");
    print("💡 Recommendation:");
    print("   1. Check Focus Server logs for active jobs with this UUID");
    print("   2. Check Kubernetes pods for running jobs");
    print("   3. If confirmed inactive/abandoned, manually delete");
    print("");
    print("❌ Canceling operation for safety.");
    quit(1);
}

// Only proceed if >24h old (definitely stale)
print("✅ Recording is >24h old - confirmed STALE (not LIVE)");
print("   Proceeding with cleanup...");
print("");

// Update the recording
var updateResult = collection.updateOne(
    { uuid: staleUUID },
    {
        `$set: {
            deleted: true,
            end_time: new Date(),
            cleanup_note: "Marked as deleted due to stale status (no end_time, >24h old - confirmed not LIVE)",
            cleanup_date: new Date()
        }
    }
);

if (updateResult.modifiedCount === 1) {
    print("✅ Recording marked as deleted successfully!");
    
    // Verify
    var updated = collection.findOne({ uuid: staleUUID });
    print("");
    print("📋 Updated recording:");
    print("   Deleted: " + updated.deleted);
    print("   End time: " + updated.end_time);
    print("   Cleanup note: " + updated.cleanup_note);
} else {
    print("⚠️  No changes made (recording might already be marked as deleted)");
}
print("");
"@
}

# Save script to temporary file
$tempScript = [System.IO.Path]::GetTempFileName() + ".js"
$jsScript | Out-File -FilePath $tempScript -Encoding utf8

Write-Host "Step 2: Finding stale recording..." -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "[DRY RUN] Would execute:" -ForegroundColor Yellow
    Write-Host "  mongosh `"$MONGODB_URI`" --file `"$tempScript`"" -ForegroundColor White
    Write-Host ""
    Write-Host "Action: $action" -ForegroundColor Yellow
    Write-Host ""
    Remove-Item $tempScript -ErrorAction SilentlyContinue
    exit 0
}

# Confirm action
if ($Delete) {
    Write-Host "⚠️  WARNING: This will PERMANENTLY DELETE the recording!" -ForegroundColor Red
    Write-Host ""
    $confirm = Read-Host "Are you sure you want to DELETE? Type 'yes' to confirm"
    if ($confirm -ne "yes") {
        Write-Host "Operation cancelled." -ForegroundColor Yellow
        Remove-Item $tempScript -ErrorAction SilentlyContinue
        exit 0
    }
}

Write-Host "[OK] Executing..." -ForegroundColor Green
Write-Host ""

# Execute MongoDB script
try {
    mongosh "$MONGODB_URI" --file "$tempScript"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Cleanup completed!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "⚠️  Script completed with warnings" -ForegroundColor Yellow
    }
} catch {
    Write-Host ""
    Write-Host "❌ Error executing MongoDB script: $_" -ForegroundColor Red
    exit 1
} finally {
    # Cleanup
    Remove-Item $tempScript -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Next Steps" -ForegroundColor Yellow
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Verify the recording was updated:" -ForegroundColor White
Write-Host "   mongosh `"$MONGODB_URI`"" -ForegroundColor Cyan
Write-Host "   db.getCollection(`"$GUID`").findOne({uuid: `"$STALE_UUID`"})" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Run the test to verify:" -ForegroundColor White
Write-Host "   pytest tests/data_quality/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_recordings_have_all_required_metadata -v --env=production" -ForegroundColor Cyan
Write-Host ""
Write-Host "════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

