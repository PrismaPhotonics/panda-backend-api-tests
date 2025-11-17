"""
Script to fix potential serialization issues in test files.

This script:
1. Checks for invalid characters/encoding issues
2. Normalizes line endings
3. Ensures UTF-8 encoding
4. Removes any problematic characters
"""

import sys
import os
from pathlib import Path

def check_and_fix_file(file_path: str) -> bool:
    """
    Check and fix potential serialization issues in a file.
    
    Args:
        file_path: Path to the file to check/fix
        
    Returns:
        True if file was fixed, False if no issues found
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    print(f"📄 Checking file: {file_path}")
    print(f"   Size: {file_path.stat().st_size} bytes")
    
    # Read file with UTF-8 encoding
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    original_content = content
    issues_found = []
    
    # Check for problematic characters
    invalid_chars = []
    for i, char in enumerate(content):
        code = ord(char)
        # Check for control characters (except newline, tab, carriage return)
        if code < 32 and code not in (9, 10, 13):
            invalid_chars.append((i, code, char))
    
    if invalid_chars:
        issues_found.append(f"Found {len(invalid_chars)} invalid control characters")
        # Remove invalid characters
        content = ''.join(char for char in content if ord(char) >= 32 or ord(char) in (9, 10, 13))
    
    # Normalize line endings to LF (Unix style)
    if '\r\n' in content or '\r' in content:
        issues_found.append("Found Windows line endings (CRLF)")
        content = content.replace('\r\n', '\n').replace('\r', '\n')
    
    # Check for BOM
    if content.startswith('\ufeff'):
        issues_found.append("Found UTF-8 BOM")
        content = content.lstrip('\ufeff')
    
    # Check for trailing whitespace (can cause issues)
    lines = content.split('\n')
    trailing_ws_count = 0
    for i, line in enumerate(lines):
        if line.rstrip() != line:
            trailing_ws_count += 1
            lines[i] = line.rstrip()
    
    if trailing_ws_count > 0:
        issues_found.append(f"Found trailing whitespace in {trailing_ws_count} lines")
        content = '\n'.join(lines)
    
    # Check file size
    if len(content.encode('utf-8')) > 100000:  # > 100KB
        issues_found.append(f"File is large: {len(content.encode('utf-8'))} bytes")
    
    if issues_found:
        print(f"⚠️  Issues found:")
        for issue in issues_found:
            print(f"   - {issue}")
        
        # Create backup
        backup_path = file_path.with_suffix(file_path.suffix + '.backup')
        print(f"💾 Creating backup: {backup_path}")
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        
        # Write fixed content
        print(f"🔧 Fixing file...")
        with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        
        print(f"✅ File fixed successfully!")
        print(f"   Original size: {len(original_content.encode('utf-8'))} bytes")
        print(f"   Fixed size: {len(content.encode('utf-8'))} bytes")
        return True
    else:
        print(f"✅ No issues found - file is clean!")
        return False


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python fix_serialization_issue.py <file_path>")
        print("\nExample:")
        print("  python fix_serialization_issue.py tests/integration/api/test_config_validation_high_priority.py")
        sys.exit(1)
    
    file_path = sys.argv[1]
    fixed = check_and_fix_file(file_path)
    
    if fixed:
        print("\n✅ File has been fixed. Please try using Cursor again.")
    else:
        print("\n✅ File is clean. The serialization issue may be in Cursor itself.")
        print("   Try:")
        print("   1. Close and reopen Cursor")
        print("   2. Close the large file")
        print("   3. Restart Cursor")


if __name__ == '__main__':
    main()


