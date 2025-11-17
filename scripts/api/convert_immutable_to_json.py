"""
Convert Immutable.js structure from browser to plain JSON
"""
import json
from pathlib import Path

def convert_immutable_to_json(immutable_data):
    """
    Convert Immutable.js structure to plain Python dict/list.
    
    Args:
        immutable_data: Dictionary containing Immutable.js structure
        
    Returns:
        Plain Python dict/list structure
    """
    if isinstance(immutable_data, dict):
        # Check if it's an Immutable Map structure
        if '_map' in immutable_data and '_list' in immutable_data:
            result = {}
            # Extract entries from _list._tail.array
            if '_list' in immutable_data:
                list_data = immutable_data['_list']
                if '_tail' in list_data and 'array' in list_data['_tail']:
                    entries = list_data['_tail']['array']
                    for entry in entries:
                        if isinstance(entry, list) and len(entry) >= 2:
                            key = entry[0]
                            value = entry[1]
                            result[key] = convert_immutable_to_json(value)
            return result
        
        # Check if it's an Immutable List structure
        if '_tail' in immutable_data and 'array' in immutable_data['_tail']:
            arr = immutable_data['_tail']['array']
            return [convert_immutable_to_json(item) for item in arr]
        
        # Regular dict - convert recursively
        result = {}
        for key, value in immutable_data.items():
            if key.startswith('_') and key not in ['_tail', '_map', '_list']:
                continue  # Skip internal Immutable properties
            result[key] = convert_immutable_to_json(value)
        return result
    
    elif isinstance(immutable_data, list):
        return [convert_immutable_to_json(item) for item in immutable_data]
    
    else:
        return immutable_data


def main():
    """Main function to convert the saved Immutable structure."""
    # Read the saved file
    input_file = Path(r"c:\Users\roy.avrahami\.cursor\projects\c-Projects-focus-server-automation\agent-tools\566c27ac-53b3-416c-97c5-ad2f6751808d.txt")
    output_file = Path("docs/03_architecture/api/swagger_spec.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Reading from: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove the "### Result\n" prefix if present
    if content.startswith("### Result\n"):
        content = content[11:]
    
    # Try to find the first valid JSON object
    # Look for the first { and try to parse from there
    first_brace = content.find('{')
    if first_brace > 0:
        content = content[first_brace:]
    
    # Try to parse JSON incrementally
    # Find the matching closing brace
    brace_count = 0
    end_pos = 0
    for i, char in enumerate(content):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                end_pos = i + 1
                break
    
    if end_pos > 0:
        content = content[:end_pos]
    
    # Parse JSON
    try:
        # Use json.JSONDecoder for large files
        decoder = json.JSONDecoder()
        data, idx = decoder.raw_decode(content)
        print(f"Parsed JSON successfully")
        
        # Convert Immutable structure
        print("Converting Immutable structure to plain JSON...")
        plain_json = convert_immutable_to_json(data)
        
        # Save as JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(plain_json, f, indent=2, ensure_ascii=False)
        
        print(f"Saved to: {output_file}")
        
        # Print summary
        if isinstance(plain_json, dict):
            print(f"\nSummary:")
            print(f"  OpenAPI version: {plain_json.get('openapi', 'N/A')}")
            print(f"  Title: {plain_json.get('info', {}).get('title', 'N/A')}")
            print(f"  Version: {plain_json.get('info', {}).get('version', 'N/A')}")
            paths = plain_json.get('paths', {})
            print(f"  Endpoints: {len(paths)}")
            
            # Count methods
            method_count = 0
            for path, methods in paths.items():
                if isinstance(methods, dict):
                    method_count += len([m for m in methods.keys() if m in ['get', 'post', 'put', 'delete', 'patch']])
            print(f"  Total methods: {method_count}")
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print(f"First 500 chars: {content[:500]}")


if __name__ == "__main__":
    main()

