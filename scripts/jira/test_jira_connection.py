"""Quick test of Jira connection."""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from external.jira import JiraClient

try:
    print("Connecting to Jira...")
    client = JiraClient()
    print("[OK] Connected successfully!")
    print(f"   User: {client.jira.current_user()}")
    print(f"   Project: {client.project_key}")
    client.close()
except Exception as e:
    print(f"[ERROR] Connection failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

