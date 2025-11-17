"""Quick script to check a specific ticket."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from external.jira import JiraClient

ticket_key = 'PZ-14518'
client = JiraClient()
ticket = client.get_issue(ticket_key)
desc = ticket.get('description', '')
print(f"Ticket: {ticket_key}")
print(f"Summary: {ticket.get('summary', 'N/A')}")
print(f"\nDescription (last 1000 chars):")
print(desc[-1000:] if len(desc) > 1000 else desc)

