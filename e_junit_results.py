[1mdiff --git a/parse_junit_results.py b/parse_junit_results.py[m
[1mindex 0ebe5d8..5626c56 100644[m
[1m--- a/parse_junit_results.py[m
[1m+++ b/parse_junit_results.py[m
[36m@@ -13,6 +13,22 @@[m [mfrom datetime import datetime[m
 from collections import OrderedDict[m
 [m
 [m
[32m+[m[32mdef safe_print(message: str):[m
[32m+[m[32m    """[m
[32m+[m[32m    Print message to stdout with fallback for encoding issues.[m
[32m+[m[32m    On Windows with cp1255 (Hebrew) encoding, emojis cause UnicodeEncodeError.[m
[32m+[m[32m    This function handles that gracefully by stripping problematic characters.[m
[32m+[m[32m    """[m
[32m+[m[32m    try:[m
[32m+[m[32m        print(message)[m
[32m+[m[32m    except UnicodeEncodeError:[m
[32m+[m[32m        # Remove emojis and other non-ASCII characters for console output[m
[32m+[m[32m        safe_message = message.encode('ascii', 'ignore').decode('ascii')[m
[32m+[m[32m        # Replace common emoji patterns with text equivalents[m
[32m+[m[32m        safe_message = safe_message.replace('', '[PASS]').replace('', '[FAIL]')[m
[32m+[m[32m        print(safe_message if safe_message.strip() else message.encode('ascii', 'replace').decode('ascii'))[m
[32m+[m
[32m+[m
 def get_test_category(classname: str) -> str:[m
     """Categorize test by its module/class name."""[m
     if 'integration' in classname.lower():[m
[36m@@ -424,13 +440,13 @@[m [mdef write_summary(total_tests, total_failures, total_errors, total_skipped, tota[m
     print("=" * 60)[m
     [m
     if failed_tests or error_tests:[m
[31m-        print("\n❌ FAILED TESTS:")[m
[32m+[m[32m        safe_print("\n[FAIL] FAILED TESTS:")[m
         for test in (failed_tests + error_tests)[:10]:[m
             print(f"  - {test['short_name']} ({test['status']})")[m
         if len(failed_tests) + len(error_tests) > 10:[m
             print(f"  ... and {len(failed_tests) + len(error_tests) - 10} more")[m
     else:[m
[31m-        print("\n✅ All tests passed!")[m
[32m+[m[32m        safe_print("\n[OK] All tests passed!")[m
     print()[m
 [m
 [m
