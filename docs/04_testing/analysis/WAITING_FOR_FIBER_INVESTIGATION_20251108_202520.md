# Waiting for Fiber Investigation Report

**Date:** 2025-11-08 20:25:20

## Summary

- Error found in pz_core_libs: True
- Commits found: 2
- Error found in logs: False
- System waiting for fiber: True
- PRR value: 0.0

## Detailed Results

```json
{
  "timestamp": "2025-11-08T20:23:49.033489",
  "investigations": {
    "pz_core_libs_search": {
      "error_found": true,
      "files_found": [
        "pz\\microservices\\backoffice_v2\\services\\known_locations.py"
      ],
      "error_message": "Cannot proceed: Missing required fiber metadata fields: prr"
    },
    "git_history": {
      "commits_found": [
        "3bd8cfcb6 Merged in replace-generic-fiber-to-be-according-to-the-convention (pull request #1441)",
        "0bcd7629b replace generic fiber to be according to the convention"
      ],
      "recent_changes": []
    },
    "focus_server_logs": {
      "error_found_in_logs": false,
      "first_occurrence": null,
      "log_entries": []
    },
    "system_state": {
      "metadata_available": true,
      "prr_value": 0.0,
      "is_waiting_for_fiber": true,
      "metadata_details": {
        "prr": 0.0,
        "dx": null,
        "sw_version": "waiting for fiber",
        "fiber_description": "waiting for fiber",
        "number_of_channels": 2337,
        "fiber_start_meters": null,
        "fiber_length_meters": null
      }
    }
  }
}
```
