# Waiting for Fiber Investigation Report

**Date:** 2025-11-08 20:27:02

## Summary

- Error found in pz_core_libs: True
- Commits found: 2
- Error found in logs: True
- System waiting for fiber: True
- PRR value: 0.0

## Detailed Results

```json
{
  "timestamp": "2025-11-08T20:25:32.177363",
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
      "error_found_in_logs": true,
      "first_occurrence": {
        "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
        "line": "2025-11-08T18:13:28+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
      },
      "log_entries": [
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 2,
          "content": "2025-11-08T18:13:28+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 6,
          "content": "2025-11-08T18:13:31+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 10,
          "content": "2025-11-08T18:13:35+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 14,
          "content": "2025-11-08T18:13:38+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 18,
          "content": "2025-11-08T18:13:41+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 22,
          "content": "2025-11-08T18:13:44+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 26,
          "content": "2025-11-08T18:13:47+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 30,
          "content": "2025-11-08T18:13:51+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 34,
          "content": "2025-11-08T18:13:54+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 38,
          "content": "2025-11-08T18:13:57+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 42,
          "content": "2025-11-08T18:14:00+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 46,
          "content": "2025-11-08T18:14:04+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 50,
          "content": "2025-11-08T18:14:07+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 54,
          "content": "2025-11-08T18:14:10+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 58,
          "content": "2025-11-08T18:14:13+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 62,
          "content": "2025-11-08T18:14:17+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 66,
          "content": "2025-11-08T18:14:20+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 70,
          "content": "2025-11-08T18:14:23+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 74,
          "content": "2025-11-08T18:14:26+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 78,
          "content": "2025-11-08T18:14:30+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 82,
          "content": "2025-11-08T18:14:33+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 86,
          "content": "2025-11-08T18:14:36+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 90,
          "content": "2025-11-08T18:14:39+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 94,
          "content": "2025-11-08T18:14:43+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 98,
          "content": "2025-11-08T18:14:46+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 102,
          "content": "2025-11-08T18:14:49+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 106,
          "content": "2025-11-08T18:14:52+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 110,
          "content": "2025-11-08T18:14:55+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 114,
          "content": "2025-11-08T18:14:59+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 118,
          "content": "2025-11-08T18:15:02+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 122,
          "content": "2025-11-08T18:15:05+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 126,
          "content": "2025-11-08T18:15:08+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 130,
          "content": "2025-11-08T18:15:11+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 134,
          "content": "2025-11-08T18:15:14+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 138,
          "content": "2025-11-08T18:15:18+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 142,
          "content": "2025-11-08T18:15:21+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 146,
          "content": "2025-11-08T18:15:24+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 150,
          "content": "2025-11-08T18:15:27+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 154,
          "content": "2025-11-08T18:15:31+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 158,
          "content": "2025-11-08T18:15:34+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 162,
          "content": "2025-11-08T18:15:37+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 166,
          "content": "2025-11-08T18:15:40+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 170,
          "content": "2025-11-08T18:15:44+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 174,
          "content": "2025-11-08T18:15:47+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 178,
          "content": "2025-11-08T18:15:50+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 182,
          "content": "2025-11-08T18:15:53+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 186,
          "content": "2025-11-08T18:15:56+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 190,
          "content": "2025-11-08T18:16:00+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 194,
          "content": "2025-11-08T18:16:03+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 198,
          "content": "2025-11-08T18:16:06+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 202,
          "content": "2025-11-08T18:16:09+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 206,
          "content": "2025-11-08T18:16:13+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 210,
          "content": "2025-11-08T18:16:16+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 214,
          "content": "2025-11-08T18:16:19+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 218,
          "content": "2025-11-08T18:16:23+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 222,
          "content": "2025-11-08T18:16:26+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 226,
          "content": "2025-11-08T18:16:29+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 230,
          "content": "2025-11-08T18:16:32+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 234,
          "content": "2025-11-08T18:16:35+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 238,
          "content": "2025-11-08T18:16:38+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 242,
          "content": "2025-11-08T18:16:42+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 246,
          "content": "2025-11-08T18:16:45+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 250,
          "content": "2025-11-08T18:16:48+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 254,
          "content": "2025-11-08T18:16:52+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 258,
          "content": "2025-11-08T18:16:55+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 262,
          "content": "2025-11-08T18:16:58+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 266,
          "content": "2025-11-08T18:17:01+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 270,
          "content": "2025-11-08T18:17:04+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 274,
          "content": "2025-11-08T18:17:07+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 278,
          "content": "2025-11-08T18:17:11+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 282,
          "content": "2025-11-08T18:17:14+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 286,
          "content": "2025-11-08T18:17:18+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 290,
          "content": "2025-11-08T18:17:21+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 294,
          "content": "2025-11-08T18:17:24+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 298,
          "content": "2025-11-08T18:17:28+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 302,
          "content": "2025-11-08T18:17:31+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 306,
          "content": "2025-11-08T18:17:34+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 310,
          "content": "2025-11-08T18:17:38+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 314,
          "content": "2025-11-08T18:17:41+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 318,
          "content": "2025-11-08T18:17:44+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 322,
          "content": "2025-11-08T18:17:47+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 326,
          "content": "2025-11-08T18:17:50+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 330,
          "content": "2025-11-08T18:17:53+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 334,
          "content": "2025-11-08T18:17:57+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 338,
          "content": "2025-11-08T18:18:00+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 342,
          "content": "2025-11-08T18:18:03+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 346,
          "content": "2025-11-08T18:18:06+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 350,
          "content": "2025-11-08T18:18:10+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 354,
          "content": "2025-11-08T18:18:13+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 358,
          "content": "2025-11-08T18:18:17+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 362,
          "content": "2025-11-08T18:18:20+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 366,
          "content": "2025-11-08T18:18:23+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 370,
          "content": "2025-11-08T18:18:26+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 374,
          "content": "2025-11-08T18:18:30+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 378,
          "content": "2025-11-08T18:18:33+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 382,
          "content": "2025-11-08T18:18:36+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 386,
          "content": "2025-11-08T18:18:39+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 390,
          "content": "2025-11-08T18:18:43+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 394,
          "content": "2025-11-08T18:18:46+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 398,
          "content": "2025-11-08T18:18:50+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 402,
          "content": "2025-11-08T18:18:53+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 406,
          "content": "2025-11-08T18:18:56+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 410,
          "content": "2025-11-08T18:18:59+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 414,
          "content": "2025-11-08T18:19:02+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 418,
          "content": "2025-11-08T18:19:06+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 422,
          "content": "2025-11-08T18:19:09+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 426,
          "content": "2025-11-08T18:19:12+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 430,
          "content": "2025-11-08T18:19:15+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 434,
          "content": "2025-11-08T18:19:19+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 438,
          "content": "2025-11-08T18:19:22+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 442,
          "content": "2025-11-08T18:19:25+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 446,
          "content": "2025-11-08T18:19:28+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 450,
          "content": "2025-11-08T18:19:31+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 454,
          "content": "2025-11-08T18:19:34+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 458,
          "content": "2025-11-08T18:19:38+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 462,
          "content": "2025-11-08T18:19:41+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 466,
          "content": "2025-11-08T18:19:44+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 470,
          "content": "2025-11-08T18:19:47+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 474,
          "content": "2025-11-08T18:19:50+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 478,
          "content": "2025-11-08T18:19:54+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 482,
          "content": "2025-11-08T18:19:57+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 486,
          "content": "2025-11-08T18:20:00+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 490,
          "content": "2025-11-08T18:20:04+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 494,
          "content": "2025-11-08T18:20:07+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 498,
          "content": "2025-11-08T18:20:10+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 502,
          "content": "2025-11-08T18:20:13+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 506,
          "content": "2025-11-08T18:20:17+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 510,
          "content": "2025-11-08T18:20:20+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 514,
          "content": "2025-11-08T18:20:23+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 518,
          "content": "2025-11-08T18:20:27+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 522,
          "content": "2025-11-08T18:20:30+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 526,
          "content": "2025-11-08T18:20:33+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 530,
          "content": "2025-11-08T18:20:36+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 534,
          "content": "2025-11-08T18:20:40+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 538,
          "content": "2025-11-08T18:20:43+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 542,
          "content": "2025-11-08T18:20:46+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 546,
          "content": "2025-11-08T18:20:50+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 550,
          "content": "2025-11-08T18:20:53+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 554,
          "content": "2025-11-08T18:20:57+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 558,
          "content": "2025-11-08T18:21:00+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 562,
          "content": "2025-11-08T18:21:03+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 566,
          "content": "2025-11-08T18:21:06+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 570,
          "content": "2025-11-08T18:21:09+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 574,
          "content": "2025-11-08T18:21:13+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 578,
          "content": "2025-11-08T18:21:16+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 582,
          "content": "2025-11-08T18:21:20+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 586,
          "content": "2025-11-08T18:21:23+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 590,
          "content": "2025-11-08T18:21:26+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 594,
          "content": "2025-11-08T18:21:29+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 598,
          "content": "2025-11-08T18:21:33+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 602,
          "content": "2025-11-08T18:21:36+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 606,
          "content": "2025-11-08T18:21:39+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 610,
          "content": "2025-11-08T18:21:42+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 614,
          "content": "2025-11-08T18:21:45+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 618,
          "content": "2025-11-08T18:21:49+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 622,
          "content": "2025-11-08T18:21:52+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 626,
          "content": "2025-11-08T18:21:55+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 630,
          "content": "2025-11-08T18:21:59+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 634,
          "content": "2025-11-08T18:22:02+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 638,
          "content": "2025-11-08T18:22:05+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 642,
          "content": "2025-11-08T18:22:08+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 646,
          "content": "2025-11-08T18:22:12+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 650,
          "content": "2025-11-08T18:22:15+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 654,
          "content": "2025-11-08T18:22:18+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 658,
          "content": "2025-11-08T18:22:22+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 662,
          "content": "2025-11-08T18:22:25+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 666,
          "content": "2025-11-08T18:22:28+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 670,
          "content": "2025-11-08T18:22:31+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 674,
          "content": "2025-11-08T18:22:34+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 678,
          "content": "2025-11-08T18:22:38+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 682,
          "content": "2025-11-08T18:22:41+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 686,
          "content": "2025-11-08T18:22:44+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 690,
          "content": "2025-11-08T18:22:47+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 694,
          "content": "2025-11-08T18:22:50+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 698,
          "content": "2025-11-08T18:22:54+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 702,
          "content": "2025-11-08T18:22:57+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 706,
          "content": "2025-11-08T18:23:01+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 710,
          "content": "2025-11-08T18:23:04+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 714,
          "content": "2025-11-08T18:23:07+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 718,
          "content": "2025-11-08T18:23:10+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 722,
          "content": "2025-11-08T18:23:14+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 726,
          "content": "2025-11-08T18:23:17+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 730,
          "content": "2025-11-08T18:23:20+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 734,
          "content": "2025-11-08T18:23:23+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 738,
          "content": "2025-11-08T18:23:26+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 742,
          "content": "2025-11-08T18:23:30+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 746,
          "content": "2025-11-08T18:23:33+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 750,
          "content": "2025-11-08T18:23:36+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 754,
          "content": "2025-11-08T18:23:39+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 758,
          "content": "2025-11-08T18:23:43+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 762,
          "content": "2025-11-08T18:23:46+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 766,
          "content": "2025-11-08T18:23:49+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 770,
          "content": "2025-11-08T18:23:52+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 774,
          "content": "2025-11-08T18:23:56+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 778,
          "content": "2025-11-08T18:23:59+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 782,
          "content": "2025-11-08T18:24:02+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 786,
          "content": "2025-11-08T18:24:06+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 790,
          "content": "2025-11-08T18:24:09+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 794,
          "content": "2025-11-08T18:24:13+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 798,
          "content": "2025-11-08T18:24:16+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 802,
          "content": "2025-11-08T18:24:19+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 806,
          "content": "2025-11-08T18:24:22+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 810,
          "content": "2025-11-08T18:24:26+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 814,
          "content": "2025-11-08T18:24:29+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 818,
          "content": "2025-11-08T18:24:33+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 822,
          "content": "2025-11-08T18:24:36+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 826,
          "content": "2025-11-08T18:24:39+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 830,
          "content": "2025-11-08T18:24:42+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 834,
          "content": "2025-11-08T18:24:46+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 838,
          "content": "2025-11-08T18:24:49+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 842,
          "content": "2025-11-08T18:24:53+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 846,
          "content": "2025-11-08T18:24:56+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 850,
          "content": "2025-11-08T18:24:59+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 854,
          "content": "2025-11-08T18:25:02+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 858,
          "content": "2025-11-08T18:25:06+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 862,
          "content": "2025-11-08T18:25:09+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 866,
          "content": "2025-11-08T18:25:12+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 870,
          "content": "2025-11-08T18:25:15+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 874,
          "content": "2025-11-08T18:25:18+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 879,
          "content": "2025-11-08T18:25:21+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 883,
          "content": "2025-11-08T18:25:25+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 887,
          "content": "2025-11-08T18:25:28+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 891,
          "content": "2025-11-08T18:25:32+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 895,
          "content": "2025-11-08T18:25:35+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 899,
          "content": "2025-11-08T18:25:39+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 903,
          "content": "2025-11-08T18:25:42+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 907,
          "content": "2025-11-08T18:25:45+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 911,
          "content": "2025-11-08T18:25:49+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 915,
          "content": "2025-11-08T18:25:52+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 919,
          "content": "2025-11-08T18:25:55+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 923,
          "content": "2025-11-08T18:25:59+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 927,
          "content": "2025-11-08T18:26:02+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 931,
          "content": "2025-11-08T18:26:05+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 935,
          "content": "2025-11-08T18:26:08+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 939,
          "content": "2025-11-08T18:26:12+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 943,
          "content": "2025-11-08T18:26:15+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 947,
          "content": "2025-11-08T18:26:18+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 951,
          "content": "2025-11-08T18:26:22+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 955,
          "content": "2025-11-08T18:26:25+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 959,
          "content": "2025-11-08T18:26:29+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 963,
          "content": "2025-11-08T18:26:32+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 967,
          "content": "2025-11-08T18:26:35+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 971,
          "content": "2025-11-08T18:26:38+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 975,
          "content": "2025-11-08T18:26:41+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 979,
          "content": "2025-11-08T18:26:45+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 983,
          "content": "2025-11-08T18:26:48+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 987,
          "content": "2025-11-08T18:26:51+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 991,
          "content": "2025-11-08T18:26:54+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 995,
          "content": "2025-11-08T18:26:58+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        },
        {
          "pod": "panda-panda-focus-server-78dbcfd9d9-kjj77",
          "line_number": 999,
          "content": "2025-11-08T18:27:01+0000 ERROR pz.focus_server Cannot configure job - validation failed: Cannot proceed: Missing required fiber metadata fields: prr"
        }
      ]
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
