"""
Convert Markdown to Confluence Wiki Markup
==========================================

Converts Markdown document to Confluence Wiki Markup format
that can be copy-pasted directly into Confluence.

Author: QA Automation Architect
Date: 2025-11-05
"""

import sys
import os
import re
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure UTF-8 for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')


def markdown_to_confluence_wiki(markdown_content: str) -> str:
    """
    Convert Markdown to Confluence Wiki Markup.
    
    Args:
        markdown_content: Markdown content string
    
    Returns:
        Confluence Wiki Markup string
    """
    content = markdown_content
    
    # Remove emojis (keep only text)
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE
    )
    content = emoji_pattern.sub('', content)
    
    # Headers
    content = re.sub(r'^# (.+)$', r'h1. \1', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.+)$', r'h2. \1', content, flags=re.MULTILINE)
    content = re.sub(r'^### (.+)$', r'h3. \1', content, flags=re.MULTILINE)
    content = re.sub(r'^#### (.+)$', r'h4. \1', content, flags=re.MULTILINE)
    content = re.sub(r'^##### (.+)$', r'h5. \1', content, flags=re.MULTILINE)
    
    # Bold - Markdown uses **text** or __text__, Confluence uses *text*
    content = re.sub(r'\*\*(.+?)\*\*', r'*\1*', content)
    content = re.sub(r'__(.+?)__', r'*\1*', content)
    
    # Italic - Markdown uses *text* or _text_, Confluence uses _text_
    # Need to be careful not to conflict with bold
    # Convert italic markers that are not part of bold
    content = re.sub(r'(?<!\*)\*(?!\*)([^*]+?)(?<!\*)\*(?!\*)', r'_\1_', content)
    
    # Code blocks - Markdown: ```language\ncode\n```, Confluence: {code:language}\ncode\n{code}
    content = re.sub(r'```(\w+)?\n(.*?)```', lambda m: f'{{code:{m.group(1) or ""}}}\n{m.group(2)}\n{{code}}', content, flags=re.DOTALL)
    
    # Inline code - Markdown: `code`, Confluence: {{code}}
    content = re.sub(r'`([^`]+)`', r'{{\1}}', content)
    
    # Links - Markdown: [text](url), Confluence: [text|url]
    content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'[\1|\2]', content)
    
    # Unordered lists - Markdown: - item, Confluence: * item
    lines = content.split('\n')
    result_lines = []
    in_code_block = False
    
    for line in lines:
        # Track code blocks
        if '{code' in line:
            in_code_block = True
        if '{code}' in line and in_code_block:
            in_code_block = False
        
        if not in_code_block:
            # Unordered lists
            if re.match(r'^[-*]\s+(.+)$', line):
                line = re.sub(r'^[-*]\s+(.+)$', r'* \1', line)
            # Ordered lists
            elif re.match(r'^\d+\.\s+(.+)$', line):
                line = re.sub(r'^\d+\.\s+(.+)$', r'# \1', line)
        
        result_lines.append(line)
    
    content = '\n'.join(result_lines)
    
    # Tables - Markdown tables use | separator, Confluence uses | | |
    # Keep table format as-is (Confluence accepts similar format)
    lines = content.split('\n')
    result_lines = []
    in_table = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('|') and stripped.endswith('|'):
            # Table row
            if not in_table:
                in_table = True
            # Confluence tables use | | | format
            # Remove first and last | if present, then add spaces
            cells = [cell.strip() for cell in stripped.split('|') if cell.strip() and cell.strip() != '-']
            if cells and not all(c.replace('-', '').replace(':', '').strip() == '' for c in cells):
                # Format as Confluence table
                result_lines.append('| ' + ' | '.join(cells) + ' |')
            else:
                # Skip separator rows
                continue
        else:
            if in_table:
                in_table = False
            result_lines.append(line)
    
    content = '\n'.join(result_lines)
    
    # Horizontal rules - Markdown: ---, Confluence: ----
    content = re.sub(r'^---$', r'----', content, flags=re.MULTILINE)
    
    # Blockquotes - Markdown: > text, Confluence: {quote}text{quote}
    content = re.sub(r'^>\s+(.+)$', r'{quote}\1{quote}', content, flags=re.MULTILINE)
    
    # Clean up multiple empty lines
    content = re.sub(r'\n{3,}', r'\n\n', content)
    
    return content


def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Convert Markdown to Confluence Wiki Markup'
    )
    parser.add_argument(
        'input_file',
        type=Path,
        help='Input Markdown file'
    )
    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output file (default: input_file.confluence)'
    )
    
    args = parser.parse_args()
    
    if not args.input_file.exists():
        print(f"Error: File not found: {args.input_file}")
        return 1
    
    # Read Markdown file
    with open(args.input_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Convert to Confluence Wiki Markup
    confluence_content = markdown_to_confluence_wiki(markdown_content)
    
    # Write output
    if args.output:
        output_file = args.output
    else:
        output_file = args.input_file.with_suffix('.confluence')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(confluence_content)
    
    print(f"✅ Converted Markdown to Confluence Wiki Markup")
    print(f"   Input:  {args.input_file}")
    print(f"   Output: {output_file}")
    print(f"\n📋 To use in Confluence:")
    print(f"   1. Open Confluence page in edit mode")
    print(f"   2. Click '...' → Insert → Markup → Confluence Wiki")
    print(f"   3. Copy content from {output_file}")
    print(f"   4. Paste into markup editor and click Insert")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

