# ============================================================================
# Fix MongoDB Indexes - Production Environment
# ============================================================================
# This script creates missing MongoDB indexes on the production database
# ============================================================================

param(
    [Parameter(Mandatory=$false)]
    [switch]$DryRun = $false
)

$ErrorActionPreference = "Stop"

Write-Host "`n════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Fix MongoDB Indexes - Production Environment" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# MongoDB connection details
$MONGODB_HOST = "10.10.100.108"
$MONGODB_PORT = "27017"
$MONGODB_USER = "prisma"
$MONGODB_PASS = "prisma"
$MONGODB_DB = "prisma"
$GUID = "d57c8adb-ea00-4666-83cb-0248ae9d602f"

$MONGODB_URI = "mongodb://${MONGODB_USER}:${MONGODB_PASS}@${MONGODB_HOST}:${MONGODB_PORT}/${MONGODB_DB}?authSource=${MONGODB_DB}"

Write-Host "📋 Connection Details:" -ForegroundColor Yellow
Write-Host "   Host: $MONGODB_HOST:$MONGODB_PORT" -ForegroundColor White
Write-Host "   Database: $MONGODB_DB" -ForegroundColor White
Write-Host "   Collection GUID: $GUID" -ForegroundColor White
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
    Write-Host "Please install MongoDB Shell (mongosh):" -ForegroundColor Yellow
    Write-Host "  1. Download from: https://www.mongodb.com/try/download/shell" -ForegroundColor White
    Write-Host "  2. Or use Docker: docker run -it --rm mongo:latest mongosh" -ForegroundColor White
    Write-Host ""
    Write-Host "Alternatively, you can run the commands manually:" -ForegroundColor Yellow
    Write-Host "  mongosh `"$MONGODB_URI`"" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host ""

# Create JavaScript script for creating indexes
$jsScript = @"
// MongoDB Index Creation Script
// Collection: $GUID

use $MONGODB_DB

print("════════════════════════════════════════════════════════════");
print("Creating indexes on collection: $GUID");
print("════════════════════════════════════════════════════════════");
print("");

var collection = db.getCollection("$GUID");

// Check existing indexes
print("📋 Current indexes:");
var existingIndexes = collection.getIndexes();
existingIndexes.forEach(function(idx) {
    print("   - " + idx.name + " on " + JSON.stringify(idx.key));
});
print("");

// Index #1: start_time
print("Creating index: start_time_1...");
try {
    collection.createIndex(
        { "start_time": 1 },
        { background: true, name: "start_time_1" }
    );
    print("✅ Index 'start_time_1' created successfully");
} catch (e) {
    if (e.codeName === "IndexOptionsConflict") {
        print("⚠️  Index 'start_time_1' already exists");
    } else {
        print("❌ Error creating 'start_time_1': " + e.message);
    }
}
print("");

// Index #2: end_time
print("Creating index: end_time_1...");
try {
    collection.createIndex(
        { "end_time": 1 },
        { background: true, name: "end_time_1" }
    );
    print("✅ Index 'end_time_1' created successfully");
} catch (e) {
    if (e.codeName === "IndexOptionsConflict") {
        print("⚠️  Index 'end_time_1' already exists");
    } else {
        print("❌ Error creating 'end_time_1': " + e.message);
    }
}
print("");

// Index #3: uuid (UNIQUE)
print("Creating index: uuid_1 (UNIQUE)...");
try {
    collection.createIndex(
        { "uuid": 1 },
        { unique: true, background: true, name: "uuid_1" }
    );
    print("✅ Index 'uuid_1' created successfully");
} catch (e) {
    if (e.codeName === "IndexOptionsConflict" || e.codeName === "IndexKeySpecsConflict") {
        print("⚠️  Index 'uuid_1' already exists");
    } else if (e.codeName === "DuplicateKey") {
        print("❌ Error: Duplicate UUID values found! Cannot create unique index.");
        print("   Please clean duplicate UUIDs first.");
    } else {
        print("❌ Error creating 'uuid_1': " + e.message);
    }
}
print("");

// Index #4: deleted
print("Creating index: deleted_1...");
try {
    collection.createIndex(
        { "deleted": 1 },
        { background: true, name: "deleted_1" }
    );
    print("✅ Index 'deleted_1' created successfully");
} catch (e) {
    if (e.codeName === "IndexOptionsConflict") {
        print("⚠️  Index 'deleted_1' already exists");
    } else {
        print("❌ Error creating 'deleted_1': " + e.message);
    }
}
print("");

// Verify all indexes
print("════════════════════════════════════════════════════════════");
print("Final index list:");
print("════════════════════════════════════════════════════════════");
var finalIndexes = collection.getIndexes();
finalIndexes.forEach(function(idx) {
    var unique = idx.unique ? " [UNIQUE]" : "";
    print("   ✅ " + idx.name + unique + " on " + JSON.stringify(idx.key));
});
print("");

// Check if all required indexes exist
var requiredIndexes = ["_id_", "start_time_1", "end_time_1", "uuid_1", "deleted_1"];
var indexNames = finalIndexes.map(function(idx) { return idx.name; });
var missingIndexes = requiredIndexes.filter(function(name) {
    return !indexNames.includes(name);
});

if (missingIndexes.length === 0) {
    print("✅ All required indexes are present!");
} else {
    print("⚠️  Missing indexes: " + missingIndexes.join(", "));
}
print("");
"@

# Save script to temporary file
$tempScript = [System.IO.Path]::GetTempFileName() + ".js"
$jsScript | Out-File -FilePath $tempScript -Encoding utf8

Write-Host "Step 2: Connecting to MongoDB..." -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "[DRY RUN] Would execute:" -ForegroundColor Yellow
    Write-Host "  mongosh `"$MONGODB_URI`" --file `"$tempScript`"" -ForegroundColor White
    Write-Host ""
    Write-Host "Script content:" -ForegroundColor Yellow
    Write-Host $jsScript -ForegroundColor Gray
    Remove-Item $tempScript -ErrorAction SilentlyContinue
    exit 0
}

Write-Host "[OK] Connecting..." -ForegroundColor Green
Write-Host ""

# Execute MongoDB script
try {
    mongosh "$MONGODB_URI" --file "$tempScript"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Index creation completed!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "⚠️  Script completed with warnings (exit code: $LASTEXITCODE)" -ForegroundColor Yellow
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
Write-Host "1. Verify indexes were created:" -ForegroundColor White
Write-Host "   mongosh `"$MONGODB_URI`"" -ForegroundColor Cyan
Write-Host "   db.getCollection(`"$GUID`").getIndexes()" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Run the test to verify:" -ForegroundColor White
Write-Host "   pytest be_focus_server_tests/data_quality/test_mongodb_data_quality.py::TestMongoDBDataQuality::test_mongodb_indexes_exist_and_optimal -v --env=production" -ForegroundColor Cyan
Write-Host ""
Write-Host "════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

