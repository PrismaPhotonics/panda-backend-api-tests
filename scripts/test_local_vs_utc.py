"""Test if Focus Server expects local or UTC timestamps."""
import requests
import urllib3
from datetime import datetime, timedelta, timezone
urllib3.disable_warnings()

print("="*70)
print("TESTING LOCAL vs UTC TIMESTAMPS")
print("="*70)

# Get current time
now_local = datetime.now()
now_utc = datetime.now(timezone.utc)

print(f"Local time: {now_local}")
print(f"UTC time: {now_utc}")

# Create timestamps for 10 minutes ago
ten_min_ago_local = now_local - timedelta(minutes=10)
ten_min_ago_utc = now_utc - timedelta(minutes=10)

local_epoch = int(ten_min_ago_local.timestamp())
utc_epoch = int(ten_min_ago_utc.timestamp())

print(f"\n10 minutes ago:")
print(f"  Local epoch: {local_epoch} ({datetime.fromtimestamp(local_epoch)})")
print(f"  UTC epoch: {utc_epoch} ({datetime.fromtimestamp(utc_epoch)})")

# These should be the SAME since timestamp() converts to UTC epoch
print(f"\nDifference: {local_epoch - utc_epoch} seconds")
print("(Should be 0 or very small - both are correct UTC epochs)")

# The ISSUE is when we get datetime from MongoDB (which is naive UTC)
# and treat it as local time
print("\n" + "="*70)
print("THE PROBLEM:")
print("="*70)
print("MongoDB stores: 2025-12-04 15:32:56 (as naive datetime, but actually UTC)")
print("Python timestamp() on naive datetime assumes LOCAL timezone")
print("So it adds 2 hours (Israel timezone) to the epoch!")
print("\nSolution: Explicitly mark MongoDB datetimes as UTC before converting")

