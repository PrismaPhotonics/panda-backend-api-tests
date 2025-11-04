"""
Load Testing Package
===================

בדיקות עומס וקיבולת למערכת Focus Server.

Test Categories:
- Baseline: ביצועי בסיס (job בודד)
- Linear: עומס הדרגתי (מציאת נקודת שבירה)
- Stress: בדיקת לחץ (דחיפת המערכת לגבול)
- Soak: עומס ממושך (זיהוי memory leaks)
- Recovery: התאוששות אחרי עומס

Usage:
    # Run all load tests
    pytest tests/load/ -v -m load

    # Run specific category
    pytest tests/load/ -v -m baseline
    pytest tests/load/ -v -m linear
    pytest tests/load/ -v -m stress

Author: QA Automation Team
Date: October 26, 2025
"""

__version__ = "1.0.0"
__all__ = [
    "test_job_capacity_limits",
]

